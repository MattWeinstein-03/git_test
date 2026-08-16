import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const DB_PATH = join(__dirname, '..', 'products.db');

let db;

export function getDb() {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    db.pragma('foreign_keys = ON');
    initSchema();
  }
  return db;
}

function initSchema() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      upc TEXT UNIQUE NOT NULL,
      title TEXT,
      description TEXT,
      brand TEXT,
      category TEXT,
      images TEXT,          -- JSON array of image URLs
      weight TEXT,
      dimensions TEXT,
      ingredients TEXT,
      nutrition_facts TEXT, -- JSON object
      source TEXT,          -- which API provided this data
      raw_data TEXT,        -- full JSON response for reference
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_products_upc ON products(upc);
    CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
    CREATE INDEX IF NOT EXISTS idx_products_title ON products(title);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

    CREATE TABLE IF NOT EXISTS scan_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      upc TEXT NOT NULL,
      product_id INTEGER,
      scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE INDEX IF NOT EXISTS idx_scan_history_upc ON scan_history(upc);
    CREATE INDEX IF NOT EXISTS idx_scan_history_date ON scan_history(scanned_at);
  `);
}

// ─── Product CRUD ─────────────────────────────────────────────────────────────

export function findProductByUpc(upc) {
  const db = getDb();
  return db.prepare('SELECT * FROM products WHERE upc = ?').get(upc);
}

export function insertProduct(product) {
  const db = getDb();
  const stmt = db.prepare(`
    INSERT INTO products (upc, title, description, brand, category, images, weight, dimensions, ingredients, nutrition_facts, source, raw_data)
    VALUES (@upc, @title, @description, @brand, @category, @images, @weight, @dimensions, @ingredients, @nutrition_facts, @source, @raw_data)
  `);
  const result = stmt.run({
    upc: product.upc,
    title: product.title || null,
    description: product.description || null,
    brand: product.brand || null,
    category: product.category || null,
    images: product.images ? JSON.stringify(product.images) : null,
    weight: product.weight || null,
    dimensions: product.dimensions || null,
    ingredients: product.ingredients || null,
    nutrition_facts: product.nutrition_facts ? JSON.stringify(product.nutrition_facts) : null,
    source: product.source || null,
    raw_data: product.raw_data ? JSON.stringify(product.raw_data) : null,
  });
  return result.lastInsertRowid;
}

export function updateProduct(upc, product) {
  const db = getDb();
  const stmt = db.prepare(`
    UPDATE products SET
      title = @title,
      description = @description,
      brand = @brand,
      category = @category,
      images = @images,
      weight = @weight,
      dimensions = @dimensions,
      ingredients = @ingredients,
      nutrition_facts = @nutrition_facts,
      source = @source,
      raw_data = @raw_data,
      updated_at = CURRENT_TIMESTAMP
    WHERE upc = @upc
  `);
  return stmt.run({
    upc,
    title: product.title || null,
    description: product.description || null,
    brand: product.brand || null,
    category: product.category || null,
    images: product.images ? JSON.stringify(product.images) : null,
    weight: product.weight || null,
    dimensions: product.dimensions || null,
    ingredients: product.ingredients || null,
    nutrition_facts: product.nutrition_facts ? JSON.stringify(product.nutrition_facts) : null,
    source: product.source || null,
    raw_data: product.raw_data ? JSON.stringify(product.raw_data) : null,
  });
}

export function getAllProducts({ limit = 100, offset = 0, search = '' } = {}) {
  const db = getDb();
  if (search) {
    return db.prepare(`
      SELECT * FROM products
      WHERE title LIKE @search OR brand LIKE @search OR upc LIKE @search OR category LIKE @search
      ORDER BY updated_at DESC
      LIMIT @limit OFFSET @offset
    `).all({ search: `%${search}%`, limit, offset });
  }
  return db.prepare('SELECT * FROM products ORDER BY updated_at DESC LIMIT ? OFFSET ?').all(limit, offset);
}

export function getProductCount(search = '') {
  const db = getDb();
  if (search) {
    return db.prepare(`
      SELECT COUNT(*) as count FROM products
      WHERE title LIKE @search OR brand LIKE @search OR upc LIKE @search OR category LIKE @search
    `).get({ search: `%${search}%` }).count;
  }
  return db.prepare('SELECT COUNT(*) as count FROM products').get().count;
}

export function deleteProduct(upc) {
  const db = getDb();
  return db.prepare('DELETE FROM products WHERE upc = ?').run(upc);
}

// ─── Scan History ─────────────────────────────────────────────────────────────

export function recordScan(upc, productId) {
  const db = getDb();
  return db.prepare('INSERT INTO scan_history (upc, product_id) VALUES (?, ?)').run(upc, productId || null);
}

export function getRecentScans(limit = 50) {
  const db = getDb();
  return db.prepare(`
    SELECT sh.*, p.title, p.brand, p.images
    FROM scan_history sh
    LEFT JOIN products p ON sh.product_id = p.id
    ORDER BY sh.scanned_at DESC
    LIMIT ?
  `).all(limit);
}

export function getStats() {
  const db = getDb();
  const totalProducts = db.prepare('SELECT COUNT(*) as count FROM products').get().count;
  const totalScans = db.prepare('SELECT COUNT(*) as count FROM scan_history').get().count;
  const topBrands = db.prepare(`
    SELECT brand, COUNT(*) as count FROM products
    WHERE brand IS NOT NULL AND brand != ''
    GROUP BY brand ORDER BY count DESC LIMIT 10
  `).all();
  const recentlyAdded = db.prepare('SELECT upc, title, brand, created_at FROM products ORDER BY created_at DESC LIMIT 5').all();
  return { totalProducts, totalScans, topBrands, recentlyAdded };
}
