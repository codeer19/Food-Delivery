import json

from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        "https://www.zomato.com/ncr/delivery",
        timeout=60000
    )

    for _ in range(5):

        page.mouse.wheel(0, 5000)

        page.wait_for_timeout(2000)

    restaurants = page.locator("h4")

    data = []

    for i in range(restaurants.count()):

        try:
            name = restaurants.nth(i).inner_text()

            data.append(name)

        except:
            pass

    with open("restaurants.json", "w") as f:

        json.dump(data, f, indent=4)

    print(data)

    browser.close()