"""
test_single.py — Quick test: scrape the menu of ONE restaurant
to verify the scraper is working correctly.
"""

import json
from playwright.sync_api import sync_playwright

TEST_URL = "https://www.zomato.com/ncr/dominos-pizza-4-connaught-place-new-delhi/order"

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

    print(f"Navigating to: {TEST_URL}")
    page.goto(TEST_URL, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Slow scroll to lazy-load all images
    print("Scrolling to load all images...")
    prev_height = 0
    stall_count = 0
    while stall_count < 3:
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(300)
        current_height = page.evaluate("document.documentElement.scrollHeight")
        if current_height == prev_height:
            stall_count += 1
        else:
            stall_count = 0
            prev_height = current_height

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1500)

    # ── Extract menu items ──
    print("Extracting menu items...")
    items = page.evaluate("""() => {

        const results = [];
        const seenNames = new Set();

        // Find all images from Zomato's dish photo CDN
        const allImgs = Array.from(document.querySelectorAll('img'));
        const dishImgs = allImgs.filter(img => {
            const src = img.currentSrc || img.src || '';
            return src.includes('zmtcdn.com/data/dish_photos');
        });

        console.log('Found ' + dishImgs.length + ' dish images');

        for (const img of dishImgs) {
            if (results.length >= 50) break;

            const imgSrc = img.currentSrc || img.src || '';
            if (!imgSrc || imgSrc.startsWith('data:')) continue;

            // The alt attribute IS the dish name on current Zomato
            let name = (img.alt || '').trim();

            // Walk up to find the card container with price
            let card = img.parentElement;
            for (let i = 0; i < 8; i++) {
                if (!card) break;
                const t = (card.innerText || '').trim();
                if (/₹[1-9]/.test(t) && t.length > 20) break;
                card = card.parentElement;
            }
            if (!card) continue;

            const text = (card.innerText || '').trim();
            if (!text) continue;

            // Extract price
            const priceMatch = text.match(/₹\\s*([1-9][\\d,]*)/);
            if (!priceMatch) continue;
            const price = '₹' + priceMatch[1];

            // If alt didn't give us a name, get first meaningful line
            if (!name || name === 'dish' || name === 'Dish') {
                const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                name = lines.find(l =>
                    l.length > 1
                    && l.length < 120
                    && !l.startsWith('₹')
                    && !/^[\\d.]+$/.test(l)
                    && !/^(Bestseller|Must Try|NEW)$/i.test(l)
                    && !/^\\d+\\s*ratings?$/i.test(l)
                ) || '';
            }

            if (!name || name.length > 120 || seenNames.has(name)) continue;
            seenNames.add(name);

            // Description
            const textLines = text.split('\\n').map(l => l.trim()).filter(Boolean);
            const description = textLines.find(l =>
                l !== name
                && !l.startsWith('₹')
                && !/^[\\d.]+$/.test(l)
                && !/^\\d+\\s*ratings?$/i.test(l)
                && !/^(Bestseller|Must Try|NEW|Customisable|ADD)$/i.test(l)
                && l.length > 10
                && l.length < 500
            ) || '';

            results.push({ name, price, description, image: imgSrc });
        }

        return results;
    }""")

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(items)} menu items found")
    print(f"{'='*60}")

    for i, item in enumerate(items[:10]):
        print(f"\n  [{i+1}] {item['name']}")
        print(f"      Price: {item['price']}")
        print(f"      Image: {item['image'][:80]}..." if item.get('image') else "      Image: (none)")
        print(f"      Desc:  {item['description'][:80]}..." if item.get('description') else "      Desc:  (none)")

    # Save results
    with open("test_menu_output.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    print(f"\nFull results saved to test_menu_output.json")

    browser.close()
