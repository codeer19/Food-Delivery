"""
Looks at the PARENT of each card to find the image element.
"""
from playwright.sync_api import sync_playwright

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
    page.goto("https://www.zomato.com/ncr/delivery", timeout=60000)
    page.wait_for_timeout(5000)

    for _ in range(4):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(2000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    cards = page.locator('a[href*="/order"]').filter(has=page.locator("h4"))
    total = cards.count()
    print(f"Total cards: {total}\n")

    for i in range(min(3, total)):
        card = cards.nth(i)
        card.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        name = card.locator("h4").inner_text()
        print(f"\n{'='*60}")
        print(f"CARD {i}: {name}")
        print(f"{'='*60}")

        # Walk up 1, 2, 3 levels and dump HTML + images each time
        result = page.evaluate("""(el) => {
            const output = [];
            let current = el.parentElement;
            for (let level = 1; level <= 4; level++) {
                if (!current) break;

                // All imgs in this ancestor
                const imgs = Array.from(current.querySelectorAll("img")).map(img => ({
                    src:        img.src,
                    currentSrc: img.currentSrc,
                    dataSrc:    img.getAttribute("data-src"),
                    srcset:     img.getAttribute("srcset"),
                    outerHTML:  img.outerHTML.slice(0, 300)
                }));

                // CSS background on every element in this ancestor
                const bgs = [];
                for (const child of current.querySelectorAll("*")) {
                    const bg = window.getComputedStyle(child).backgroundImage;
                    if (bg && bg !== "none" && bg.includes("http")) {
                        bgs.push({ tag: child.tagName, class: child.className, bg });
                    }
                }

                output.push({
                    level,
                    tag: current.tagName,
                    class: current.className.slice(0, 80),
                    outerHTMLsnippet: current.outerHTML.slice(0, 500),
                    imgs,
                    bgs
                });

                current = current.parentElement;
            }
            return output;
        }""", card.element_handle())

        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))

    browser.close()