import pandas as pd
import numpy as np
import re
import os

class FlipkartCleaner:
    def __init__(self,input_dir="./etl/scraped_data",output_dir="./etl/clean_data"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_next_filenames(self):
        """Auto-increment the output file name."""
        existing_files = os.listdir("./etl/scraped_data")
        csv_files = [f for f in existing_files if f.startswith("flipkart_scraped_data_") and f.endswith(".csv")]
        indices = [
            int(f.replace("flipkart_scraped_data_", "").replace(".csv", ""))
            for f in csv_files if f.replace("flipkart_scraped_data_", "").replace(".csv", "").isdigit()
        ]
        latest_index = max(indices, default=1)
        return (os.path.join(self.input_dir, f"flipkart_scraped_data_{latest_index}.csv"),os.path.join(self.output_dir, f"flipkart_cleaned_data_{latest_index}.csv"))
    
    def cleanDataAndExport(self):
        dataFilePath,cleanedFilePath = self.get_next_filenames()
        df_raw = pd.read_csv(dataFilePath)

        potential_brands = ['HP','ASUS','Lenovo','DELL','MSI','Avita','Acer','Infinix','Apple','SAMSUNG','MICROSOFT','Ultimus''GIGABYTE','Colorful','ZEBRONICS','CHUWI','Thomson','realme','WINGS','AXL','ALIENWARE','Vaio','Primebook','walker']
        # Create a regex pattern that matches any of the brands
        pattern = r'\b(' + '|'.join(re.escape(brand) for brand in potential_brands) + r')\b'
        df_raw = df_raw.copy()
        # Use regex to find and set the brand name if it exists in the 'product_title'
        df_raw['brand'] = df_raw['product_title'].apply(lambda title: re.search(pattern, title).group(0) if re.search(pattern, title) else None)

        # For storage capacity
        storageCapacityColumns = ['processor_and_memory_features.emmc_storage_capacity','processor_and_memory_features.expandable_ssd_capacity','processor_and_memory_features.hdd_capacity','processor_and_memory_features.ssd_capacity','processor_and_memory_features.ufs_storage_capacity']
        df_raw = df_raw.copy()
        df_raw['Storage_Capacity'] = df_raw[storageCapacityColumns].bfill(axis=1).iloc[:,0]

        # Replace null values in 'general.model_name' with values from 'general.series'
        df_raw['general.model_name'] = df_raw['general.model_name'].fillna(df_raw['general.series'])

        #Add Source
        df_raw = df_raw.copy()
        df_raw['Source'] = 'Flipkart'

        # Renaming columns to ensure uniformity
        renaming_dict = {'brand': 'Brand', 
                        'general.model_name': 'Laptop_Model_Name', 
                        'general.model_number': 'Laptop_Model_Number', 
                        'processor_and_memory_features.processor_brand': 'Processor_Brand', 
                        'processor_and_memory_features.processor_name': 'Processor_Model', 
                        'processor_and_memory_features.storage_type': 'Storage_Type', 
                        'Storage_Capacity': 'Storage_Capacity', 
                        'operating_system.operating_system': 'Operating_System', 
                        'processor_and_memory_features.ram': 'RAM', 
                        'display_and_audio_features.screen_size': 'Display_Size', 
                        'display_and_audio_features.screen_resolution': 'Display_Resolution', 
                        'rating_average': 'Extracted_Rating', 
                        'general.battery_backup': 'Battery_Backup', 
                        'dimensions.dimensions': 'Laptop_Dimensions', 
                        'dimensions.weight': 'Laptop_Weight', 
                        'review_count': 'No_Of_Reviews', 
                        'price': 'Price', 
                        'in_stock': 'Stock', 
                        'timestamp': 'Time_Of_Extraction', 
                        'url': 'URL', 'Source': 'Source','image_src':'image_src'}
        df_renamed = df_raw.rename(columns=renaming_dict)

        selectedColumns = list(renaming_dict.values())
        df = df_renamed[selectedColumns]

        df = df.copy()
        df.loc[df['Laptop_Model_Name'].isin(['G6 MF-H2IN853SH', 'AORUS 15 9MF-E2IN583SH']), 'Brand'] = 'GIGABYTE'
        df = df.copy()
        df['Brand'] = df['Brand'].fillna('ULTIMUS')

        # Function to convert dimensions from mm to inches
        def convert_dimensions(dimensions_str):
            if pd.isnull(dimensions_str):
                return None
            
            # Normalize the string to lowercase 'x' and remove ' mm'
            dimensions_str = dimensions_str.replace(' mm', '').replace(' X ', ' x ').replace(' X', ' x').replace('x ', ' x ')
            
            # Extract dimensions by splitting the string
            dimensions = dimensions_str.split(' x ')
            
            try:
                # Convert each dimension from mm to inches and round to 2 decimal places
                inches = [f"{round(float(dim) / 25.4, 2)}" for dim in dimensions]
                
                # Return the dimensions as a formatted string in inches
                return ' x '.join(inches) + ' inches'
            except ValueError:
                return None  # Return None if conversion fails

        # Apply the conversion function to the dimensions column
        df['Laptop_Dimensions'] = df['Laptop_Dimensions'].apply(convert_dimensions)

        # Function to convert weight from Kg to Pounds
        def convert_weight(weight_str):
            if pd.isnull(weight_str):
                return None
            
            # Extract the numeric part and convert to float
            try:
                weight_kg = float(weight_str.replace(' Kg', '').strip())
                weight_lb = round(weight_kg * 2.20462, 2)  # Convert to pounds and round to 2 decimal places
                return f"{weight_lb} lbs"  # Return the weight in lbs
            except ValueError:
                return None  # Return None if conversion fails

        # Apply the conversion function to the weight column

        df['Laptop_Weight'] = df['Laptop_Weight'].apply(convert_weight)

        df = df.copy()
        df['Laptop_Weight(Pounds)'] = df['Laptop_Weight'].str.extract('(\d+(\.\d+)?)')[0].astype(float)
        df['RAM(GB)'] = df['RAM'].str.extract('(\d+)').astype(int)

        # Function to extract the battery life in hours
        def extract_battery_life(battery_life_str):
            if pd.isnull(battery_life_str):
                return None
            
            # Extract the numeric part
            try:
                battery_life = float(battery_life_str.split()[1])  # Take the second word which is the number
                return battery_life  # Return the battery life in hours as a float
            except (ValueError, IndexError):
                return None  # Return None if extraction fails

        # Create a new column for battery life in hours
        df = df.copy()
        df['Battery_Life(Hours_Upto)'] = df['Battery_Backup'].apply(extract_battery_life)

        # Define the exchange rate
        exchange_rate = 0.012  # Example exchange rate (1 INR = 0.012 USD)

        # Function to convert price from INR to USD
        def convert_price_to_usd(price_str):
            if pd.isnull(price_str):
                return None
            
            # Remove the currency symbol and commas, then convert to float
            try:
                price_inr = float(price_str.replace('₹', '').replace(',', '').strip())
                price_usd = price_inr * exchange_rate  # Convert to USD
                return round(price_usd, 2)  # Round to 2 decimal places
            except ValueError:
                return None  # Return None if conversion fails

        # Create a new column for the price in USD
        df = df.copy()
        df['Price(USD)'] = df['Price'].apply(convert_price_to_usd)
        
        def split_reviews(review_str):
            if pd.isnull(review_str):
                return None, None
            
            # Replace non-breaking space with regular space
            review_str = review_str.replace('\xa0', ' ')

            if ' & ' in review_str:
                try:
                    # Split based on ' & ' after replacing non-breaking spaces
                    ratings, reviews = review_str.split(' & ')

                    # Extract number of ratings
                    no_of_ratings = int(ratings.replace(',', '').split()[0])
                    # Extract number of reviews
                    no_of_reviews = int(reviews.replace(',', '').split()[0])  
                    
                    return no_of_ratings, no_of_reviews
                except (ValueError, IndexError) as e:
                    return None, None

            # Handle cases without reviews
            if 'Ratings' in review_str:
                try:
                    no_of_ratings = int(review_str.replace(',', '').split()[0])
                    return no_of_ratings, None
                except ValueError as e:
                    return None, None

            return None, None
            

        # Apply the function and create new columns
        df = df.copy()
        df['No_of_Ratings'], df['No_Of_Reviews2'] = zip(*df['No_Of_Reviews'].apply(split_reviews))

        # Converting all storage sizes to GB
        def convert_to_gb(size):
            if 'TB' in size:
                return int(size.replace('TB', '').strip()) * 2048
            elif 'GB' in size:
                return int(size.replace('GB', '').strip())
            elif 'SSD' in size: 
                return int(size.replace('SSD', '').strip())
            else:
                return size

        df = df.copy()
        df['Storage_Capacity(GB)'] = df['Storage_Capacity'].apply(convert_to_gb)
        df['Storage_Capacity(GB)'] = df['Storage_Capacity(GB)'].astype(int)

        # Function to extract inch value
        def extract_inches(display_size):
            if pd.isnull(display_size):
                return None
            match = re.search(r'(\d+\.?\d*)\s*Inch', display_size)
            return float(match.group(1)) if match else None

        # Apply the function to create a new column
        df = df.copy()
        df['Display_Size(Inches)'] = df['Display_Size'].apply(extract_inches)
        df.head()

        finalColumns = ['Brand', 'Laptop_Model_Name', 'Laptop_Model_Number', 'Processor_Brand',
       'Processor_Model', 'Storage_Type', 'Storage_Capacity(GB)',
       'Operating_System','Display_Size(Inches)', 'Display_Resolution',
       'Extracted_Rating', 'Laptop_Dimensions', 'Stock',
       'Time_Of_Extraction', 'URL', 'Source', 'Laptop_Weight(Pounds)',
       'RAM(GB)', 'Battery_Life(Hours_Upto)', 'Price(USD)', 'No_of_Ratings','image_src']

        alignedDF = df[finalColumns]

        alignRenaming = {
    'Price(USD)':'Price',
    'No_of_Ratings':'No_Of_Reviews'
        }
        finalDF = alignedDF.rename(columns=alignRenaming)

        # Export DataFrame to CSV
        finalDF.to_csv(cleanedFilePath, index=False)
        return cleanedFilePath