import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import {
  getDb,
  findProductByUpc,
  insertProduct,
  updateProduct,
  getAllProducts,
  getProductCount,
  deleteProduct,
  recordScan,
  getRecentScans,
  getStats,
} from './database.js';
import { lookupUPC, bulkLookup } from './api-lookup.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(join(__dirname, '..', 'public')));

// Initialize database on startup
getDb();
console.log('✅ Database initialized');

// ─── API Routes ───────────────────────────────────────────────────────────────

/**
 * POST /api/scan
 * Main endpoint - scan a UPC barcode.
 * Checks local DB first, if not found queries external APIs and saves.
 */
app.post('/api/scan', async (req, res) => {
  try {
    const { upc } = req.body;
    if (!upc) {
      return res.status(400).json({ error: 'UPC code is required' });
    }

    const cleanUpc = upc.replace(/[\s\-]/g, '');
    console.log(`\n📦 Scan request for UPC: ${cleanUpc}`);

    // Check local database first
    let product = findProductByUpc(cleanUpc);
    let fromCache = true;

    if (product) {
      console.log(`  ↪ Found in local DB: ${product.title}`);
      // Parse JSON fields for response
      product = parseProductJsonFields(product);
    } else {
      console.log(`  ↪ Not in local DB, querying APIs...`);
      fromCache = false;

      // Lookup from external APIs
      const lookupResult = await lookupUPC(cleanUpc);

      if (lookupResult) {
        // Save to database
        const id = insertProduct(lookupResult);
        product = { id, ...lookupResult };
        console.log(`  ✅ Saved to DB: ${product.title}`);
      } else {
        // Record the scan attempt even if not found
        recordScan(cleanUpc, null);
        return res.json({
          found: false,
          upc: cleanUpc,
          message: 'Product not found in any database. You can add it manually.',
        });
      }
    }

    // Record the scan
    recordScan(cleanUpc, product.id);

    res.json({
      found: true,
      fromCache,
      product,
    });
  } catch (err) {
    console.error('Scan error:', err);
    res.status(500).json({ error: 'Internal server error', details: err.message });
  }
});

/**
 * POST /api/bulk-scan
 * Bulk lookup - accepts an array of UPCs.
 */
app.post('/api/bulk-scan', async (req, res) => {
  try {
    const { upcs } = req.body;
    if (!upcs || !Array.isArray(upcs)) {
      return res.status(400).json({ error: 'Array of UPC codes is required' });
    }

    if (upcs.length > 50) {
      return res.status(400).json({ error: 'Maximum 50 UPCs per bulk request' });
    }

    console.log(`\n📦 Bulk scan request for ${upcs.length} UPCs`);

    const results = [];
    for (const upc of upcs) {
      const cleanUpc = upc.replace(/[\s\-]/g, '');

      // Check local DB first
      let product = findProductByUpc(cleanUpc);
      if (product) {
        product = parseProductJsonFields(product);
        recordScan(cleanUpc, product.id);
        results.push({ upc: cleanUpc, found: true, fromCache: true, product });
        continue;
      }

      // Lookup externally
      const lookupResult = await lookupUPC(cleanUpc);
      if (lookupResult) {
        const id = insertProduct(lookupResult);
        product = { id, ...lookupResult };
        recordScan(cleanUpc, id);
        results.push({ upc: cleanUpc, found: true, fromCache: false, product });
      } else {
        recordScan(cleanUpc, null);
        results.push({ upc: cleanUpc, found: false, product: null });
      }

      // Rate limit between external lookups
      await new Promise(resolve => setTimeout(resolve, 1200));
    }

    res.json({
      total: upcs.length,
      found: results.filter(r => r.found).length,
      notFound: results.filter(r => !r.found).length,
      results,
    });
  } catch (err) {
    console.error('Bulk scan error:', err);
    res.status(500).json({ error: 'Internal server error', details: err.message });
  }
});

/**
 * GET /api/products
 * List all products in the database with search/pagination.
 */
app.get('/api/products', (req, res) => {
  try {
    const { limit = 50, offset = 0, search = '' } = req.query;
    const products = getAllProducts({
      limit: parseInt(limit),
      offset: parseInt(offset),
      search,
    }).map(parseProductJsonFields);

    const total = getProductCount(search);

    res.json({ products, total, limit: parseInt(limit), offset: parseInt(offset) });
  } catch (err) {
    console.error('List products error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/products/:upc
 * Get a single product by UPC.
 */
app.get('/api/products/:upc', (req, res) => {
  try {
    const product = findProductByUpc(req.params.upc);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.json(parseProductJsonFields(product));
  } catch (err) {
    console.error('Get product error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * PUT /api/products/:upc
 * Manually update/add product data.
 */
app.put('/api/products/:upc', (req, res) => {
  try {
    const { upc } = req.params;
    const existing = findProductByUpc(upc);

    if (existing) {
      updateProduct(upc, { ...req.body, source: req.body.source || 'manual' });
      const updated = findProductByUpc(upc);
      res.json({ message: 'Product updated', product: parseProductJsonFields(updated) });
    } else {
      const id = insertProduct({ upc, ...req.body, source: req.body.source || 'manual' });
      const product = findProductByUpc(upc);
      res.json({ message: 'Product created', product: parseProductJsonFields(product) });
    }
  } catch (err) {
    console.error('Update product error:', err);
    res.status(500).json({ error: 'Internal server error', details: err.message });
  }
});

/**
 * DELETE /api/products/:upc
 * Remove a product from the database.
 */
app.delete('/api/products/:upc', (req, res) => {
  try {
    const result = deleteProduct(req.params.upc);
    if (result.changes === 0) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.json({ message: 'Product deleted' });
  } catch (err) {
    console.error('Delete product error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/history
 * Recent scan history.
 */
app.get('/api/history', (req, res) => {
  try {
    const { limit = 50 } = req.query;
    const history = getRecentScans(parseInt(limit));
    res.json(history);
  } catch (err) {
    console.error('History error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/stats
 * Dashboard statistics.
 */
app.get('/api/stats', (req, res) => {
  try {
    res.json(getStats());
  } catch (err) {
    console.error('Stats error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * POST /api/export
 * Export all products as JSON.
 */
app.post('/api/export', (req, res) => {
  try {
    const products = getAllProducts({ limit: 999999 }).map(parseProductJsonFields);
    res.setHeader('Content-Disposition', 'attachment; filename=upc-products-export.json');
    res.json(products);
  } catch (err) {
    console.error('Export error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * POST /api/import
 * Import products from JSON array.
 */
app.post('/api/import', (req, res) => {
  try {
    const { products } = req.body;
    if (!products || !Array.isArray(products)) {
      return res.status(400).json({ error: 'Array of products is required' });
    }

    let imported = 0;
    let skipped = 0;
    let errors = 0;

    for (const product of products) {
      if (!product.upc) {
        errors++;
        continue;
      }
      const existing = findProductByUpc(product.upc);
      if (existing) {
        skipped++;
        continue;
      }
      try {
        insertProduct({ ...product, source: product.source || 'import' });
        imported++;
      } catch (e) {
        errors++;
      }
    }

    res.json({ message: 'Import complete', imported, skipped, errors });
  } catch (err) {
    console.error('Import error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function parseProductJsonFields(product) {
  if (!product) return product;
  return {
    ...product,
    images: safeJsonParse(product.images, []),
    nutrition_facts: safeJsonParse(product.nutrition_facts, null),
    raw_data: safeJsonParse(product.raw_data, null),
  };
}

function safeJsonParse(str, fallback) {
  if (!str) return fallback;
  if (typeof str !== 'string') return str;
  try {
    return JSON.parse(str);
  } catch {
    return fallback;
  }
}

// ─── Start Server ─────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`\n🚀 UPC Product Database running at http://localhost:${PORT}`);
  console.log(`📖 API docs: http://localhost:${PORT}/api`);
  console.log(`📷 Scanner: http://localhost:${PORT}\n`);
});
