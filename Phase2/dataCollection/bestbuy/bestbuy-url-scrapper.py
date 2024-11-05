import requests
from bs4 import BeautifulSoup
import time
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

all_laptop_urls = set()

# Function to scrape a single page
def scrape_page(url, existing_urls):
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # product_link_htags = soup.find_all('h4', class_='sku-title')
        # print(product_link_htags)
        product_links = [a['href'] for h4 in soup.find_all("h4", class_="sku-title") for a in h4.find_all("a")]
        # laptop_urls = [link.get('href') for link in product_links if link.get('href')]
        laptop_urls = ['https://www.bestbuy.com' + url if url.startswith('/') else url for url in product_links]
        # Filter out URLs that are already in existing_urls
        new_laptop_urls = [url for url in laptop_urls if url not in existing_urls]
        
        return new_laptop_urls
    else:
        print(f"Failed to download page {page_number}. Status code: {response.status_code}")
        return []

# Loop through 69 pages
for page_number in range(1, 72):
    print(f"Scraping page {page_number}...")
    url = f'https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat138500050001&cp={page_number}&id=pcat17071&iht=n&ks=960&list=y&sc=Global&st=categoryid%24pcmcat138500050001&type=page&usc=All%20Categories'
    page_urls = scrape_page(url, all_laptop_urls)
    
    # Check if the page has less than 20 URLs.
    # Sometimes due to ads and different product categories - AMmazon displays products in the range of 20-24 URLs
    # This check is added to ensure we scrape more than 20 URLs per pagination
    if len(page_urls) < 16:
        print(f"Warning: Page {page_number} has less than 20 URLs.")
        print(f"URL: {url}")
        # Added to manually check what went wrong with the URL, why it has less than required URLs
        input("Press Enter to continue...")
    
    # Add URLs to the set
    all_laptop_urls.update(page_urls)
    
    # Append URLs to a file - we will iterate and scrape these again to fetch product specific details.
    with open('bestbuy_laptop_urls.txt', 'a') as file:
        for url in page_urls:
            file.write(url + '\n')
    
    # Add a delay between requests to avoid overwhelming the server and getting blocked
    time.sleep(random.uniform(1, 5))

print(f"Scraped a total of {len(all_laptop_urls)} unique laptop URLs.")
print(f"All URLs have been appended to laptop_urls.txt")


