import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime
import csv

# This was a time-consuming script and was thus run in multiple batches
# Output file name is to ensure each batch gets its own file name, we will combine these batches using pandas during the cleaning process.
# output_file = 'amazon_laptop_data6.csv'
# failed_urls_file="amazon_failed_urls6.txt"
# For ensuring correct batching while reading URLs from the file.
start_index = 0
end_index = 10

class AmazonScraper:
    def __init__(self,url_file,output_dir="scraped_data"):
        self.url_file = url_file
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_next_filenames(self):
        """Auto-increment the output file name."""
        existing_files = os.listdir(self.output_dir)
        csv_files = [f for f in existing_files if f.startswith("amazon_scraped_data_") and f.endswith(".csv")]
        indices = [
            int(f.replace("amazon_scraped_data_", "").replace(".csv", ""))
            for f in csv_files if f.replace("amazon_scraped_data_", "").replace(".csv", "").isdigit()
        ]
        next_index = max(indices, default=0) + 1
        return (os.path.join(self.output_dir, f"amazon_scraped_data_{next_index}.csv"),os.path.join(self.output_dir, f"amazon_failed_urls_{next_index}.txt"))
    
    def processURLs(self,output_file,failed_urls_file,url_set = set()):


        def scrape_laptop_info(url):

            try:
                # Amazon blocks if same user agent is used. To avoid this, I use user agents in random order to avoid this.
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
                    'Cache-Control': 'max-age=0',
                    'Cookie': 'x-amz-captcha-1=1724354575099927; x-amz-captcha-2=SQkSw6jFuY811RLzQyZV3g==; skin=noskin; ubid-main=132-1074986-8554950; lc-main=en_US; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiMThmMWM5Iiwia2V5IjoiYy9yQnIvVHZWSjhpNGx6VFJPcTRnbXdnY0o5dzFEUzdmZTk0ekZpY2NPUWtQQUd4ZS8rYXdkMjB1OEN4T1VTemVQWFRzYnhjL0FNOGo2UU41ekJVbldSV0ZEd1RheXlHZTBJa3d0NHc3YjBia2hpVWVYT1M5Z2swRGJPWXVSd0t1T3djOTlXVXZUUWVzUWRCWHdWQVBkT3QvUWNpekpmKzZrT3gvL1d6WmorRHNPSC9uckxYclFQY3h1Rm5lRlIwOXpONlBVT1dGdXRmVHR5L2djVzJWT2N2dngramdvUDlTdElJL1AvM0JvZWJSUWQ4WFNncGZkTWlWUDFSSjdpU1NSZlNlS1NvQUY3ZHhHSkNKMEFCUnVGVTNSUG4ycERSWC9DWDYxVlJ2RktwNUEyV3NmUW8wdkM2ZzRwVjZRMHc4OTJTNjhPaDlqV05kRzFENWEzYkZnPT0ifQ==; lwa-context=ac5bd3cbe61418b1832e49014f3e7c05; i18n-prefs=USD; sst-main=Sst1|PQE0QkvG34FUSgYtJgJArAqFCQuDYhebhfYUa6kPdNW0qF73UEfzaoj7vWo70661JUj9iT3NVJnLAGey1Vu62ELv8jhW-Xu0db_RoAYZygvgnTEhBva0BXoHPUE5T_6VaO8u5NZl7h0GhcS1CtEWI9TbdGRtJo3mydkfaSlOjytRkyjG8fNAY7VKlw-5V-P2QshWpQIni6GwbubRdEDioT1wqIuny26Wx9Epv8qUe7csttn_Tj7ZRMKWYcZ-5iqvd2UE_aREMysZ8yw89GOPtDNNkoCn9C0h91sc0xvW2DlbXD4; x-main=1Bj0FFwf0izbYhJyvygPfiMsNhZq1WMa9YhUbAGsMfrLnJLqkJiWWM7NeG38OT0c; at-main=Atza|IwEBIIYyclilis5nOa1AG_ldOLl-m2oFeOJQeaPf9NXc_HaGOWx72F9jH71zdnEKa53MF354Z_1ILc8g17RazrFy_ZzEZ1nYnHMESsi1P19cYkGUgcNcOcyDUdErm1OBVrcVTaRF5DY-b_7VvVinFkcRc0vTYktj7lBjOF7TgM4pzX03kCSElKAtBYHLk6EObfXy8OqJqcrfIxjys_qtYn93XGDDQJRpzotBEyjb0el5nKU54qRurM3elbvp92SkUoWDMrM; sess-at-main="n+5GZmKXcpknPmvMQpYmWwmzzzjYJMs3LP2f6wbzMkU="; session-id=136-6041417-7446714; session-id-apay=136-6041417-7446714; session-id-time=2082787201l; JSESSIONID=99F170CEE959AE4A7A90B363B862ECDA; session-token=WxnfLybBYAHQ8FqN6VBffFF58LA2ClevHEfK1kW9Rka0z/HbRKtTjXi1o3kLQqAV7dJixuYExxpm6nIFMBUo33bAv23Zjt8yD95rLKmyTmYMS8hIQFCvcZypkzDFsput8AFpRnP5YQ074K+R7wq8zEUzfIHxA5dK3kpUx2TeDxD7UNRTOaod5hF30DeTj8ctwT/dKGNDkIyeEcbRSfpB1Zrs26T938YkFd0JiFk4jvk4EXSJvMOblzDPQ9wgLv712Rd/hJYwyxBwvt4L6ArJ6elH2AYWf8vx8EuqAyKOCVIssXOPIPWDjxenCACggACK1Y5Wj/LOm3OgaLu2/rQd/qrocGHvZ9ac41f8ZedQ4+9T0getVKPU2tRKptdP/Zm+; csm-hit=tb:s-B605WMKRTQ0E45CQ0KMS|1727042773231&t:1727042775886&adb:adblk_yes'
                }

                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to fetch the page. Status code: {response.status_code}")
                    return

                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract product information
                title = soup.find('span', {'id': 'productTitle'}).text.strip() if soup.find('span',
                                                                                            {'id': 'productTitle'}) else 'N/A'
                if title == 'N/A':
                    return None
                try:
                    priceWhole = soup.find('span', class_='a-price-whole').text.replace(',', '').strip()
                    priceDecimal = soup.find('span', class_='a-price-fraction').text.strip()

                    price = None

                    if priceWhole != 'N/A' and priceDecimal != 'N/A':
                        price = f"{float(priceWhole) + float(priceDecimal) / 100:.2f}"
                    elif priceWhole == 'N/A' and priceDecimal == 'N/A':
                        price = soup.find('span', class_='a-price').find('span', class_='a-offscreen').text.strip()
                    else:
                        price = 'N/A'

                except AttributeError:
                    price = 'N/A'

                landing_image_src = None
                try:
                    # Find the image tag with id="landingImage"
                    landing_image_tag = soup.find('img', id='landingImage')

                    # Extract the src attribute
                    if landing_image_tag:
                        landing_image_src = landing_image_tag.get('src')
                        print(f"The src URL of the landing image is: {landing_image_src}")
                    else:
                        print("Image tag with id='landingImage' not found.")
                        landing_image_src = None
                except AttributeError:
                    landing_image_src = None

                # Rating
                ratingDiv = soup.find('div', {'id': 'averageCustomerReviews'})
                print(ratingDiv)
                if not ratingDiv:
                    ratingDiv = 'N/A'
                else:
                    ratingDiv = ratingDiv.find('span',class_='a-size-base a-color-base').text.strip()

                # rating = soup.find('span', {'class': 'a-icon-alt'}).text.strip() if soup.find('span', {'class': 'a-icon-alt'}) else 'N/A'

                # Reviews
                reviewsDiv = soup.find('span', {'id': 'acrCustomerReviewText'})
                reviews_text = reviewsDiv.text.strip() if reviewsDiv else None

                # typicalPrice = 'N/A'
                # Look for 'Typical Price' or 'List Price' - This is the usual price without the current deal/discount available.
                # price_labels = soup.find_all('span', class_='a-size-small aok-offscreen')
                # for label in price_labels:
                #     if 'Typical Price'.lower() in label.text.lower() or 'List Price'.lower() in label.text.lower():
                #
                #         if 'Typical Price'.lower() in label.text.lower() or 'List Price'.lower() in label.text.lower():
                #             typicalPriceText = label.text.strip()
                #             if ':' in typicalPriceText:
                #                 typicalPrice = typicalPriceText.split(':')[1].strip()
                #             else:
                #                 typicalPrice = typicalPriceText.split(' ')[-1].strip()
                #         break

                # Stock Data
                # Find the div with id "availability"
                availability_div = soup.find('div', id="availability")
                if availability_div and availability_div.find('span', string="Currently Unavailable"):
                    availability = "No"
                else:
                    availability = "Yes"

                # Extract product details
                details = {}
                detail_bullets = soup.find('table', {'class': 'a-normal a-spacing-micro'})
                if detail_bullets:
                    for tr in detail_bullets.find_all('tr'):
                        key = tr.find('td', {'class': 'a-span3'}).text.strip().replace(':', '').replace('&lrm;', '')
                        value = tr.find('td', {'class': 'a-span9'}).text.strip().replace('\u200e', '').replace(':', '')
                        details[key] = value

                # Extract technical details
                tech_details = {}
                tech_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
                if tech_table:
                    for row in tech_table.find_all('tr'):
                        key = row.find('th').text.strip().replace('&lrm;', '')
                        value = row.find('td').text.strip().replace('\u200e', '').replace(':', '')
                        tech_details[key] = value

                # Extract other technical details
                other_tech_details = {}
                other_tech_table = soup.find('table', {'id': 'productDetails_techSpec_section_2'})
                if other_tech_table:
                    for row in other_tech_table.find_all('tr'):
                        key = row.find('th').text.strip().replace('&lrm;', '')
                        value = row.find('td').text.strip().replace('\u200e', '').replace(':', '')
                        other_tech_details[key] = value

                # Extract Additional details
                additional_details = {}
                additional_details_table = soup.find('table', {'id': 'productDetails_detailBullets_sections1'})
                if additional_details_table:
                    for row in additional_details_table.find_all('tr'):
                        key = row.find('th').text.strip().replace('&lrm;', '')
                        value = row.find('td').text.strip().replace('\u200e', '').replace(':', '')
                        additional_details[key] = value

                # Update - New Amazon UI Structure
                newProdDetails = {}
                newProdDetailsTableList = soup.find_all('table', class_='a-keyvalue prodDetTable')
                if newProdDetailsTableList:
                    for newProdDetailsTable in newProdDetailsTableList:
                        for row in newProdDetailsTable.find_all('tr'):
                            key = row.find('th').text.strip().replace('&lrm;', '')
                            value = row.find('td').text.strip().replace('\u200e', '').replace(':', '')
                            newProdDetails[key] = value

                # Combine all information
                laptop_info = {
                    'Title': title,
                    'Price': price,
                    'Rating': ratingDiv,
                    'Product Details': details,
                    'Technical Details': tech_details,
                    # 'Typical Price': typicalPrice,
                    'Additional Details': additional_details,
                    'Other Technical Details': other_tech_details,
                    'New Product Details': newProdDetails,
                    'URL': url,
                    'Reviews': reviews_text,
                    'In Stock': availability,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'image_url': landing_image_src
                }

                return laptop_info
            except Exception as e:
                print(f"Error extracting specs for {url}: {e}")
                with open(failed_urls_file, "a") as file:
                    file.write(url + "\n")
                return None

        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        new_data = []

        try:
            # Read the file with all Product URLs
            with open('./laptopUrls/amazon_laptop_urls.txt', 'r') as file:
                urls = file.read().splitlines()
            
            file_exists = os.path.exists(output_file)

            # These are headers(product detail keys) received as per multiple iterations.
            # But since the Amazon UI structure is dynamic and kept changing for multiple products/brands/segments, the script is designed to combine new found headers with existing ones.
            existing_headers = ['Additional Details_ASIN', 'Additional Details_Batteries', 'Additional Details_Batteries required', 'Additional Details_Best Sellers Rank', 'Additional Details_Customer Reviews', 'Additional Details_Date First Available', 'Additional Details_Form Factor', 'Additional Details_Graphics Card Ram Size', 'Additional Details_Hard Drive Size', 'Additional Details_Included Components', 'Additional Details_Is Discontinued By Manufacturer', 'Additional Details_Item Weight', 'Additional Details_Item model number', 'Additional Details_Manufacturer', 'Additional Details_Number of Ports', 'Additional Details_Processor Speed', 'Additional Details_Product Dimensions', 'Additional Details_Ram Memory Installed Size', 'Additional Details_Resolution', 'Additional Details_Scanner Resolution', 'Additional Details_Specific instructions for use', 'Additional Details_Standing screen display size', 'Additional Details_Total Usb Ports', 'Additional Details_Warranty Description', 'Other Technical Details_Audio-out Ports (#)', 'Other Technical Details_Batteries', 'Other Technical Details_Brand', 'Other Technical Details_Color', 'Other Technical Details_Computer Memory Type', 'Other Technical Details_Flash Memory Size', 'Other Technical Details_Hard Drive Interface', 'Other Technical Details_Hard Drive Rotational Speed', 'Other Technical Details_Hardware Platform', 'Other Technical Details_Item Dimensions  LxWxH', 'Other Technical Details_Item Weight', 'Other Technical Details_Item model number', 'Other Technical Details_Number of Processors', 'Other Technical Details_Operating System', 'Other Technical Details_Optical Drive Type', 'Other Technical Details_Package Dimensions', 'Other Technical Details_Power Source', 'Other Technical Details_Processor Brand', 'Other Technical Details_Product Dimensions', 'Other Technical Details_Rear Webcam Resolution', 'Other Technical Details_Series', 'Other Technical Details_Voltage', 'Price', 'Product Details_Battery Cell Composition', 'Product Details_Brand', 'Product Details_CPU Model', 'Product Details_CPU Speed', 'Product Details_Cache Size', 'Product Details_Color', 'Product Details_Connectivity Technology', 'Product Details_Display Resolution Maximum', 'Product Details_Display resolution', 'Product Details_Graphics Card Description', 'Product Details_Graphics Coprocessor', 'Product Details_Graphics Processor Manufacturer', 'Product Details_Hard Disk Description', 'Product Details_Hard Disk Size', 'Product Details_Has webcam capability?', 'Product Details_Human Interface Input', 'Product Details_Item Weight', 'Product Details_Lithium Battery Energy Content', 'Product Details_Manufacturer', 'Product Details_Memory Slots Available', 'Product Details_Memory Storage Capacity', 'Product Details_Model Name', 'Product Details_Operating System', 'Product Details_Processor Count', 'Product Details_RAM Memory Technology', 'Product Details_RAM Type', 'Product Details_Ram Memory Installed Size', 'Product Details_Resolution', 'Product Details_Screen Size', 'Product Details_Special Feature', 'Product Details_Specific Uses For Product', 'Product Details_Total USB Ports', 'Product Details_Wireless Communication Technology', 'Rating', 'Technical Details_ASIN', 'Technical Details_Average Battery Life (in hours)', 'Technical Details_Batteries', 'Technical Details_Card Description', 'Technical Details_Chipset Brand', 'Technical Details_Country of Origin', 'Technical Details_Date First Available', 'Technical Details_Graphics Card Ram Size', 'Technical Details_Graphics Coprocessor', 'Technical Details_Hard Drive', 'Technical Details_Item Weight', 'Technical Details_Item model number', 'Technical Details_Manufacturer', 'Technical Details_Max Screen Resolution', 'Technical Details_Memory Speed', 'Technical Details_National Stock Number', 'Technical Details_Number of USB 2.0 Ports', 'Technical Details_Number of USB 3.0 Ports', 'Technical Details_Processor', 'Technical Details_Product Dimensions', 'Technical Details_RAM', 'Technical Details_Screen Resolution', 'Technical Details_Standing screen display size', 'Technical Details_Wireless Type', 'Title', 'Typical Price', 'URL','New Product Details_Keyboard Layout', 'New Product Details_Control Method', 'New Product Details_Keyboard Description', 'New Product Details_Human-Interface Input', 'New Product Details_Total Thunderbolt Ports', 'New Product Details_Total Number of HDMI Ports', 'New Product Details_Number of Ports', 'New Product Details_Number of Ethernet Ports', 'New Product Details_Total Usb Ports', 'New Product Details_Ram Memory Maximum Size', 'New Product Details_RAM Memory Slot Total Count', 'New Product Details_RAM Type', 'New Product Details_RAM Memory Technology', 'New Product Details_RAM Memory Installed', 'New Product Details_Bluetooth Version', 'New Product Details_Bluetooth support?', 'New Product Details_Wi-Fi Generation', 'New Product Details_Wireless Compability', 'New Product Details_Connectivity Technology', 'New Product Details_Wireless Technology', 'New Product Details_Graphics Ram Type', 'New Product Details_Item Dimensions L x W x Thickness', 'New Product Details_Chipset Type', 'New Product Details_Optical Storage Device', 'New Product Details_Power Device', 'New Product Details_Number of Drivers', 'New Product Details_Video Output', 'New Product Details_Virtual Reality Ready', 'New Product Details_Specific Uses For Product', 'New Product Details_Webcam Capability', 'New Product Details_Automatic Backup Software Included', 'New Product Details_Form Factor', 'New Product Details_Hard Disk Interface', 'New Product Details_Camera Description', 'New Product Details_Color', 'New Product Details_Hard-Drive Size', 'New Product Details_Operating System', 'New Product Details_Additional Features', 'New Product Details_Graphics Description', 'New Product Details_Graphics Coprocessor', 'New Product Details_Hard Disk Description', 'New Product Details_Video Processor', 'New Product Details_Series Number', 'New Product Details_UPC', 'New Product Details_Customer Reviews', 'New Product Details_Best Sellers Rank', 'New Product Details_ASIN', 'New Product Details_Model Number', 'New Product Details_Included Components', 'New Product Details_Manufacturer', 'New Product Details_Brand Name', 'New Product Details_Model Name', 'New Product Details_Model Year', 'New Product Details_CPU Model Speed Maximum', 'New Product Details_CPU Model Generation', 'New Product Details_Processor Count', 'New Product Details_Processor Brand', 'New Product Details_CPU Model Number', 'New Product Details_Processor Series', 'New Product Details_Processor Speed', 'New Product Details_Battery Average Life Standby', 'New Product Details_Battery Average Life', 'New Product Details_Battery Cell Type', 'New Product Details_Has Color Screen', 'New Product Details_Screen Finish', 'New Product Details_Supported Monitor Maximum Quantity', 'New Product Details_Display Type', 'New Product Details_Display Resolution Maximum', 'New Product Details_Display Technology', 'New Product Details_Screen Size', 'New Product Details_Resolution', 'New Product Details_Native Resolution', 'New Product Details_Audio features', 'New Product Details_Audio Recording', 'New Product Details_Speaker Description', 'New Product Details_Microphone Form Factor', 'New Product Details_Audio Output Type']

            all_headers = set(existing_headers)

            # Process all URLs first to collect all possible headers and add data to an array.
            # [start_index: end_index + 1], start = start_index
            for index, url in enumerate(urls):
                if url in url_set:
                    continue
                url_set.add(url)
                print(f"Processing URL # {index} : {url}")
                info = scrape_laptop_info(url)
                if info:
                    flat_info = flatten_dict(info)
                    all_headers.update(flat_info.keys())
                    new_data.append(flat_info)
                else:
                    print(f"No data found for URL # {index} - {url}")

                time.sleep(random.uniform(0, 2))
            
            
        except FileNotFoundError:
            print("No laptop_urls.txt file found.")
            return
        finally:
            # If new headers were found or file doesn't exist, write/update the header row
            if not file_exists or new_data:
                mode = 'w' if not file_exists else 'r+'
                with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
                    # Convert all_headers to a list and sort it for consistency
                    all_headers = sorted(list(all_headers))
                    writer = csv.DictWriter(csvfile, fieldnames=all_headers)
            
                    if not file_exists:
                        writer.writeheader()
                    
                    if file_exists:
                        csvfile.seek(0, 2)
                    
                    for row in new_data:
                        
                        complete_row = {header: row.get(header, '') for header in all_headers}
                        
                        writer.writerow(complete_row)

    def run(self):
        output_file,failed_urls_file = self.get_next_filenames()
        self.processURLs(output_file,failed_urls_file)


