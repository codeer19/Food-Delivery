import json
import re
from playwright.sync_api import sync_playwright

# =============================================
# CONFIG — change only these two lines
# for each new city you want to scrape
# =============================================

CITY_NAME = "Patiala"
ZOMATO_URL = "https://www.zomato.com/patiala/delivery"

# Output files:  restaurants_rajpura.json
#                api_responses_rajpura.json
# Your existing ncr files are NEVER touched.

# =============================================

all_restaurants = []

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

    api_data = []

    def handle_response(response):
        try:
            url = response.url
            if "api" in url or "zomato" in url:
                print("\nAPI:", url)
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
                api_data.append({"url": url, "data": data})
        except:
            pass

    page.on("response", handle_response)

    print(f"\nScraping: {ZOMATO_URL}")
    page.goto(ZOMATO_URL, timeout=60000)
    page.wait_for_timeout(5000)

    for i in range(12):
        print(f"\nScrolling {i+1}")
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(2000)

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    cards = page.locator('a[href*="/order"]').filter(has=page.locator("h4"))
    total = cards.count()
    print(f"\nTOTAL RESTAURANTS: {total}")

    for i in range(total):
        try:
            card = cards.nth(i)
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(400)

            name = ""
            try:
                name = card.locator("h4").inner_text()
            except:
                pass

            image = ""
            try:
                image = page.evaluate(
                    """(card) => {
                        const parent = card.parentElement;
                        if (!parent) return "";
                        const img = parent.querySelector('img[alt="Restaurant Card"]');
                        if (img) return img.currentSrc || img.src || "";
                        return "";
                    }""",
                    card.element_handle()
                )
            except:
                pass

            link = ""
            try:
                link = card.get_attribute("href")
            except:
                pass

            text = ""
            try:
                text = card.inner_text()
            except:
                pass

            rating = ""
            try:
                ratings = re.findall(r"\b\d\.\d\b", text)
                if ratings:
                    rating = ratings[0]
            except:
                pass

            delivery_time = ""
            try:
                delivery = re.findall(r"\d+\s*mins?", text)
                if delivery:
                    delivery_time = delivery[0]
            except:
                pass

            price = ""
            try:
                prices = re.findall(r"₹[\d,]+", text)
                if prices:
                    price = prices[0]
            except:
                pass

            cuisines = []
            try:
                for item in text.split("\n"):
                    if "," in item and len(item) < 80:
                        cuisines.append(item)
            except:
                pass

            restaurant = {
                "city": CITY_NAME,
                "name": name,
                "rating": rating,
                "delivery_time": delivery_time,
                "price": price,
                "image": image,
                "link": link,
                "cuisines": cuisines,
                "raw_text": text
            }

            all_restaurants.append(restaurant)
            print("\n--------------------------------")
            print(json.dumps(restaurant, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f"\nERROR on card {i}: {e}")

    # City-specific filenames — old files never overwritten
    restaurants_file = f"restaurants_{CITY_NAME}.json"
    api_file = f"api_responses_{CITY_NAME}.json"

    with open(restaurants_file, "w", encoding="utf-8") as f:
        json.dump(all_restaurants, f, indent=4, ensure_ascii=False)

    with open(api_file, "w", encoding="utf-8") as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)

    print(f"\nDONE")
    print(f"{restaurants_file} saved  ({len(all_restaurants)} restaurants)")
    print(f"{api_file} saved")

    browser.close()