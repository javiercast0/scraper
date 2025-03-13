from playwright.sync_api import sync_playwright
import time
from plyer import notification

def scraping(browser, url, priceNotif, results, category):
    print(f"***********{category}***********")
    print("Creating a new tab...")
    page = browser.new_page()

    # Go to URL
    page.goto(url)
    
    # Names
    page.wait_for_selector(".ItemCard__title.my-1")
    name_elements = page.query_selector_all(".ItemCard__title.my-1")
    names = [element.inner_text() for element in name_elements]

    # Prices
    page.wait_for_selector(".ItemCard__price.ItemCard__price--bold")
    price_elements = page.query_selector_all(".ItemCard__price.ItemCard__price--bold")
    prices = [element.inner_text() for element in price_elements]
    
    # URLs
    page.wait_for_selector(".ItemCardList__item")
    url_elements = page.query_selector_all(".ItemCardList__item")
    urlsItems = [element.get_attribute("href") for element in url_elements if element]
    
    # Check if they have the badge for "Reserved" or "Sold"
    badge_elements = page.query_selector_all(".ItemCard__badge.d-flex.align-self-start.ml-2.mt-2")
    badges = [element.inner_text() for element in badge_elements]

    # Print name, price and URL together
    for name, price, urlItem in zip(names, prices, urlsItems):
        # Check if the item has a badge
        badge = page.query_selector(f'a[href="{urlItem}"] .ItemCard__badge.d-flex.align-self-start.ml-2.mt-2')
        # Only process items without the badge and not in the category i want.
        if badge is None and category != "Juegos Switch":
            print(f"{name} - {price} - {category}\n {urlItem}")
            print(f"-----------------------------------------------")

            # Check if the price is below the notification threshold
            if float(price.replace('€', '').replace(',', '.')) <= priceNotif:
                results.append((name, price, urlItem, category))
                notification.notify(
                    title="CHECK!!",
                    message=f"{name}: {price} - {category}\n {urlItem}",
                    timeout=10
                )
                
    page.close()

with sync_playwright() as p:
    try:
        # Open Browser
        print("Launching the browser...")
        browser = p.chromium.launch(headless=True)
        
        results = []
        
        while True:
            # Mario Kart 8
            scraping(browser, "https://es.wallapop.com/app/search?filters_source=search_box&keywords=MARIO%20KART%208&category_ids=24200&latitude=36.8596583&longitude=-2.4411745&time_filter=today&order_by=newest", 25, results, "MK8")
            # Zelda
            scraping(browser, "https://es.wallapop.com/app/search?filters_source=search_box&keywords=Zelda&category_ids=24200&latitude=36.8596583&longitude=-2.4411745&time_filter=today&order_by=newest", 25, results, "Zelda")
            # Nintendo Switch
            scraping(browser, "https://es.wallapop.com/app/search?filters_source=search_box&keywords=Nintendo%20Switch&category_ids=24200&latitude=36.8596583&longitude=-2.4411745&time_filter=today&order_by=newest", 140, results, "Nintendo Switch")
            # Juegos Switch
            scraping(browser, "https://es.wallapop.com/app/search?filters_source=side_bar_filters&keywords=juegos%20switch&latitude=36.8596583&longitude=-2.4411745&order_by=newest&time_filter=today", 99999, results, "Juegos Switch")
            
            # Print all results that meet the condition
            print("\n*** Items that meet the price condition ***")
            for name, price, urlItem, category in results:
                print(f"{name} - {price} - {category}\n {urlItem}")
                print(f"-----------------------------------------------")
            
            # Clear results for the next iteration
            results.clear()
            
            # Wait 20 minutes before the next scrape
            print("Waiting 20 minutes before the next scrape...")        
            time.sleep(1200)
            # Show notification for reload
            notification.notify(
                title="Reload...",
                message="Just reloading the scraping...",
                timeout=3
            )
    
    except Exception as e:
        print(f"An error occurred: {e}")
        # Show notification for error
        notification.notify(
            title="Scraping Error",
            message=f"An error occurred: {e}",
            timeout=10
        )
    
    finally:
        # Ensure the browser is closed
        browser.close()