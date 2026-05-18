"""
menu_scraper.py — fetches menu items per restaurant with images,
                   descriptions, prices, and categories.

Works with Zomato's current DOM (2026) where dish images have
alt=<dish name> instead of alt="dish".
"""

import json
import time
from playwright.sync_api import sync_playwright

CITIES = [
    {
        "input_file":  "restaurants.json",
        "output_file": "restaurants_delhi_full.json",
        "city":        "ncr"
    },
    {
        "input_file":  "restaurants_Patiala.json",
        "output_file": "restaurants_Patiala_full.json",
        "city":        "patiala"
    },
    {
        "input_file":  "restaurants_rajpura.json",
        "output_file": "restaurants_rajpura_full.json",
        "city":        "rajpura"
    },
]

BASE_URL  = "https://www.zomato.com"
DELAY     = 3
MAX_ITEMS = 50


def scrape_menu(page, url):
    """
    Navigate to a restaurant's order page and extract:
      - menu items (name, price, description, image, category)
      - basic info (address, phone, hours)
    """
    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # ── Slow scroll to trigger lazy-loading of all dish images ──
        prev_height = 0
        stall_count = 0
        while stall_count < 3:
            page.mouse.wheel(0, 600)
            page.wait_for_timeout(300)
            current_height = page.evaluate(
                "document.documentElement.scrollHeight"
            )
            if current_height == prev_height:
                stall_count += 1
            else:
                stall_count = 0
                prev_height = current_height

        # Scroll back up so evaluate runs from top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        # ── Extract menu items via JS ──
        menu = page.evaluate("""(MAX_ITEMS) => {

            const results = [];
            const seenNames = new Set();

            // ─── Strategy 1: Find images from zmtcdn dish_photos ───
            // Zomato dish images come from b.zmtcdn.com/data/dish_photos/
            // Their alt text = the dish name (e.g., "Farmhouse Pizza")
            const allImgs = Array.from(document.querySelectorAll('img'));
            const dishImgs = allImgs.filter(img => {
                const src = img.currentSrc || img.src || '';
                return src.includes('zmtcdn.com/data/dish_photos');
            });

            for (const img of dishImgs) {
                if (results.length >= MAX_ITEMS) break;

                const imgSrc = img.currentSrc || img.src || '';
                if (!imgSrc || imgSrc.startsWith('data:')) continue;

                // The alt attribute IS the dish name
                let name = (img.alt || '').trim();

                // Walk up to find the menu item card container
                let card = img.closest('[role="button"]')
                         || img.closest('[class*="dish"]')
                         || img.closest('[class*="item"]');

                // If no semantic container found, walk up manually
                if (!card) {
                    card = img.parentElement;
                    for (let i = 0; i < 8; i++) {
                        if (!card) break;
                        const t = (card.innerText || '').trim();
                        // Card should have a price
                        if (/₹[1-9]/.test(t) && t.length > 20) break;
                        card = card.parentElement;
                    }
                }
                if (!card) continue;

                const text = (card.innerText || '').trim();
                if (!text) continue;

                // Extract price
                const priceMatch = text.match(/₹\s*([1-9][\d,]*)/);
                if (!priceMatch) continue;
                const price = '₹' + priceMatch[1];

                // If we didn't get name from alt, get it from text
                if (!name || name === 'dish' || name === 'Dish') {
                    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
                    // Name = first line that isn't a price, rating, or badge
                    name = lines.find(l =>
                        l.length > 1
                        && l.length < 120
                        && !l.startsWith('₹')
                        && !/^[\d.]+$/.test(l)
                        && !/^(Bestseller|Must Try|NEW)$/i.test(l)
                        && !/^\d+\s*ratings?$/i.test(l)
                    ) || '';
                }

                if (!name || name.length > 120 || seenNames.has(name)) continue;
                seenNames.add(name);

                // Extract description: a meaningful line that isn't the name or price
                const textLines = text.split('\n').map(l => l.trim()).filter(Boolean);
                const description = textLines.find(l =>
                    l !== name
                    && !l.startsWith('₹')
                    && !/^[\d.]+$/.test(l)
                    && !/^\d+\s*ratings?$/i.test(l)
                    && !/^(Bestseller|Must Try|NEW|Customisable|ADD)$/i.test(l)
                    && l.length > 10
                    && l.length < 500
                ) || '';

                // Detect veg/non-veg badge
                let isVeg = null;
                const vegIcon = card.querySelector('[class*="veg"], [class*="Veg"]');
                if (vegIcon) {
                    const vegText = vegIcon.className || '';
                    if (/non.?veg/i.test(vegText)) isVeg = false;
                    else if (/veg/i.test(vegText)) isVeg = true;
                }

                results.push({
                    name,
                    price,
                    description,
                    image: imgSrc,
                    isVeg
                });
            }

            // ─── Strategy 2 (fallback): Find items by price pattern ───
            // For items without images
            if (results.length < 5) {
                // Look for elements containing prices
                const allEls = document.querySelectorAll('div, section, li');
                for (const el of allEls) {
                    if (results.length >= MAX_ITEMS) break;

                    const text = (el.innerText || '').trim();
                    if (!text || text.length > 1000 || text.length < 5) continue;

                    // Must have a price
                    if (!/₹[1-9]/.test(text)) continue;

                    // Should be a leaf-ish card (not a huge container)
                    const childDivs = el.querySelectorAll('div');
                    if (childDivs.length > 15) continue;

                    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
                    if (lines.length < 2) continue;

                    const name = lines.find(l =>
                        l.length > 2
                        && l.length < 120
                        && !l.startsWith('₹')
                        && !/^[\d.]+$/.test(l)
                        && !/^(Bestseller|Must Try|NEW|ADD)$/i.test(l)
                    ) || '';

                    if (!name || seenNames.has(name)) continue;

                    const priceMatch = text.match(/₹\s*([1-9][\d,]*)/);
                    if (!priceMatch) continue;

                    // Check this element has an img
                    const img = el.querySelector('img');
                    let imgSrc = '';
                    if (img) {
                        imgSrc = img.currentSrc || img.src || '';
                        if (imgSrc.startsWith('data:')) imgSrc = '';
                    }

                    seenNames.add(name);

                    const description = lines.find(l =>
                        l !== name
                        && !l.startsWith('₹')
                        && !/^[\d.]+$/.test(l)
                        && l.length > 10
                    ) || '';

                    results.push({
                        name,
                        price: '₹' + priceMatch[1],
                        description,
                        image: imgSrc,
                        isVeg: null
                    });
                }
            }

            // ─── Group by category ───
            // Try to find category headers on the page
            const categories = [];
            const catHeaders = document.querySelectorAll(
                'h2, h3, h4, [class*="category"], [class*="Category"], [class*="section-title"]'
            );

            const catNames = [];
            for (const h of catHeaders) {
                const t = (h.innerText || '').trim();
                // Category headers typically have format: "Category Name (count)"
                const catMatch = t.match(/^(.+?)(?:\s*\(\d+\))?$/);
                if (catMatch && catMatch[1].length > 1 && catMatch[1].length < 80
                    && !catMatch[1].includes('₹')
                    && !/^\d+$/.test(catMatch[1])) {
                    catNames.push(catMatch[1].trim());
                }
            }

            // If we found categories, return as-is with "Menu" wrapper
            // (proper category assignment would need spatial analysis)
            if (results.length > 0) {
                return [{ category: "Menu", items: results }];
            }

            return [];

        }""", MAX_ITEMS)

        # ── Basic restaurant info ──
        about = page.evaluate("""() => {
            const info = { address: '', phone: '', hours: '' };

            // Phone number
            try {
                const ph = document.querySelector('a[href^="tel:"]');
                if (ph) info.phone = ph.href.replace('tel:', '');
            } catch(e) {}

            // Address — look for elements near "Direction" or "Address" labels
            try {
                // Try to find address in a more specific way
                const allP = document.querySelectorAll('p, span, div');
                for (const el of allP) {
                    const t = (el.innerText || '').trim();
                    // Address heuristic: contains comma, has reasonable length,
                    // doesn't contain prices, and ideally contains location words
                    if (t.length > 20 && t.length < 250
                        && t.includes(',')
                        && !t.includes('₹')
                        && !t.includes('ADD')
                        && !t.includes('read more')
                        && (t.match(/,/g) || []).length >= 2
                        && !/^\d+\s*ratings?/i.test(t)
                    ) {
                        // Check if it looks like an address (has numbers/road/street/nagar etc.)
                        if (/\d/.test(t) || /road|street|nagar|sector|phase|colony|area|floor|market|block/i.test(t)) {
                            info.address = t;
                            break;
                        }
                    }
                }
            } catch(e) {}

            // Hours
            try {
                const allEls = document.querySelectorAll('p, span, div');
                for (const el of allEls) {
                    const t = (el.innerText || '').trim();
                    if (t.includes('am') && t.includes('pm') && t.length < 100
                        && !t.includes('₹') && /\d/.test(t)) {
                        info.hours = t;
                        break;
                    }
                }
            } catch(e) {}

            return info;
        }""")

        return menu, about

    except Exception as e:
        print(f"    ERROR: {e}")
        return [], {}


# ── MAIN ──────────────────────────────────

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1400, "height": 900}
    )
    page = context.new_page()

    for city_cfg in CITIES:

        print(f"\n{'='*60}")
        print(f"CITY: {city_cfg['city']}  ({city_cfg['input_file']})")
        print(f"{'='*60}")

        try:
            with open(city_cfg["input_file"], "r", encoding="utf-8") as f:
                restaurants = json.load(f)
        except FileNotFoundError:
            print(f"  ⚠ File not found: {city_cfg['input_file']}, skipping...")
            continue

        enriched = []

        for idx, restaurant in enumerate(restaurants):

            link = restaurant.get("link", "")
            name = restaurant.get("name", "?")

            if not link:
                restaurant["menu"]    = []
                restaurant["address"] = ""
                restaurant["phone"]   = ""
                restaurant["hours"]   = ""
                enriched.append(restaurant)
                continue

            full_url = BASE_URL + link if link.startswith("/") else link
            print(f"\n  [{idx+1}/{len(restaurants)}] {name}")
            print(f"  {full_url}")

            menu, about = scrape_menu(page, full_url)

            # Fix image URL — keep only valid Zomato CDN images
            image = restaurant.get("image", "")
            if image and not image.startswith("https://b.zmtcdn"):
                image = ""

            restaurant["image"]   = image
            restaurant["menu"]    = menu
            restaurant["address"] = about.get("address", "")
            restaurant["phone"]   = about.get("phone", "")
            restaurant["hours"]   = about.get("hours", "")

            total_items = sum(len(c["items"]) for c in menu)
            print(f"  → {total_items} dishes scraped")

            if total_items > 0 and menu:
                # Show a sample
                sample = menu[0]["items"][0]
                print(f"    Sample: {sample['name']} | {sample['price']}")
                if sample.get("image"):
                    print(f"    Image: {sample['image'][:80]}...")
                if sample.get("description"):
                    print(f"    Desc: {sample['description'][:80]}...")

            enriched.append(restaurant)

            # Save after every restaurant (crash-safe)
            with open(city_cfg["output_file"], "w", encoding="utf-8") as f:
                json.dump(enriched, f, indent=4, ensure_ascii=False)

            time.sleep(DELAY)

        print(f"\n✓ {len(enriched)} restaurants → {city_cfg['output_file']}")

    browser.close()
    print("\n\nALL CITIES DONE!")