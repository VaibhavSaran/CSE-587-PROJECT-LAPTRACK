import pandas as pd
import numpy as np
import re
import os

class BestBuyCleaner:
    def __init__(self,input_dir="./etl/scraped_data",output_dir="./etl/clean_data"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_next_filenames(self):
        """Auto-increment the output file name."""
        existing_files = os.listdir("./etl/scraped_data")
        csv_files = [f for f in existing_files if f.startswith("bestbuy_scraped_data_") and f.endswith(".csv")]
        indices = [
            int(f.replace("bestbuy_scraped_data_", "").replace(".csv", ""))
            for f in csv_files if f.replace("bestbuy_scraped_data_", "").replace(".csv", "").isdigit()
        ]
        latest_index = max(indices, default=1)
        return (os.path.join(self.input_dir, f"bestbuy_scraped_data_{latest_index}.csv"),os.path.join(self.output_dir, f"bestbuy_cleaned_data_{latest_index}.csv"))
    
    def cleanDataAndExport(self):
        dataFilePath,cleanedFilePath = self.get_next_filenames()
        df_raw = pd.read_csv(dataFilePath)

        potential_brands = ['HP','ASUS','Lenovo','DELL','MSI','Avita','Acer','Infinix','Apple','SAMSUNG','MICROSOFT','Ultimus''GIGABYTE','Colorful','ZEBRONICS','CHUWI','Thomson','realme','WINGS','AXL','ALIENWARE','Vaio','Primebook','walker']
        # Create a regex pattern that matches any of the brands
        pattern = r'\b(' + '|'.join(re.escape(brand) for brand in potential_brands) + r')\b'
        df_raw = df_raw.copy()
        # Use regex to find and set the brand name if it exists in the 'product_title'
        df_raw['general.brand'] = df_raw.apply(lambda row: re.search(pattern, row['product_title']).group(0) if re.search(pattern, row['product_title']) else row['general.brand'],axis=1)

        batterycolumns = ['key_specs.battery_life_(up_to)','power.battery_life_(up_to)']
        df_raw = df_raw.copy()
        df_raw['Battery_Life'] = df_raw[batterycolumns].bfill(axis=1).iloc[:,0]

        batteryTypecolumns = ['key_specs.battery_type','power.battery_type']
        df_raw = df_raw.copy()
        df_raw['Battery_Type'] = df_raw[batteryTypecolumns].bfill(axis=1).iloc[:,0]

        #Add Source
        df_raw['Source'] = 'BestBuy'
        df_raw.head()

        graphicsTypecolumns = ['key_specs.battery_type','power.battery_type']
        df_raw = df_raw.copy()
        df_raw['Battery_Type'] = df_raw[batteryTypecolumns].bfill(axis=1).iloc[:,0]

        # Renaming columns to ensure uniformity
        renaming_dict = {'general.brand': 'Brand', 
                        'general.product_name': 'Laptop_Model_Name', 
                        'general.model_number': 'Laptop_Model_Number', 
                        'processor.processor_brand': 'Processor_Brand', 
                        'processor.processor_model': 'Processor_Model', 
                        'storage.storage_type': 'Storage_Type', 
                        'storage.total_storage_capacity': 'Storage_Capacity', 
                        'compatibility.operating_system': 'Operating_System', 
                        'memory.system_memory_(ram)': 'RAM', 
                        'key_specs.screen_size': 'Display_Size', 
                        'display.screen_resolution': 'Display_Resolution', 
                        'rating_average': 'Extracted_Rating', 
                        'Battery_Life': 'Battery_Backup', 
                        'dimensions.product_height':'Laptop_Height',
                        'dimensions.product_width':'Laptop_Width',
                        'dimensions.product_depth':'Laptop_Depth',
                        'dimensions.product_weight': 'Laptop_Weight', 
                        'review_count': 'No_Of_Reviews', 
                        'price': 'Price', 
                        'in_stock': 'Stock', 
                        'timestamp': 'Time_Of_Extraction', 
                        'url': 'URL', 
                        'Source': 'Source',
                        'image_src':'image_src'}

        df_renamed = df_raw.rename(columns=renaming_dict)
        selectedColumns = list(renaming_dict.values())
        df = df_renamed[selectedColumns]
        df = df.copy()
        df['Storage_Type'] = df['Storage_Type'].fillna('SSD')
        df = df.copy()
        df['Storage_Capacity'] = df['Storage_Capacity'].fillna('512 gigabytes')
        df = df.copy()
        df['Operating_System'] = df['Operating_System'].fillna('MacOS')

        df = df.copy()
        df['Storage_Capacity(GB)'] = df['Storage_Capacity'].str.extract('(\d+)').astype(int)
        df['RAM(GB)'] = df['RAM'].str.extract('(\d+)').astype(int)

        df = df.copy()
        # Extract the numeric part from 'display_size' and convert to float
        df['Display_Size(Inches)'] = df['Display_Size'].str.extract('(\d+(\.\d+)?)')[0].astype(float)
        df['Laptop_Weight(Pounds)'] = df['Laptop_Weight'].str.extract('(\d+(\.\d+)?)')[0].astype(float)

        df = df.copy()
        # Function to format dimensions only if all are present
        def format_dimensions(row):
            height = row['Laptop_Height']
            width = row['Laptop_Width']
            depth = row['Laptop_Depth']
            
            # Check if all dimensions are not null
            if pd.notnull(height) and pd.notnull(width) and pd.notnull(depth):
                # Remove ' inches' and convert to float
                height_value = height.replace(' inches', '')
                width_value = width.replace(' inches', '')
                depth_value = depth.replace(' inches', '')
                
                return f"{height_value} x {width_value} x {depth_value} inches"
            else:
                return np.nan  # Or return an empty string or a placeholder if preferred
        # Create a new column with the desired format
        df['Laptop_Dimensions'] = df.apply(format_dimensions, axis=1)

        # Function to extract price as float
        def extract_price(price_str):
            if pd.isnull(price_str):
                return None
            match = re.search(r'\$([\d,]+\.\d{2})', price_str)
            if match:
                # Convert extracted price to float after removing commas
                return float(match.group(1).replace(',', ''))
            return None

        # Apply the function to the price column
        df['Price'] = df['Price'].apply(extract_price)

        # Function to extract the battery life in hours
        def extract_battery_life(battery_life_str):
            if pd.isnull(battery_life_str):
                return None
            
            # Extract the numeric part
            try:
                battery_life = float(battery_life_str.split()[0])  # Take the second word which is the number
                return battery_life  # Return the battery life in hours as a float
            except (ValueError, IndexError):
                return None  # Return None if extraction fails

        # Create a new column for battery life in hours
        df = df.copy()
        df['Battery_Life(Hours_Upto)'] = df['Battery_Backup'].apply(extract_battery_life)

        finalColumns = ['Brand', 'Laptop_Model_Name', 'Laptop_Model_Number', 'Processor_Brand',
       'Processor_Model', 'Storage_Type', 
       'Operating_System', 'Display_Resolution',
       'Extracted_Rating', 'Battery_Life(Hours_Upto)', 'No_Of_Reviews', 'Price', 'Stock',
       'Time_Of_Extraction', 'URL', 'Source', 'Storage_Capacity(GB)',
       'RAM(GB)', 'Display_Size(Inches)', 'Laptop_Weight(Pounds)',
       'Laptop_Dimensions','image_src']
        
        alignedDF = df[finalColumns]

        # Export DataFrame to CSV
        alignedDF.to_csv(cleanedFilePath, index=False)
        return cleanedFilePath