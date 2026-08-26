import fetch from 'node-fetch';

/**
 * Multi-source UPC product lookup.
 * Tries UPCitemdb (free tier, no key needed for trial) first,
 * then falls back to Open Food Facts (completely free, open data).
 * Returns a normalized product object or null.
 */

// ─── UPCitemdb (Free Trial: 100 requests/day, no API key needed) ──────────────

async function lookupUPCitemdb(upc) {
  try {
    const response = await fetch(`https://api.upcitemdb.com/prod/trial/lookup?upc=${upc}`, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: 10000,
    });

    if (!response.ok) {
      console.log(`[UPCitemdb] HTTP ${response.status} for UPC: ${upc}`);
      return null;
    }

    const data = await response.json();

    if (!data.items || data.items.length === 0) {
      console.log(`[UPCitemdb] No items found for UPC: ${upc}`);
      return null;
    }

    const item = data.items[0];
    return normalizeUPCitemdb(item, upc, data);
  } catch (err) {
    console.error(`[UPCitemdb] Error looking up UPC ${upc}:`, err.message);
    return null;
  }
}

function normalizeUPCitemdb(item, upc, rawData) {
  const images = [];
  if (item.images && item.images.length > 0) {
    images.push(...item.images);
  }

  return {
    upc,
    title: item.title || null,
    description: item.description || null,
    brand: item.brand || null,
    category: item.category || null,
    images,
    weight: item.weight || null,
    dimensions: item.dimension || null,
    ingredients: null,
    nutrition_facts: null,
    source: 'upcitemdb',
    raw_data: rawData,
  };
}

// ─── Open Food Facts (Completely free, community-driven, great for food) ──────

async function lookupOpenFoodFacts(upc) {
  try {
    const response = await fetch(
      `https://world.openfoodfacts.org/api/v2/product/${upc}.json`,
      {
        headers: {
          'User-Agent': 'UPCProductDB/1.0 (contact@example.com)',
        },
        timeout: 10000,
      }
    );

    if (!response.ok) {
      console.log(`[OpenFoodFacts] HTTP ${response.status} for UPC: ${upc}`);
      return null;
    }

    const data = await response.json();

    if (data.status !== 1 || !data.product) {
      console.log(`[OpenFoodFacts] Product not found for UPC: ${upc}`);
      return null;
    }

    return normalizeOpenFoodFacts(data.product, upc, data);
  } catch (err) {
    console.error(`[OpenFoodFacts] Error looking up UPC ${upc}:`, err.message);
    return null;
  }
}

function normalizeOpenFoodFacts(product, upc, rawData) {
  const images = [];
  if (product.image_url) images.push(product.image_url);
  if (product.image_front_url) images.push(product.image_front_url);
  if (product.image_nutrition_url) images.push(product.image_nutrition_url);
  if (product.image_ingredients_url) images.push(product.image_ingredients_url);
  // Deduplicate
  const uniqueImages = [...new Set(images)];

  const nutritionFacts = product.nutriments
    ? {
        energy_kcal: product.nutriments['energy-kcal_100g'],
        fat: product.nutriments.fat_100g,
        saturated_fat: product.nutriments['saturated-fat_100g'],
        carbohydrates: product.nutriments.carbohydrates_100g,
        sugars: product.nutriments.sugars_100g,
        fiber: product.nutriments.fiber_100g,
        proteins: product.nutriments.proteins_100g,
        salt: product.nutriments.salt_100g,
        sodium: product.nutriments.sodium_100g,
      }
    : null;

  return {
    upc,
    title: product.product_name || product.product_name_en || null,
    description: product.generic_name || product.generic_name_en || null,
    brand: product.brands || null,
    category: product.categories || null,
    images: uniqueImages,
    weight: product.quantity || null,
    dimensions: null,
    ingredients: product.ingredients_text || product.ingredients_text_en || null,
    nutrition_facts: nutritionFacts,
    source: 'openfoodfacts',
    raw_data: rawData,
  };
}

// ─── Open Beauty Facts (for cosmetics/personal care) ──────────────────────────

async function lookupOpenBeautyFacts(upc) {
  try {
    const response = await fetch(
      `https://world.openbeautyfacts.org/api/v2/product/${upc}.json`,
      {
        headers: {
          'User-Agent': 'UPCProductDB/1.0 (contact@example.com)',
        },
        timeout: 10000,
      }
    );

    if (!response.ok) return null;

    const data = await response.json();
    if (data.status !== 1 || !data.product) return null;

    const product = data.product;
    const images = [];
    if (product.image_url) images.push(product.image_url);
    if (product.image_front_url) images.push(product.image_front_url);

    return {
      upc,
      title: product.product_name || null,
      description: product.generic_name || null,
      brand: product.brands || null,
      category: product.categories || null,
      images: [...new Set(images)],
      weight: product.quantity || null,
      dimensions: null,
      ingredients: product.ingredients_text || null,
      nutrition_facts: null,
      source: 'openbeautyfacts',
      raw_data: data,
    };
  } catch (err) {
    console.error(`[OpenBeautyFacts] Error looking up UPC ${upc}:`, err.message);
    return null;
  }
}

// ─── Main Lookup (cascading through sources) ──────────────────────────────────

/**
 * Look up a UPC across multiple free APIs.
 * Returns the first successful result, or null if none found.
 */
export async function lookupUPC(upc) {
  // Clean the UPC - remove any spaces or dashes
  const cleanUpc = upc.replace(/[\s\-]/g, '');

  console.log(`[Lookup] Searching for UPC: ${cleanUpc}`);

  // Strategy: Try UPCitemdb first (broadest coverage for general products)
  // Then Open Food Facts (best for food/beverages)
  // Then Open Beauty Facts (cosmetics/personal care)

  let result = await lookupUPCitemdb(cleanUpc);
  if (result && result.title) {
    console.log(`[Lookup] Found via UPCitemdb: ${result.title}`);
    return result;
  }

  result = await lookupOpenFoodFacts(cleanUpc);
  if (result && result.title) {
    console.log(`[Lookup] Found via OpenFoodFacts: ${result.title}`);
    return result;
  }

  result = await lookupOpenBeautyFacts(cleanUpc);
  if (result && result.title) {
    console.log(`[Lookup] Found via OpenBeautyFacts: ${result.title}`);
    return result;
  }

  console.log(`[Lookup] No results found for UPC: ${cleanUpc}`);
  return null;
}

/**
 * Bulk lookup - process an array of UPCs with rate limiting.
 * Returns an array of { upc, product, found } objects.
 */
export async function bulkLookup(upcs, { delayMs = 1500 } = {}) {
  const results = [];

  for (let i = 0; i < upcs.length; i++) {
    const upc = upcs[i].trim();
    if (!upc) continue;

    console.log(`[Bulk] Processing ${i + 1}/${upcs.length}: ${upc}`);
    const product = await lookupUPC(upc);
    results.push({ upc, product, found: !!product });

    // Rate limiting - be nice to free APIs
    if (i < upcs.length - 1) {
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  return results;
}
