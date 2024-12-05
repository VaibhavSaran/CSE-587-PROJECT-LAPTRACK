from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import csv
from datetime import datetime
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Set up WebDriver options (optional: to run headless or set other options)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start browser maximized

driver_path = '/Users/shauryamathur/Documents/Projects/AutomateBrowserClicks/seleniumPractice/chromedriver-mac-arm64/chromedriver'  # Update with your actual path
all_specifications = []
all_keys = set()  # Set to track all unique keys across URLs
all_headers = set()
url_set = set()
def find_specifications_button(driver):
    try:
        # Try finding the button with the class 'show-full-specs-btn'
        specs_button = driver.find_element("xpath", "//button[contains(@class, 'QqFHMw _4FgsLt')]")
        print("Button with class 'QqFHMw _4FgsLt' found.")
        return specs_button  # Return the button if found
    except NoSuchElementException:
        print("Button with class 'show-full-specs-btn' not found. Trying the next option.")


    # If neither button is found, raise an exception
    raise NoSuchElementException(
        "Neither 'show-full-specs-btn' nor button with nested <h3> tag containing 'Specifications' was found.")

# Function to extract specifications from a single URL
def extract_specs(driver,url):
    # Enable Network domain and set headers
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
    driver.get(url)
    try:
        # Get the page source after the pop-up appears
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Initialize a dictionary to store the specifications for this URL
        specifications = {"url": url,"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  # Include the URL as the first column

        #Get Product model,title and Price and Reviews
        # Find the <div> with class "sku-title"
        sku_title_div = soup.find('span', class_='VU-ZEz')

        # Find the image tag with class="primary-image"
        primary_image_tag = soup.find('img', class_='DByuf4 IZexXJ jLEJ7H')
        # Extract the src attribute
        if primary_image_tag:
            primary_image_src = primary_image_tag.get('src')
            specifications['image_src'] = primary_image_src
            print(f"The src URL of the primary image is: {primary_image_src}")
        else:
            print("Image tag with class='primary-image' not found.")
            specifications['image_src'] = None

        # Extract the text from the <h1> tag within this <div>
        if sku_title_div:
            product_title = sku_title_div.text.strip()
            specifications['product_title'] = product_title
            print(product_title)  # Output the product title
        else:
            print("No <span> with class 'VU-ZEz' found.")

        rating_average_span = soup.find('div', class_='XQDdHH')

        # Extract and print the text
        if rating_average_span:
            span_text = rating_average_span.text.strip()  # Get the text and strip extra whitespace
            specifications['rating_average'] = span_text
            print(span_text)  # Output the text from the <span>
        else:
            print("No <span> found with the specified classes.")

        review_count_span = soup.find('span', class_='Wphh3N')

        # Extract and print the text
        if review_count_span:
            span_text = review_count_span.text.strip()  # Get the text and strip extra whitespace
            specifications['review_count'] = span_text
            print(span_text)  # Output the text from the <span>
        else:
            print("No <span> found with the specified classes.")


        outOfStock_div = soup.find('div',class_='Z8JjpR')
        notifymeButton = soup.find('button',class_='QqFHMw AMnSvF v6sqKe')

        if outOfStock_div or notifymeButton:
            specifications['in_stock'] = "No"
        else:
            specifications['in_stock'] = "Yes"


        # Find the element with data-testid containing "customer-price"
        price_elements = soup.find('div',class_=['Nx9bqj', 'CxhGGd', 'yKS4la'])

        # Extract and print the text from found elements
        for price_element in price_elements:
            price_text = price_element.text.strip()  # Get the text and strip extra whitespace
            specifications['price'] = price_text
            break
            # print(price_text)

        specs_button = find_specifications_button(driver)
        # Click the 'Show Full Specs' button
        # specs_button = driver.find_element("xpath", "//button[contains(@class, 'show-full-specs-btn')]")
        specs_button.click()

        # Wait for the pop-up to load
        time.sleep(1)

        # Get the page source after the pop-up appears
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract data from the specs section
        # specs_section = soup.find('div', class_='overflow-scroll-wrapper v-scrolling-vertical flex-grow-1')
        # print('SpecsSection',specs_section)

        # Locate each <li> element within the section
        specs_list = soup.find_all('div', class_='GNDEQ-')
        # print(specs_list)
        for item in specs_list:
            # Get the category name from the <h4> tag
            category_tag = item.find('div',class_='_4BJ2V+')
            if category_tag:
                category = category_tag.text.strip().lower().replace(" ", "_")

                # Initialize a sub-dictionary for this category
                category_data = {}

                # Find the table by its class name
                table = item.find('table', class_='_0ZhAN9')

                # Loop through all rows in the table
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:  # Ensure there are at least two columns
                        key = cells[0].get_text(strip=True).lower().replace(" ", "_")   # Get text from the first cell (key)
                        full_key = f"{category}.{key}"  # Format as category.key
                        value = cells[1].get_text(strip=True)  # Get text from the second cell (value)
                        specifications[full_key] = value
                        all_keys.add(full_key)  # Track all unique keys

        # Add this URL's specifications to the list
        all_specifications.append(specifications)
        all_headers.update(specifications.keys())
    except Exception as e:
        print(f"Error extracting specs for {url}: {e}")
        with open(failed_urls_file, "a") as file:
            file.write(url + "\n")
        return None


# Set up Selenium using ChromeDriverManager
driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

# Base URL for the search page
base_url = "https://www.bestbuy.com/site/searchpage.jsp?st=laptop&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp={}&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"

# Initialize an empty list to store specifications
specs_data = []
output_file = 'flipkart_laptop_data5.csv'
failed_urls_file="flipkart_failed_urls5.txt"
def scrape_urls():
    # new_data = []
    try:
        with open('flipkart_laptop_urls.txt', 'r') as file:
            urls = file.read().splitlines()
        file_exists = os.path.exists(output_file)
        # print(urls[:10])
        for ix,url in enumerate(urls):
            print(f'Extracting URL #{ix+1} of {len(urls)}')
            url = url.replace('https://www.flipkart.com//','https://www.flipkart.com/')
            if url in url_set:
                continue
            url_set.add(url)
            extract_specs(driver,url)

    except FileNotFoundError:
        print("No laptop_urls.txt file found.")
    finally:
        print('Headers',all_headers)
        all_keys_list = list(all_keys)  # Convert set to list for consistent ordering

        # Add 'url' as the first column
        all_keys_list.insert(0, "url")

        with open(output_file, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=all_headers)
            writer.writeheader()

            # Write each URL's specifications as a row in the CSV
            for specs in all_specifications:
                # Use .get() to fill in missing keys with empty values for each row
                row = {key: specs.get(key, "") for key in all_headers}
                writer.writerow(row)
        # Close the browser
        driver.quit()
scrape_urls()

