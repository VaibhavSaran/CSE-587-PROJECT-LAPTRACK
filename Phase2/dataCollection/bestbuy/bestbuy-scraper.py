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
from webdriver_manager.chrome import ChromeDriverManager

output_file = 'bestbuy_laptop_data4.csv'
failed_urls_file="bestbuy_failed_urls4.txt"

# Set up WebDriver options (optional: to run headless or set other options)
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")  # Start browser maximized

# driver_path = '/Users/shauryamathur/Documents/Projects/AutomateBrowserClicks/seleniumPractice/chromedriver-mac-arm64/chromedriver'  # Update with your actual path
all_specifications = []
all_keys = set()  # Set to track all unique keys across URLs
all_headers = set()
url_set = set()
def find_specifications_button(driver):
    try:
        # Try finding the button with the class 'show-full-specs-btn'
        specs_button = driver.find_element("xpath", "//button[contains(@class, 'show-full-specs-btn')]")
        print("Button with class 'show-full-specs-btn' found.")
        return specs_button  # Return the button if found
    except NoSuchElementException:
        print("Button with class 'show-full-specs-btn' not found. Trying the next option.")

    try:
        # Try finding the button with the nested <h3> containing 'Specifications'
        specs_button_with_h3 = driver.find_element("xpath", "//button[.//h3[text()='Specifications']]")
        print("Button with nested <h3> tag containing 'Specifications' found.")
        return specs_button_with_h3  # Return the button if found
    except NoSuchElementException:
        print("Button with nested <h3> tag containing 'Specifications' not found.")

    # If neither button is found, raise an exception
    raise NoSuchElementException(
        "Neither 'show-full-specs-btn' nor button with nested <h3> tag containing 'Specifications' was found.")

# Function to extract specifications from a single URL
def extract_specs(url):
    print(url)
    driver.get(url)
    try:
        # Get the page source after the pop-up appears
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Initialize a dictionary to store the specifications for this URL
        specifications = {"url": url,"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  # Include the URL as the first column

        #Get Product model,title and Price and Reviews
        # Find the <div> with class "sku-title"
        sku_title_div = soup.find('div', class_='sku-title')

        # Find the image tag with class="primary-image"
        primary_image_tag = soup.find('img', class_='primary-image')
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
            h1_tag = sku_title_div.find('h1')  # Find the <h1> tag within the div
            if h1_tag:
                product_title = h1_tag.text.strip()  # Get the text and strip any extra whitespace
                specifications['product_title'] = product_title
                print(product_title)  # Output the product title
            else:
                print("No <h1> tag found within the <div class='sku-title'>.")
        else:
            print("No <div> with class 'sku-title' found.")

        rating_average_span = soup.find('span', class_='ugc-c-review-average')

        # Extract and print the text
        if rating_average_span:
            span_text = rating_average_span.text.strip()  # Get the text and strip extra whitespace
            specifications['rating_average'] = span_text
            print(span_text)  # Output the text from the <span>
        else:
            print("No <span> found with the specified classes.")

        review_count_span = soup.find('span', class_='c-reviews order-2')

        # Extract and print the text
        if review_count_span:
            span_text = review_count_span.text.strip()  # Get the text and strip extra whitespace
            specifications['review_count'] = span_text
            print(span_text)  # Output the text from the <span>
        else:
            print("No <span> found with the specified classes.")

        # Find all <div> elements whose IDs start with "fulfillment-add-to-cart-button"
        divs = soup.find_all('div', id=lambda x: x and x.startswith('fulfillment-add-to-cart-button'))

        for div in divs:
            # Find the nested button within the div
            button = div.find('button')
            if button:
                button_text = button.text.strip().lower()  # Get the button text and strip whitespace
                print('Button Text',button_text)
                # Classify stock status based on button text
                if button_text == "Sold out".lower():
                    specifications['in_stock'] = "No"
                else:
                    specifications['in_stock'] = "yes"

        # Find the element with data-testid containing "customer-price"
        price_elements = soup.find_all(attrs={"data-testid": lambda x: x and "customer-price" in x})

        # Extract and print the text from found elements
        for price_element in price_elements:
            price_text = price_element.text.strip()  # Get the text and strip extra whitespace
            specifications['price'] = price_text
            # print(price_text)

        specs_button = find_specifications_button(driver)
        # Click the 'Show Full Specs' button
        # specs_button = driver.find_element("xpath", "//button[contains(@class, 'show-full-specs-btn')]")
        specs_button.click()

        # Wait for the pop-up to load
        time.sleep(2)

        # Get the page source after the pop-up appears
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract data from the specs section
        specs_section = soup.find('div', class_='overflow-scroll-wrapper v-scrolling-vertical flex-grow-1')
        # print('SpecsSection',specs_section)


        if specs_section:
            # Locate each <li> element within the section
            specs_list = specs_section.find_all('li')
            # print(specs_list)
            for item in specs_list:
                # Get the category name from the <h4> tag
                category_tag = item.find(['h4', 'h3'])
                if category_tag:
                    category = category_tag.text.strip().lower().replace(" ", "_")

                    # Initialize a sub-dictionary for this category
                    category_data = {}

                    # Find all key-value pairs within <div> tags in this <li>
                    key_value_pairs = item.find_all('div', recursive=False)
                    for i in range(0, len(key_value_pairs)):
                        # print(key_value_pairs[i])
                        nested_divs = key_value_pairs[i].find_all('div', recursive=False)
                        if len(nested_divs) >= 2:  # Ensure there are at least two sibling divs
                            key = nested_divs[0].text.strip().lower().replace(" ", "_")  # First div as key
                            value = nested_divs[1].text.strip()  # Second div as value
                            full_key = f"{category}.{key}"  # Format as category.key
                            specifications[full_key] = value
                            all_keys.add(full_key)  # Track all unique keys
                            # print('ALL Keys', all_keys)


            # Add this URL's specifications to the list
            all_specifications.append(specifications)
            all_headers.update(specifications.keys())

    except Exception as e:
        print(f"Error extracting specs for {url}: {e}")
        with open(failed_urls_file, "a") as file:
            file.write(url + "\n")
        return None


# Set up Selenium using ChromeDriverManager
# driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (necessary in Docker)
chrome_options.add_argument("window-size=1200x600")  # Set window size (optional)

# Set up the ChromeDriver using ChromeDriverManager
service = Service(ChromeDriverManager().install())

# Initialize the WebDriver with the options and service
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL for the search page
base_url = "https://www.bestbuy.com/site/searchpage.jsp?st=laptop&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp={}&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"

# Initialize an empty list to store specifications
specs_data = []

def scrape_urls():
    # new_data = []
    try:
        with open('bestbuy_laptop_urls.txt', 'r') as file:
            urls = file.read().splitlines()
        file_exists = os.path.exists(output_file)
        # print(urls[:10])
        for ix,url in enumerate(urls):
            print(f'Extracting URL #{ix+1} of {len(urls)}')
            if url in url_set:
                continue
            url_set.add(url)
            extract_specs(url)

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

