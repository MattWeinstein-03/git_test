// ─── UPC Product Database - Frontend Application ──────────────────────────────

const API_BASE = '';  // Same origin

// ─── State ────────────────────────────────────────────────────────────────────
let currentTab = 'scanner';
let cameraRunning = false;
let dbPage = 0;
const DB_PAGE_SIZE = 24;

// ─── Tab Navigation ───────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.tab;
    switchTab(target);
  });
});

function switchTab(tabName) {
  currentTab = tabName;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
  document.getElementById(`tab-${tabName}`).classList.add('active');

  if (tabName === 'database') loadProducts();
  if (tabName === 'stats') loadStats();
  if (tabName === 'scanner') loadRecentScans();
}

// ─── Scanner Tab ──────────────────────────────────────────────────────────────

const upcInput = document.getElementById('upc-input');
const lookupBtn = document.getElementById('lookup-btn');
const startCameraBtn = document.getElementById('start-camera-btn');
const stopCameraBtn = document.getElementById('stop-camera-btn');

// Lookup on button click or Enter
lookupBtn.addEventListener('click', () => doLookup(upcInput.value.trim()));
upcInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') doLookup(upcInput.value.trim());
});

async function doLookup(upc) {
  if (!upc) return;

  hideAllResults();
  showLoading(true);

  try {
    const response = await fetch(`${API_BASE}/api/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ upc }),
    });

    const data = await response.json();
    showLoading(false);

    if (data.found) {
      displayProduct(data.product, data.fromCache);
    } else {
      displayNotFound(upc);
    }

    loadRecentScans();
  } catch (err) {
    showLoading(false);
    alert('Error looking up product: ' + err.message);
  }
}

function displayProduct(product, fromCache) {
  const el = document.getElementById('scan-result');
  el.style.display = 'block';

  document.getElementById('result-title').textContent = product.title || 'Unknown Product';
  document.getElementById('result-upc').textContent = product.upc;
  document.getElementById('result-brand').textContent = product.brand || '—';
  document.getElementById('result-category').textContent = product.category || '—';
  document.getElementById('result-description').textContent = product.description || '—';
  document.getElementById('result-weight').textContent = product.weight || '—';

  // Source badge
  const badge = document.getElementById('result-source');
  badge.textContent = fromCache ? '📁 From DB' : `🌐 ${product.source}`;
  badge.className = `badge ${fromCache ? 'badge-cache' : 'badge-api'}`;

  // Cache status
  document.getElementById('result-cache-status').textContent = fromCache
    ? '✅ Loaded from local database (instant)'
    : '🌐 Fetched from API and saved to local database';

  // Images
  const imagesEl = document.getElementById('result-images');
  imagesEl.innerHTML = '';
  const images = product.images || [];
  if (images.length > 0) {
    const img = document.createElement('img');
    img.src = images[0];
    img.alt = product.title || 'Product image';
    img.onerror = () => { img.style.display = 'none'; };
    imagesEl.appendChild(img);
  }

  // Ingredients
  const ingredientsRow = document.getElementById('result-ingredients-row');
  const ingredientsEl = document.getElementById('result-ingredients');
  if (product.ingredients) {
    ingredientsRow.style.display = '';
    ingredientsEl.textContent = product.ingredients;
  } else {
    ingredientsRow.style.display = 'none';
  }

  // Nutrition
  const nutritionPanel = document.getElementById('result-nutrition');
  const nutritionContent = document.getElementById('nutrition-content');
  if (product.nutrition_facts && Object.keys(product.nutrition_facts).length > 0) {
    nutritionPanel.style.display = 'block';
    const nf = product.nutrition_facts;
    const items = [
      { label: 'Energy', value: nf.energy_kcal, unit: 'kcal' },
      { label: 'Fat', value: nf.fat, unit: 'g' },
      { label: 'Sat. Fat', value: nf.saturated_fat, unit: 'g' },
      { label: 'Carbs', value: nf.carbohydrates, unit: 'g' },
      { label: 'Sugars', value: nf.sugars, unit: 'g' },
      { label: 'Fiber', value: nf.fiber, unit: 'g' },
      { label: 'Protein', value: nf.proteins, unit: 'g' },
      { label: 'Salt', value: nf.salt, unit: 'g' },
    ].filter(i => i.value != null);

    nutritionContent.innerHTML = `<div class="nutrition-grid">
      ${items.map(i => `<div class="nutrition-item"><span class="n-label">${i.label}:</span> <span class="n-value">${i.value}${i.unit}</span></div>`).join('')}
    </div>`;
  } else {
    nutritionPanel.style.display = 'none';
  }
}

function displayNotFound(upc) {
  document.getElementById('not-found').style.display = 'block';
  document.getElementById('nf-upc').textContent = upc;
  document.getElementById('manual-upc').value = upc;
}

// Manual add form
document.getElementById('manual-add-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const upc = document.getElementById('manual-upc').value;
  const product = {
    title: document.getElementById('manual-title').value,
    brand: document.getElementById('manual-brand').value,
    category: document.getElementById('manual-category').value,
    description: document.getElementById('manual-description').value,
    weight: document.getElementById('manual-weight').value,
    images: document.getElementById('manual-image').value
      ? [document.getElementById('manual-image').value]
      : [],
  };

  try {
    const response = await fetch(`${API_BASE}/api/products/${upc}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product),
    });
    const data = await response.json();
    hideAllResults();
    displayProduct(data.product, true);
  } catch (err) {
    alert('Error saving product: ' + err.message);
  }
});

// ─── Camera Scanner ───────────────────────────────────────────────────────────

startCameraBtn.addEventListener('click', startCamera);
stopCameraBtn.addEventListener('click', stopCamera);

function startCamera() {
  const container = document.getElementById('camera-container');
  container.style.display = 'block';
  startCameraBtn.style.display = 'none';
  stopCameraBtn.style.display = 'inline-block';

  Quagga.init({
    inputStream: {
      name: 'Live',
      type: 'LiveStream',
      target: document.querySelector('#interactive'),
      constraints: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    },
    decoder: {
      readers: [
        'ean_reader',
        'ean_8_reader',
        'upc_reader',
        'upc_e_reader',
        'code_128_reader',
        'code_39_reader',
      ],
    },
    locate: true,
    frequency: 10,
  }, (err) => {
    if (err) {
      console.error('Quagga init error:', err);
      alert('Could not access camera. Make sure you allow camera access.');
      stopCamera();
      return;
    }
    Quagga.start();
    cameraRunning = true;
  });

  // Debounce detections
  let lastDetected = '';
  let lastDetectedTime = 0;

  Quagga.onDetected((result) => {
    const code = result.codeResult.code;
    const now = Date.now();

    // Ignore duplicate scans within 3 seconds
    if (code === lastDetected && now - lastDetectedTime < 3000) return;

    lastDetected = code;
    lastDetectedTime = now;

    // Visual feedback
    upcInput.value = code;
    stopCamera();
    doLookup(code);
  });
}

function stopCamera() {
  if (cameraRunning) {
    Quagga.stop();
    cameraRunning = false;
  }
  document.getElementById('camera-container').style.display = 'none';
  startCameraBtn.style.display = 'inline-block';
  stopCameraBtn.style.display = 'none';
}

// ─── Recent Scans ─────────────────────────────────────────────────────────────

async function loadRecentScans() {
  try {
    const response = await fetch(`${API_BASE}/api/history?limit=10`);
    const scans = await response.json();
    const container = document.getElementById('recent-scans-list');

    if (scans.length === 0) {
      container.innerHTML = '<p style="color: var(--gray-500);">No scans yet. Start scanning!</p>';
      return;
    }

    container.innerHTML = scans.map(scan => {
      const images = safeJsonParse(scan.images, []);
      const thumb = images.length > 0 ? images[0] : '';
      return `
        <div class="scan-item" onclick="doLookup('${scan.upc}')">
          ${thumb ? `<img class="scan-item-thumb" src="${thumb}" onerror="this.style.display='none'">` : '<div class="scan-item-thumb" style="display:flex;align-items:center;justify-content:center;font-size:1.2rem">📦</div>'}
          <div class="scan-item-info">
            <div class="scan-item-title">${scan.title || 'Unknown'}</div>
            <div class="scan-item-upc">${scan.upc}${scan.brand ? ' • ' + scan.brand : ''}</div>
          </div>
          <div class="scan-item-time">${formatTime(scan.scanned_at)}</div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading recent scans:', err);
  }
}

// ─── Database Tab ─────────────────────────────────────────────────────────────

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const exportBtn = document.getElementById('export-btn');

searchBtn.addEventListener('click', () => { dbPage = 0; loadProducts(); });
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') { dbPage = 0; loadProducts(); }
});
exportBtn.addEventListener('click', exportProducts);

async function loadProducts() {
  try {
    const search = searchInput.value.trim();
    const offset = dbPage * DB_PAGE_SIZE;
    const response = await fetch(`${API_BASE}/api/products?limit=${DB_PAGE_SIZE}&offset=${offset}&search=${encodeURIComponent(search)}`);
    const data = await response.json();

    document.getElementById('product-count').textContent = `${data.total} product${data.total !== 1 ? 's' : ''}`;

    const grid = document.getElementById('products-grid');
    if (data.products.length === 0) {
      grid.innerHTML = '<p style="text-align:center;color:var(--gray-500);padding:2rem;">No products found.</p>';
    } else {
      grid.innerHTML = data.products.map(p => {
        const images = p.images || [];
        const img = images.length > 0 ? images[0] : '';
        return `
          <div class="product-card">
            ${img ? `<img class="product-card-img" src="${img}" onerror="this.style.display='none'" alt="${p.title}">` : '<div class="product-card-img" style="display:flex;align-items:center;justify-content:center;font-size:3rem;background:var(--gray-100)">📦</div>'}
            <div class="product-card-title" title="${escapeHtml(p.title || '')}">${p.title || 'Unknown'}</div>
            <div class="product-card-brand">${p.brand || '—'}</div>
            <div class="product-card-upc">${p.upc}</div>
            <div class="product-card-actions">
              <button class="btn btn-secondary" onclick="doLookup('${p.upc}'); switchTab('scanner');">View</button>
              <button class="btn btn-danger" onclick="deleteProductByUpc('${p.upc}')">Delete</button>
            </div>
          </div>
        `;
      }).join('');
    }

    // Pagination
    const totalPages = Math.ceil(data.total / DB_PAGE_SIZE);
    const pagination = document.getElementById('pagination');
    if (totalPages > 1) {
      let html = '';
      if (dbPage > 0) html += `<button class="btn btn-secondary" onclick="dbPage--;loadProducts()">← Prev</button>`;
      html += `<span style="padding:0.5rem;color:var(--gray-500);">Page ${dbPage + 1} of ${totalPages}</span>`;
      if (dbPage < totalPages - 1) html += `<button class="btn btn-secondary" onclick="dbPage++;loadProducts()">Next →</button>`;
      pagination.innerHTML = html;
    } else {
      pagination.innerHTML = '';
    }
  } catch (err) {
    console.error('Error loading products:', err);
  }
}

async function deleteProductByUpc(upc) {
  if (!confirm(`Delete product ${upc}?`)) return;
  try {
    await fetch(`${API_BASE}/api/products/${upc}`, { method: 'DELETE' });
    loadProducts();
  } catch (err) {
    alert('Error deleting product: ' + err.message);
  }
}

async function exportProducts() {
  try {
    const response = await fetch(`${API_BASE}/api/export`, { method: 'POST' });
    const data = await response.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `upc-products-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert('Error exporting: ' + err.message);
  }
}

// ─── Bulk Import Tab ──────────────────────────────────────────────────────────

document.getElementById('bulk-lookup-btn').addEventListener('click', doBulkLookup);
document.getElementById('import-btn').addEventListener('click', doFileImport);

async function doBulkLookup() {
  const text = document.getElementById('bulk-upcs').value.trim();
  if (!text) return;

  const upcs = text.split('\n').map(s => s.trim()).filter(s => s);
  if (upcs.length === 0) return;
  if (upcs.length > 50) {
    alert('Maximum 50 UPCs at a time');
    return;
  }

  const statusEl = document.getElementById('bulk-status');
  const resultsEl = document.getElementById('bulk-results');
  statusEl.textContent = `Processing ${upcs.length} UPCs...`;
  resultsEl.innerHTML = '';

  try {
    const response = await fetch(`${API_BASE}/api/bulk-scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ upcs }),
    });
    const data = await response.json();

    statusEl.textContent = `Done! Found: ${data.found}, Not found: ${data.notFound}`;

    resultsEl.innerHTML = data.results.map(r => `
      <div class="bulk-result-item ${r.found ? 'found' : 'not-found'}">
        <strong>${r.upc}</strong>
        ${r.found
          ? `— ${r.product.title || 'Unknown'} ${r.product.brand ? '(' + r.product.brand + ')' : ''} ${r.fromCache ? '📁' : '🌐'}`
          : '— Not found'}
      </div>
    `).join('');
  } catch (err) {
    statusEl.textContent = 'Error: ' + err.message;
  }
}

async function doFileImport() {
  const fileInput = document.getElementById('import-file');
  const statusEl = document.getElementById('import-status');

  if (!fileInput.files.length) {
    alert('Please select a JSON file');
    return;
  }

  const file = fileInput.files[0];
  const text = await file.text();

  try {
    const products = JSON.parse(text);
    const response = await fetch(`${API_BASE}/api/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ products: Array.isArray(products) ? products : [products] }),
    });
    const data = await response.json();
    statusEl.innerHTML = `<p>✅ ${data.message}: Imported ${data.imported}, Skipped ${data.skipped}, Errors ${data.errors}</p>`;
  } catch (err) {
    statusEl.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
  }
}

// ─── Stats Tab ────────────────────────────────────────────────────────────────

async function loadStats() {
  try {
    const response = await fetch(`${API_BASE}/api/stats`);
    const stats = await response.json();

    document.getElementById('stat-products').textContent = stats.totalProducts;
    document.getElementById('stat-scans').textContent = stats.totalScans;

    document.getElementById('top-brands').innerHTML = stats.topBrands.length > 0
      ? stats.topBrands.map(b => `<div class="brand-item"><span>${b.brand}</span><span class="brand-count">${b.count}</span></div>`).join('')
      : '<p style="color:var(--gray-500)">No brands yet</p>';

    document.getElementById('recently-added').innerHTML = stats.recentlyAdded.length > 0
      ? stats.recentlyAdded.map(p => `<div class="brand-item"><span>${p.title || p.upc}</span><span style="color:var(--gray-500);font-size:0.8rem">${formatTime(p.created_at)}</span></div>`).join('')
      : '<p style="color:var(--gray-500)">No products yet</p>';
  } catch (err) {
    console.error('Error loading stats:', err);
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function hideAllResults() {
  document.getElementById('scan-result').style.display = 'none';
  document.getElementById('not-found').style.display = 'none';
}

function showLoading(show) {
  document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function safeJsonParse(str, fallback) {
  if (!str) return fallback;
  if (typeof str !== 'string') return str;
  try { return JSON.parse(str); } catch { return fallback; }
}

function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return d.toLocaleDateString();
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ─── Init ─────────────────────────────────────────────────────────────────────
loadRecentScans();
