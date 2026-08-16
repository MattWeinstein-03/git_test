# 📦 UPC Product Database

Scan barcodes, look up product info (descriptions, images, nutrition), and build your own comprehensive product database over time.

## Features

- **📷 Camera Barcode Scanner** — Use your phone or webcam to scan UPC/EAN/Code128/Code39 barcodes
- **🔍 Manual UPC Lookup** — Type in a UPC code to look it up
- **💾 Local SQLite Database** — Products are cached locally so subsequent lookups are instant
- **🌐 Multi-Source API** — Queries 3 free APIs for maximum coverage:
  - [UPCitemdb](https://www.upcitemdb.com/) — 722M+ products (100 free lookups/day)
  - [Open Food Facts](https://world.openfoodfacts.org/) — Food/beverage products (unlimited, community-driven)
  - [Open Beauty Facts](https://world.openbeautyfacts.org/) — Cosmetics/personal care
- **📑 Bulk Import** — Paste multiple UPC codes for batch lookup
- **📥 Export/Import** — Export your database as JSON, import it elsewhere
- **📊 Statistics** — Track your scanning activity and top brands
- **✏️ Manual Entry** — Add products not found in any API

## Quick Start

```bash
# Install dependencies
npm install

# Start the server
npm start

# Open in your browser
# http://localhost:3000
```

## How It Works

1. **Scan or enter a UPC code**
2. **App checks your local database first** (instant if previously scanned)
3. **If not found locally, queries free APIs** (UPCitemdb → Open Food Facts → Open Beauty Facts)
4. **Saves the result to your local SQLite database** for future lookups
5. **Your database grows** every time you scan something new

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scan` | Look up a single UPC (checks local DB first, then APIs) |
| POST | `/api/bulk-scan` | Look up multiple UPCs (max 50) |
| GET | `/api/products` | List products (supports `?search=`, `?limit=`, `?offset=`) |
| GET | `/api/products/:upc` | Get a single product |
| PUT | `/api/products/:upc` | Add/update a product manually |
| DELETE | `/api/products/:upc` | Remove a product |
| GET | `/api/history` | Recent scan history |
| GET | `/api/stats` | Database statistics |
| POST | `/api/export` | Export all products as JSON |
| POST | `/api/import` | Import products from JSON array |

## Example API Usage

```bash
# Look up a product
curl -X POST http://localhost:3000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"upc": "049000042566"}'

# Search your database
curl "http://localhost:3000/api/products?search=coca+cola"

# Bulk lookup
curl -X POST http://localhost:3000/api/bulk-scan \
  -H "Content-Type: application/json" \
  -d '{"upcs": ["049000042566", "3017620422003", "038000138416"]}'

# Manually add a product
curl -X PUT http://localhost:3000/api/products/012345678901 \
  -H "Content-Type: application/json" \
  -d '{"title": "My Product", "brand": "MyBrand", "category": "Electronics"}'
```

## Database

Products are stored in `products.db` (SQLite) with these fields:
- `upc` — The barcode number
- `title` — Product name
- `description` — Product description
- `brand` — Brand name
- `category` — Product category
- `images` — Array of image URLs
- `weight` — Weight/size
- `ingredients` — Ingredients list (food products)
- `nutrition_facts` — Nutrition per 100g (food products)
- `source` — Which API provided the data

## Rate Limits (Free Tiers)

| Source | Limit | Coverage |
|--------|-------|----------|
| UPCitemdb | 100 requests/day | General products (722M+ items) |
| Open Food Facts | Unlimited | Food & beverages |
| Open Beauty Facts | Unlimited | Cosmetics & personal care |

## Tech Stack

- **Backend:** Node.js, Express
- **Database:** SQLite (via better-sqlite3)
- **Frontend:** Vanilla HTML/CSS/JS
- **Scanner:** QuaggaJS (camera-based barcode reading)
- **APIs:** UPCitemdb, Open Food Facts, Open Beauty Facts

## Tips

- **For higher API limits:** Sign up for a free UPCitemdb API key at https://devs.upcitemdb.com/ and add it to the headers in `src/api-lookup.js`
- **Mobile scanning:** Works best on phones with rear camera — just open the URL on your phone
- **Growing your DB:** The more you scan, the faster lookups become (local DB is checked first)
- **Backing up:** Copy `products.db` to back up your entire product database
