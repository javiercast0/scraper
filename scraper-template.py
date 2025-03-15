from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import time
from plyer import notification

app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify(message="¡Hola, mundo!")

if __name__ == '__main__':
    app.run(debug=True)

def scraping(browser, url, priceNotif, priceMet, seen_items):
    print("Creating a new tab...")
    page = browser.new_page()

    try:
        # Go to URL
        page.goto(url)
        
        # HTML Classes for our items, normally the web will have atleast these 3 classes, name of product, price and url
        # You can add more classes if you want to scrape more information, for example, an image of the product.
        # use the Inspect Code of your browser to get the classes of the elements you want to scrape.
        # In this example they are made for wallapop.
        nameClass = ".ItemCard__title.my-1"
        priceClass = ".ItemCard__price.ItemCard__price--bold"
        urlClass = ".ItemCardList__item"
        
        # Names
        page.wait_for_selector(nameClass)
        name_elements = page.query_selector_all(nameClass)
        names = [element.inner_text() for element in name_elements]

        # Prices
        page.wait_for_selector(priceClass)
        price_elements = page.query_selector_all(priceClass)
        prices = [element.inner_text() for element in price_elements]
        
        # URLs
        page.wait_for_selector(urlClass)
        url_elements = page.query_selector_all(urlClass)
        urlsItems = [element.get_attribute("href") for element in url_elements if element]
        
        
        # Print name, price and URL together, only if they are new (for consecutive scrapes)
        for name, price, urlItem in zip(names, prices, urlsItems):
            item = (name, price, urlItem)
            if item not in seen_items:
                seen_items.add(item)
                print(f"{name} - {price} - {urlItem}")
                print(f"-----------------------------------------------")

                # Check if the price is below the notification threshold, change the currency if needed!
                try:
                    price_value = float(price.replace('€', '').replace(',', '.'))
                    if price_value <= priceNotif:
                        priceMet.append(item)
                        notification.notify(
                            title="CHECK!!",
                            message=f"{name}: {price} - \n {urlItem}",
                            timeout=3
                        )
                except ValueError as e:
                    print(f"Error converting price: {e}")
    
    finally:
        time.sleep(5)
        page.close()

with sync_playwright() as p:
    try:
        # Open Browser
        print("Launching the browser...")
        browser = p.chromium.launch(headless=True)
        
        # Create an empty list to store the items that meet the price condition and a set for seen items
        priceMet = []
        seen_items = set()
        
        while True:
            # Replace "https://example.com" with the actual URL of the done search, the number is the price threshold for the notification and the list
            # of items that meet the condition. You can add more URLs just by using the same function with different parameters.
            scraping(browser, "https://example.com", 25, priceMet, seen_items)
            
            # Print all results that meet the condition
            print("\n*** Items that meet the price condition ***")
            for name, price, urlItem in priceMet:
                print(f"{name} - {price} \n {urlItem}")
                print(f"-----------------------------------------------")
            
            # Wait 20 minutes before the next scrape
            print("Waiting 20 minutes before the next scrape...")
            time.sleep(1200)    
            notification.notify(
                title="Reload...",
                message="Just reloading the scraping...",
                timeout=3
            )
    
    except Exception as e:
        print(f"An error occurred: {e}")
        notification.notify(
            title="Scraping Error",
            message=f"An error occurred: {e}",
            timeout=10
        )
    
    finally:
        # Ensure the browser is closed
        if 'browser' in locals():
            browser.close()