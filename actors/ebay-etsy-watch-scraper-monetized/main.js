// eBay + Etsy Marketplace Scraper Pro
// Smart search across eBay (active) and Etsy (active) - international brands only
// Anti-bot: Bright Data web_unlocker1

const https = require('https');

// ============================================================================
// CONFIG
// ============================================================================

const HARD_LIMITS = {
  MAX_PRESETS: 8,
  MAX_CUSTOM_TERMS: 20,
  MAX_LISTINGS_PER_QUERY: 100,
  MAX_DURATION_MIN: 30,
  MAX_TOTAL_CHARGE_USD: 2.00,
};

const EXCHANGE_RATE = {
  USD_TO_GBP: 0.79,
  USD_TO_EUR: 0.92,
};

const EBAY_BASE = 'https://www.ebay.com';
const ETSY_BASE = 'https://www.etsy.com';

// 8 PUBLIC category presets (NO Soviet brands - those stay internal)
const PRESET_TERMS = {
  // ========== WATCHES (kept for watch collectors) ==========
  'watches-luxury': {
    label: 'Luxury Watches',
    ebayTerms: ['rolex', 'omega', 'tudor', 'breitling', 'iwc', 'patek philippe', 'hublot', 'tag heuer', 'longines', 'zenith', 'cartier', 'audemars piguet'],
    etsyTerms: ['vintage rolex', 'vintage omega', 'vintage tudor', 'luxury watch vintage', 'breitling vintage', 'iwc vintage'],
  },
  'watches-japanese': {
    label: 'Japanese Watches',
    ebayTerms: ['seiko', 'casio', 'orient', 'citizen', 'grand seiko', 'seiko skx', 'seiko turtle', 'seiko samurai', 'casio g-shock'],
    etsyTerms: ['vintage seiko', 'seiko skx', 'casio g-shock', 'vintage casio', 'orient watch'],
  },
  'watches-vintage': {
    label: 'Vintage Watches',
    ebayTerms: ['vintage watch', 'antique watch', 'vintage rolex', 'vintage omega', 'vintage seiko', 'vintage timex', 'vintage citizen'],
    etsyTerms: ['vintage watch', 'antique watch', 'vintage timepiece', 'vintage wristwatch', 'retro watch'],
  },
  'watches-dive': {
    label: 'Dive Watches',
    ebayTerms: ['dive watch', 'submariner', 'seamaster', 'pelagos', 'seiko skx', 'seiko turtle', 'orca', 'bathyscaphe', 'fifty fathoms'],
    etsyTerms: ['dive watch', 'vintage diver', 'submariner style', 'seiko skx', 'vintage seiko diver'],
  },
  'watches-dress': {
    label: 'Dress Watches',
    ebayTerms: ['dress watch', 'tank', 'calatrava', 'datejust', 'santos', 'royal oak', 'nautilus', 'patrimony', 'elegance'],
    etsyTerms: ['dress watch vintage', 'tank watch', 'datejust', 'elegant watch', 'thin watch', 'classic watch'],
  },
  'watches-sports': {
    label: 'Sports / Chronograph',
    ebayTerms: ['chronograph', 'speedmaster', 'daytona', 'gmt', 'gmt-master', 'navitimer', 'superocean'],
    etsyTerms: ['chronograph vintage', 'speedmaster', 'daytona', 'vintage chronograph', 'racing watch'],
  },
  'watches-pilot': {
    label: 'Pilot / Aviator',
    ebayTerms: ['pilot watch', 'aviator', 'iwc pilot', 'mark xi', 'big pilot', 'flieger', 'breguet type xx'],
    etsyTerms: ['pilot watch', 'aviator watch', 'vintage pilot', 'flieger', 'big pilot'],
  },
  'watches-field': {
    label: 'Field / Military',
    ebayTerms: ['field watch', 'military watch', 'khaki field', 'a-11', 'hack watch', 'marathon watch', 'general purpose watch'],
    etsyTerms: ['field watch', 'military watch', 'vintage military', 'khaki field', 'dirty dozen'],
  },

  // ========== SPORTS CARDS (new - for card collectors) ==========
  'cards-sports': {
    label: 'Sports Cards',
    ebayTerms: ['baseball card', 'basketball card', 'football card', 'hockey card', 'rookie card', 'graded card', 'PSA card', 'BGS card', 'sports card', 'trading card'],
    etsyTerms: ['vintage sports card', 'rookie card', 'baseball memorabilia', 'signed card', 'sports memorabilia'],
  },
  'cards-graded': {
    label: 'Graded Cards (PSA/BGS/CGC)',
    ebayTerms: ['PSA 10', 'PSA 9', 'BGS 9.5', 'CGC graded', 'graded card', 'slabbed card', 'gem mint card', 'mint card'],
    etsyTerms: ['graded sports card', 'PSA graded card', 'BGS graded', 'slabbed card art'],
  },

  // ========== TCG / POKEMON (new) ==========
  'cards-pokemon': {
    label: 'Pokemon Cards',
    ebayTerms: ['pokemon card', 'charizard', 'pikachu', 'pokemon PSA', 'pokemon graded', '1st edition pokemon', 'pokemon base set', 'pokemon booster', 'pokemon Japanese'],
    etsyTerms: ['pokemon card', 'vintage pokemon', 'pokemon art', 'pokemon card art', 'pokemon illustration'],
  },
  'cards-tcg': {
    label: 'TCG Cards (MTG/Yu-Gi-Oh)',
    ebayTerms: ['magic the gathering', 'MTG card', 'black lotus', 'reserved list', 'MTG alpha', 'MTG beta', 'yu-gi-oh card', 'one piece card', 'MTG modern'],
    etsyTerms: ['MTG card art', 'vintage MTG', 'Yu-Gi-Oh card', 'MTG altered art', 'MTG playmat'],
  },

  // ========== SNEAKERS (new) ==========
  'sneakers-collectible': {
    label: 'Collectible Sneakers',
    ebayTerms: ['jordan', 'nike', 'yeezy', 'sneaker', 'deadstock sneaker', 'retro sneaker', 'air jordan', 'dunk low', 'travis scott', 'off-white'],
    etsyTerms: ['custom sneakers', 'handmade shoes', 'vintage sneakers', 'sneaker art', 'sneaker customization'],
  },

  // ========== VINTAGE / GENERAL (new) ==========
  'vintage-general': {
    label: 'Vintage Collectibles',
    ebayTerms: ['vintage item', 'antique', 'collectible', 'retro', 'nostalgia', 'vintage toy', 'vintage memorabilia'],
    etsyTerms: ['vintage', 'antique', 'handmade vintage', 'retro decor', 'mid century', 'vintage collectible'],
  },
};

// ============================================================================
// SMART SEARCH
// ============================================================================

const PATTERNS = {
  brand: /\b(rolex|omega|tudor|seiko|casio|orient|citizen|breitling|iwc|hublot|longines|zenith|patek|tag heuer|tissot|rado|cartier|audemars piguet|chopard|montblanc|oris|baume mercier|jaeger lecoultre|grand seiko|bell ross|graham|ulysse nardin|panerai|certina|amilton|mido|alpina)\b/i,
  model: /\b(submariner|seamaster|constellation|speedmaster|seamaster|datejust|daytona|gmt[- ]master|navitimer|royal oak|nautilus|tank|santos|calatrava|patrimony|skx\d+|turtle|samurai|monster|g-shock|presage|prospex|black bay|bremont|flyback|tourbillon|perpetual|chronograph|automatic|date\s*?\d{2,})\b/i,
  price: /\b(?:under|below|less than|<=?)\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\b/i,
  condition: /\b(new|used|unworn|preowned|full set|box|papers)\b/i,
};

function interpretQuery(text) {
  if (!text || text.length < 2) return null;
  const result = { brands: [], models: [], priceFilter: null, queryTerms: [], isLikelyPersonOrProperNoun: false };

  // Detect person names or proper nouns (likely player/celebrity names)
  // Pattern: capitalized words that aren't common English words
  const STOPWORDS = ['A', 'An', 'The', 'And', 'Or', 'Of', 'In', 'On', 'For', 'With', 'Vintage', 'New', 'Used', 'Box', 'Papers'];
  const words = text.split(/\s+/);
  const capitalizedWords = words.filter(w => /^[A-Z][a-z]+/.test(w) && !STOPWORDS.includes(w));
  // If 2+ capitalized words (e.g., "Wayne Gretzky"), likely a proper noun
  if (capitalizedWords.length >= 2) {
    result.isLikelyPersonOrProperNoun = true;
    result.queryTerms.push(text); // Use literal query
    return result;
  }

  const brandMatch = text.match(PATTERNS.brand);
  if (brandMatch) result.brands.push(brandMatch[1].toLowerCase());

  const modelMatch = text.match(PATTERNS.model);
  if (modelMatch) result.models.push(modelMatch[1].toLowerCase());

  const priceMatch = text.match(PATTERNS.price);
  if (priceMatch) result.priceFilter = { max: parseInt(priceMatch[1].replace(/,/g, ''), 10) };

  // Build query terms
  if (result.brands.length > 0) {
    result.brands.forEach(b => {
      result.queryTerms.push(b);
      if (result.models.length > 0) {
        result.models.forEach(m => result.queryTerms.push(`${b} ${m}`));
      }
    });
  } else if (result.models.length > 0) {
    result.models.forEach(m => result.queryTerms.push(m));
  } else {
    result.queryTerms.push(text);
  }

  result.matchedPreset = result.isLikelyPersonOrProperNoun ? null : matchPreset(result);
  result.presetLabel = result.matchedPreset ? PRESET_TERMS[result.matchedPreset].label : 'Custom';
  return result;
}

function matchPreset(interpretation) {
  let best = null, bestScore = 0;
  for (const [id, preset] of Object.entries(PRESET_TERMS)) {
    let score = 0;
    for (const brand of interpretation.brands) {
      if (preset.ebayTerms.some(t => t.toLowerCase().includes(brand))) score += 3;
    }
    for (const term of interpretation.queryTerms) {
      if (preset.ebayTerms.some(t => t.toLowerCase().includes(term.toLowerCase()))) score += 2;
    }
    if (score > bestScore) {
      bestScore = score;
      best = id;
    }
  }
  return best;
}

// ============================================================================
// BRIGHT DATA FETCH
// ============================================================================

function bdFetch(token, zone, url) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ zone, url, format: 'raw' });
    const req = https.request({
      hostname: 'api.brightdata.com',
      path: '/request',
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
      timeout: 120000,
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        if (res.statusCode === 200) resolve(data);
        else reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('BD timeout 120s')); });
    req.write(body);
    req.end();
  });
}

async function safeBdFetch(token, zone, url, ms = 120000) {
  return new Promise((resolve) => {
    let done = false;
    const t = setTimeout(() => { if (!done) { done = true; resolve(null); } }, ms);
    bdFetch(token, zone, url).then(html => {
      if (done) return;
      done = true; clearTimeout(t); resolve(html);
    }).catch(() => {
      if (done) return;
      done = true; clearTimeout(t); resolve(null);
    });
  });
}

// ============================================================================
// URL BUILDING
// ============================================================================

function buildEbaySearchUrl(term, pageNum = 1, soldOnly = false) {
  // eBay sold listings filter: LH_Sold=1 shows only sold, LH_Complete=1 includes completed
  // This works through Bright Data (not blocked like direct access)
  const params = new URLSearchParams();
  params.set('_nkw', term);
  params.set('_ipg', '60');
  params.set('_sop', '13');
  if (soldOnly) {
    params.set('LH_Sold', '1');
    params.set('LH_Complete', '1');
  }
  if (pageNum > 1) params.set('_pgn', pageNum);
  return `${EBAY_BASE}/sch/i.html?${params.toString()}`;
}

function buildEtsySearchUrl(term, pageNum = 1) {
  const params = new URLSearchParams();
  params.set('q', term);
  if (pageNum > 1) params.set('page', pageNum);
  return `${ETSY_BASE}/search?${params.toString()}`;
}

// ============================================================================
// HTML PARSING - eBay
// ============================================================================

function parseEbayListingsFromHtml(html, maxItems, soldOnlyFlag = false) {
  if (!html) return [];
  const results = [];
  const itemRegex = /<li[^>]*class="[^"]*s-card[^"]*"[^>]*data-listingid="(\d+)"[\s\S]*?(?=<li[^>]*class="[^"]*s-card|$)/g;
  let m;
  const seen = new Set();
  while ((m = itemRegex.exec(html)) !== null && results.length < maxItems) {
    const listingId = m[1];
    if (seen.has(listingId)) continue;
    seen.add(listingId);
    const start = m.index;
    const end = Math.min(html.length, start + 15000);
    const block = html.slice(start, end);

    const titleMatch = block.match(/<div[^>]*class="[^"]*s-card__title[^"]*"[^>]*>[\s\S]*?<span[^>]*class="[^"]*su-styled-text[^"]*"[^>]*>([^<]+)</) ||
                       block.match(/<span[^>]*class="[^"]*s-item__title[^"]*"[^>]*>([^<]+)<\/span>/);
    let title = titleMatch ? titleMatch[1].trim() : null;
    if (title) title = decodeHtmlEntities(title);

    const priceMatch = block.match(/<span[^>]*class="[^"]*s-card__price[^"]*"[^>]*>([\s\S]{0,200}?)<\/span>/) ||
                       block.match(/<span[^>]*class="[^"]*s-item__price[^"]*"[^>]*>([\s\S]{0,200}?)<\/span>/);
    let priceUsd = 0;
    let priceRaw = '';
    if (priceMatch) {
      priceRaw = priceMatch[1].trim();
      const numMatch = priceRaw.match(/[\$£€]\s*([\d,]+(?:\.\d{2})?)/);
      if (numMatch) {
        const symbol = priceRaw[0];
        const num = parseFloat(numMatch[1].replace(/,/g, ''));
        if (symbol === '$' || symbol === '') priceUsd = num;
        else if (symbol === '£') priceUsd = Math.round(num / EXCHANGE_RATE.USD_TO_GBP);
        else if (symbol === '€') priceUsd = Math.round(num / EXCHANGE_RATE.USD_TO_EUR);
      }
    }

    const urlMatch = block.match(/href="(https:\/\/www\.ebay\.com\/itm\/\d+)/);
    const url = urlMatch ? urlMatch[1].replace(/&amp;/g, '&') : `${EBAY_BASE}/itm/${listingId}`;

    if (title && listingId) {
      // Detect if this is a sold listing (only works if LH_Sold=1 doesn't get blocked)
      const isSold = soldOnlyFlag && /class="[^"]*s-card__sold[^"]*"|>Sold\s*</i.test(block);
      
      // Try to extract "X sold" count (eBay shows this on active listings)
      // Example: "112 sold" or "25 watchers"
      const soldCountMatch = block.match(/(\d+)\s*sold/i);
      const watchersMatch = block.match(/(\d+)\s*(?:watchers|watching)/i);
      
      results.push({
        title: title.substring(0, 250),
        url,
        price_usd: Math.round(priceUsd),
        price_raw: priceRaw,
        currency: priceRaw.startsWith('£') ? 'GBP' : priceRaw.startsWith('€') ? 'EUR' : 'USD',
        listing_id: listingId,
        marketplace: 'ebay',
        listing_type: isSold ? 'sold' : 'active',
        sold_date: isSold ? extractSoldDate(block) : null,
        sold_count: soldCountMatch ? parseInt(soldCountMatch[1]) : null,
        watchers_count: watchersMatch ? parseInt(watchersMatch[1]) : null,
      });
    }
  }
  return results;
}

function extractSoldDate(html) {
  // Try to extract sold date from eBay sold listings
  const dateMatch = html.match(/Sold\s+([A-Z][a-z]{2}\s+\d+,?\s+\d{4})/i) ||
                    html.match(/Sold\s+(\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4})/i);
  return dateMatch ? dateMatch[1] : null;
}

// ============================================================================
// HTML PARSING - Etsy
// ============================================================================

function parseEtsyListingsFromHtml(html, maxItems) {
  if (!html) return [];
  const results = [];
  const itemRegex = /data-listing-id="(\d+)"[\s\S]*?(?=data-listing-id=|<\/ul>)/g;
  let m;
  const seen = new Set();
  while ((m = itemRegex.exec(html)) !== null && results.length < maxItems) {
    const listingId = m[1];
    if (seen.has(listingId)) continue;
    seen.add(listingId);
    const start = m.index;
    const end = Math.min(html.length, start + 8000);
    const block = html.slice(start, end);

    const ariaMatch = block.match(/aria-label="([^"]+)"/);
    const title = ariaMatch ? decodeHtmlEntities(ariaMatch[1].trim()) : null;

    let priceUsd = 0;
    let priceRaw = '';
    const jsonLdMatch = block.match(/"@type":"Offer"[\s\S]{0,500}?"price":"([\d.]+)"/);
    if (jsonLdMatch) {
      priceUsd = parseFloat(jsonLdMatch[1]);
      priceRaw = '$' + priceUsd.toFixed(2);
    } else {
      const cvMatch = block.match(/class="[^"]*currency-value[^"]*"[^>]*>([^<]+)</);
      if (cvMatch) {
        const num = parseFloat(cvMatch[1].replace(/[^\d.]/g, ''));
        if (!isNaN(num)) {
          priceUsd = num;
          priceRaw = '$' + num.toFixed(2);
        }
      }
    }

    const urlMatch = block.match(/href="(https:\/\/www\.etsy\.com\/[^"]*\/listing\/\d+\/[^"?]+)/);
    const url = urlMatch ? urlMatch[1].replace(/&amp;/g, '&') : `${ETSY_BASE}/listing/${listingId}`;

    const shopMatch = block.match(/data-shop-id="(\d+)"/);
    const shopId = shopMatch ? shopMatch[1] : null;

    if (title && listingId && priceUsd > 0) {
      results.push({
        title: title.substring(0, 250),
        url,
        price_usd: Math.round(priceUsd),
        price_raw: priceRaw,
        currency: 'USD',
        listing_id: listingId,
        shop_id: shopId,
        marketplace: 'etsy',
      });
    }
  }
  return results;
}

function decodeHtmlEntities(s) {
  return (s || '')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, ' ');
}

// ============================================================================
// MAIN (Apify SDK)
// ============================================================================

const apify = require('apify');
const { Actor } = apify;

Actor.main(async () => {
  const input = await Actor.getInput() || {};
  const { presets = [], customSearchTerms = [], smartSearch = '', maxListingsPerQuery = 50,
          marketplaces = ['ebay', 'etsy'],
          brightDataToken, brightDataZone = 'web_unlocker1',
          includeSold = false } = input;

  if (!brightDataToken) throw new Error('brightDataToken is required');

  console.log(`[START] smartSearch="${smartSearch}" marketplaces=${marketplaces.join(',')} presets=${presets.join(',')} custom=${customSearchTerms.length} includeSold=${includeSold}`);

  const allQueries = [];

  if (smartSearch) {
    const interp = interpretQuery(smartSearch);
    if (interp) {
      console.log(`[SMART] brands=${interp.brands.length} matched_preset=${interp.matchedPreset || 'none'}`);
      for (const term of interp.queryTerms) {
        for (const m of marketplaces) {
          allQueries.push({ term, source: 'smart', label: interp.presetLabel, marketplace: m });
        }
      }
    }
  }

  for (const presetId of presets) {
    if (PRESET_TERMS[presetId]) {
      const p = PRESET_TERMS[presetId];
      if (marketplaces.includes('ebay')) {
        for (const term of p.ebayTerms) {
          allQueries.push({ term, source: `preset:${presetId}`, label: p.label, marketplace: 'ebay' });
        }
      }
      if (marketplaces.includes('etsy')) {
        for (const term of p.etsyTerms) {
          allQueries.push({ term, source: `preset:${presetId}`, label: p.label, marketplace: 'etsy' });
        }
      }
    }
  }
  for (const term of customSearchTerms) {
    for (const m of marketplaces) {
      allQueries.push({ term, source: 'custom', label: 'Custom', marketplace: m });
    }
  }

  if (allQueries.length === 0) throw new Error('No queries. Provide smartSearch, presets, or customSearchTerms.');

  console.log(`[QUERIES] ${allQueries.length} unique search queries`);

  let allResults = [];
  let bdRequests = 0;
  let estimatedCost = 0;
  const startTime = Date.now();
  const stats = { ebay: 0, etsy: 0 };

  for (const q of allQueries) {
    if (Date.now() - startTime > HARD_LIMITS.MAX_DURATION_MIN * 60 * 1000) {
      console.log('[TIMEOUT] reached max duration');
      break;
    }
    if (estimatedCost >= HARD_LIMITS.MAX_TOTAL_CHARGE_USD) {
      console.log('[COST] reached max budget');
      break;
    }

    try {
      const includeSold = input.includeSold || false;
      const url = q.marketplace === 'ebay'
        ? buildEbaySearchUrl(q.term, 1, includeSold)
        : buildEtsySearchUrl(q.term);
      console.log(`[SEARCH] ${q.marketplace}/${q.term} (${q.source}) soldOnly=${includeSold}`);
      const html = await safeBdFetch(brightDataToken, brightDataZone, url);
      bdRequests++;
      estimatedCost += 0.0015;

      if (!html || html.length < 5000) {
        console.log(`[SKIP] ${q.term} returned empty/short (${html?.length || 0} bytes)`);
        continue;
      }

      // DEBUG: Save first eBay HTML for inspection (only when soldOnly)
      if (q.marketplace === 'ebay' && includeSold && !global._ebaySoldHtmlSaved) {
        try {
          await Actor.setValue('ebay_sold_html_sample', html.substring(0, 200000));
          global._ebaySoldHtmlSaved = true;
          console.log(`[DEBUG] Saved eBay sold HTML sample (${html.length} bytes) to KV`);
        } catch (e) {
          console.log(`[DEBUG] Failed to save HTML: ${e.message}`);
        }
      }

      const listings = q.marketplace === 'ebay'
        ? parseEbayListingsFromHtml(html, maxListingsPerQuery, includeSold)
        : parseEtsyListingsFromHtml(html, maxListingsPerQuery);

      for (const card of listings) {
        card.search_term = q.term;
        card.search_source = q.source;
        card.preset_label = q.label;
        allResults.push(card);
      }
      stats[q.marketplace] += listings.length;
      console.log(`[FOUND] ${q.term} (${q.marketplace}): ${listings.length} listings`);
    } catch (err) {
      console.log(`[ERROR] ${q.term}: ${err.message}`);
    }
  }

  // Dedupe
  const seen = new Set();
  const unique = [];
  for (const r of allResults) {
    const key = `${r.marketplace}:${r.listing_id}`;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(r);
    }
  }

  console.log(`[RESULTS] ${unique.length} unique listings (ebay=${stats.ebay}, etsy=${stats.etsy})`);

  for (const item of unique) {
    await Actor.pushData(item);
  }

  const avgPrice = unique.length > 0
    ? Math.round(unique.reduce((a, b) => a + (b.price_usd || 0), 0) / unique.length)
    : 0;

  // Calculate price distribution stats
  const prices = unique.filter(item => item.price_usd > 0).map(item => item.price_usd).sort((a, b) => a - b);
  const minPrice = prices.length > 0 ? prices[0] : 0;
  const maxPrice = prices.length > 0 ? prices[prices.length - 1] : 0;
  const medianPrice = prices.length > 0
    ? (prices.length % 2 === 0
        ? Math.round((prices[prices.length / 2 - 1] + prices[prices.length / 2]) / 2)
        : prices[Math.floor(prices.length / 2)])
    : 0;
  const q1Price = prices.length >= 4 ? prices[Math.floor(prices.length * 0.25)] : 0;
  const q3Price = prices.length >= 4 ? prices[Math.floor(prices.length * 0.75)] : 0;

  await Actor.pushData({
    _summary: true,
    total_listings: unique.length,
    avg_price_usd: avgPrice,
    median_price_usd: medianPrice,
    min_price_usd: minPrice,
    max_price_usd: maxPrice,
    q1_price_usd: q1Price,
    q3_price_usd: q3Price,
    ebay_count: stats.ebay,
    etsy_count: stats.etsy,
    bd_requests: bdRequests,
    estimated_cost_usd: Math.round(estimatedCost * 1000) / 1000,
    run_duration_sec: Math.round((Date.now() - startTime) / 1000),
  });

  console.log(`[DONE] ${unique.length} listings | ${bdRequests} BD reqs | ~$${estimatedCost.toFixed(4)}`);
});
