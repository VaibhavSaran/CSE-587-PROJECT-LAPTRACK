import pandas as pd
import numpy as np
import re
import os

class AmazonCleaner:
    def __init__(self,input_dir="./etl/scraped_data",output_dir="./etl/clean_data"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_next_filenames(self):
        """Auto-increment the output file name."""
        existing_files = os.listdir("./etl/scraped_data")
        csv_files = [f for f in existing_files if f.startswith("amazon_scraped_data_") and f.endswith(".csv")]
        indices = [
            int(f.replace("amazon_scraped_data_", "").replace(".csv", ""))
            for f in csv_files if f.replace("amazon_scraped_data_", "").replace(".csv", "").isdigit()
        ]
        latest_index = max(indices, default=1)
        return (os.path.join(self.input_dir, f"amazon_scraped_data_{latest_index}.csv"),os.path.join(self.output_dir, f"amazon_cleaned_data_{latest_index}.csv"))
    
    def cleanDataAndExport(self):
        dataFilePath,cleanedFilePath = self.get_next_filenames()
        df = pd.read_csv(dataFilePath)

        # For Brand Name
        brandColumns = ['Other Technical Details_Brand','Product Details_Brand','New Product Details_Brand Name','New Product Details_Brand','Additional Details_Manufacturer']
        # Creating the new column with any non-naN value found from the chosen columns associated to Brand.
        df = df.copy()
        df['Brand'] = df[brandColumns].bfill(axis=1).iloc[:,0]

        df.loc[df['Brand'] == 'Harry Potter',['Brand']] = 'HP'
        df.loc[df['Brand'] == 'HEWLETT PACKARD',['Brand']] = 'HP'
        df.loc[df['Brand'] == 'hp',['Brand']] = 'HP'
        df.loc[df['Brand'].str.contains('lenovo', case=False, na=False), 'Brand'] = 'Lenovo'
        df.loc[df['Brand'].str.contains('acer', case=False, na=False), 'Brand'] = 'Acer'
        df.loc[df['Brand'].str.contains('dell', case=False, na=False), 'Brand'] = 'Dell'

        #Try to get Brands from Title
        potential_brands = ['HP','ASUS','Lenovo','DELL','MSI','Avita','Acer','Infinix','Apple','SAMSUNG','MICROSOFT','Ultimus''GIGABYTE','Colorful','ZEBRONICS','CHUWI','Thomson','realme','WINGS','AXL','ALIENWARE','Vaio','Primebook','walker']
        # Create a regex pattern that matches any of the brands
        pattern = r'\b(' + '|'.join(re.escape(brand) for brand in potential_brands) + r')\b'
        df = df.copy()
        # Use regex to find and set the brand name if it exists in the 'product_title'
    
        df['Brand'] = df.apply(
    lambda row: re.search(pattern, str(row['Title'])).group(0) if isinstance(row['Title'], str) and re.search(pattern, row['Title']) else row['Brand'],
    axis=1
)

        processorBrandColumns = ['Other Technical Details_Processor Brand','New Product Details_Processor Brand','Product Details_CPU Manufacturer']
        df = df.copy()
        df['Processor_Brand'] = df[processorBrandColumns].bfill(axis=1).iloc[:,0]

        # All these Processor Brands are misnomers, they are listed as processor brands on Amazon but are instead Series or a range of processors by Intel
        df.loc[df['Processor_Brand'] == 'Celeron',['Processor_Model']] = 'Celeron N5095'
        df.loc[df['Processor_Brand'] == 'Celeron',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'I',['Processor_Brand']] = 'Intel'

        # df.loc[df['Processor_Brand'] == 'I',['Processor_Brand']] = 'Intel'

        # df.loc[df['Processor_Brand'] == 'I',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Jasper Lake',['Processor_Model']] = 'Celeron N5095'
        df.loc[df['Processor_Brand'] == 'Jasper Lake',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Core',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Intel Celeron N4120',['Processor_Model']] = df.loc[df['Processor_Brand'] == 'Intel Celeron N4120',['Processor_Brand']]

        df.loc[df['Processor_Brand'] == 'Intel Celeron N4120',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'HP',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Dell',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'core_i7_6700hq',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'core_i7_5650u',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'core_i5_4260u',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'core_i5',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Int',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'INTE',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Samsung',['Processor_Brand']] = 'Intel'

        df.loc[df['Processor_Brand'] == 'Ryzen',['Processor_Brand']] = 'AMD'

        # For Processor Model
        processorModelColumns = ['Product Details_CPU Model','New Product Details_CPU Model Number','Technical Details_Processor','New Product Details_CPU Codename','New Product Details_Processor','New Product Details_Processor Series']
        df = df.copy()
        df['Processor_Model'] = df[processorModelColumns].bfill(axis=1).iloc[:,0]

        # Some products have Processor name as 'Intel Core i5' at the cost of not giving the processor comapny explicitly
        df.loc[df['Processor_Model'].str.contains('Apple',na=False),'Processor_Brand'] = 'Apple'
        df.loc[df['Processor_Model'].str.contains('Intel',na=False),'Processor_Brand'] = 'Intel'
        df.loc[df['Processor_Model'] == '3.2 GHz apple_m1','Processor_Model'] = 'Apple M1 Pro'

        # Pattern to match Apple processors and their variants (case-insensitive)
        apple_pattern = r'\b(M\d+)(?:\s+(Pro|Max|Ultra|Plus))?\b'

        # Function to normalize Apple processor models
        def normalize_apple_processors(processor):
            # Convert the processor name to uppercase for consistent matching
            processor = processor.strip()  # Ensure the model is uppercase
            match = re.search(apple_pattern, processor, re.IGNORECASE)
            if match:
                base_model = match.group(1).upper()  # E.g., 'M1', 'M2', 'M3'
                variant = match.group(2)     # E.g., 'Pro', 'Max', 'Ultra'
                if variant:
                    normalized_processor = f"{base_model} {variant}"  # Combine model and variant
                else:
                    normalized_processor = base_model  # Just the model if no variant
                return normalized_processor
            else:
                return processor  # If no match, keep as is

        # Function to normalize processor names
        def normalize_processor(model):
            # Handle common patterns and normalize
            if pd.isna(model) or model == 'Unknown':
                return None

            # Intel Core series
            intel_core = re.search(r'(Intel )?(Core i[3579])', model, re.IGNORECASE)
            if intel_core:
                # Normalize the 'Core iX' to 'Core iX' with lowercase 'i' for consistency
                core_model = intel_core.group(2).lower().capitalize()  # Converts 'Core I7' to 'Core i7'
                return core_model
            else:
                return model  # If no match, return the original model

            # First, check if it's an Apple processor
            apple_normalized = normalize_apple_processors(model)
            if apple_normalized:
                return apple_normalized

            # AMD Ryzen series
            amd_ryzen = re.search(r'(AMD )?(Ryzen \d)', model, re.IGNORECASE)
            if amd_ryzen:
                return amd_ryzen.group(2)

            # AMD Athlon or A-series
            amd_other = re.search(r'AMD (Athlon|A Series)', model, re.IGNORECASE)
            if amd_other:
                return 'AMD ' + amd_other.group(1)

            # # Celeron, Pentium, and Xeon series
            # if 'Celeron' in model:
            #     return 'Celeron'
            # if 'Pentium' in model:
            #     return 'Pentium'
            # if 'Xeon' in model:
            #     return 'Xeon'
            
            # # ARM-based processors
            # if 'ARM' in model or 'Cortex' in model:
            #     return 'ARM'
            
            # # Snapdragon and MediaTek
            # if 'Snapdragon' in model:
            #     return 'Snapdragon'
            # if 'MediaTek' in model:
            #     return 'MediaTek'
            
            # Others that might need further inspection
            return model

        df = df.copy()
        # Apply the normalization function to the DataFrame
        df['Processor_Model'] = df['Processor_Model'].apply(normalize_processor)
        df['Processor_Model'].unique()

        processor_models = df['Processor_Model'].unique()

        # Regular expression pattern to identify malformed processor names
        nonepattern = re.compile(r'(\d+(\.\d+)?\s*(GHz|GHz\s*none|none|MHz|core|E\+?\d*)|[^A-Za-z0-9\s])')

        # Find and print all models that match the pattern
        malformed_models = [model for model in processor_models if model and nonepattern.search(str(model))]

        badProcessorModelcondition = (df['Processor_Model'].isnull() | (df['Processor_Model'] == 'Unknown') | (df['Processor_Model'] == 'Other') | (df['Processor_Model'].isin(malformed_models)))

        df = df[~badProcessorModelcondition]

        osColumns = ['Product Details_Operating System','New Product Details_Operating System','Other Technical Details_Operating System']
        df = df.copy()
        df['Operating_System'] = df[osColumns].bfill(axis=1).iloc[:,0]

        # Define a function to normalize OS names using regex
        def normalize_os(os_name):
            if pd.isna(os_name):  # Handle NaN values
                return None

            # Normalize Windows OS
            if re.search(r'windows\s*11.*pro', os_name, re.IGNORECASE):
                return 'Windows 11 Pro'
            elif re.search(r'windows\s*11.*home', os_name, re.IGNORECASE):
                return 'Windows 11 Home'
            elif re.search(r'windows\s*11.*s', os_name, re.IGNORECASE):
                return 'Windows 11 S'
            elif re.search(r'windows\s*10.*pro', os_name, re.IGNORECASE):
                return 'Windows 10 Pro'
            elif re.search(r'windows\s*10.*home', os_name, re.IGNORECASE):
                return 'Windows 10 Home'
            elif re.search(r'windows\s*10.*s', os_name, re.IGNORECASE):
                return 'Windows 10 S'
            elif re.search(r'windows\s*10', os_name, re.IGNORECASE):
                return 'Windows 10'
            elif re.search(r'windows', os_name, re.IGNORECASE):
                return 'Windows'

            # Normalize macOS versions
            if re.search(r'catalina|10\.15', os_name, re.IGNORECASE):
                return 'macOS Catalina'
            elif re.search(r'mojave|10\.14', os_name, re.IGNORECASE):
                return 'macOS Mojave'
            elif re.search(r'big sur|11', os_name, re.IGNORECASE):
                return 'macOS Big Sur'
            elif re.search(r'monterey|12', os_name, re.IGNORECASE):
                return 'macOS Monterey'
            elif re.search(r'sierra|10\.12', os_name, re.IGNORECASE):
                return 'macOS Sierra'
            elif re.search(r'high sierra|10\.13', os_name, re.IGNORECASE):
                return 'macOS High Sierra'
            elif re.search(r'sonoma', os_name, re.IGNORECASE):
                return 'macOS Sonoma'
            elif re.search(r'ventura', os_name, re.IGNORECASE):
                return 'macOS Ventura'
            elif re.search(r'mavericks|10\.9', os_name, re.IGNORECASE):
                return 'macOS Mavericks'
            elif re.search(r'yosemite|10\.10', os_name, re.IGNORECASE):
                return 'macOS Yosemite'
            elif re.search(r'mountain lion|10\.8', os_name, re.IGNORECASE):
                return 'macOS Mountain Lion'
            elif re.search(r'cheetah|10\.0', os_name, re.IGNORECASE):
                return 'macOS Cheetah'
            elif re.search(r'mac\s?os', os_name, re.IGNORECASE):
                return 'macOS'

            # Normalize other OS types
            if re.search(r'chrome\s*os', os_name, re.IGNORECASE):
                return 'Chrome OS'
            elif re.search(r'linux', os_name, re.IGNORECASE):
                return 'Linux'
            elif re.search(r'dos', os_name, re.IGNORECASE):
                return 'DOS'
            elif re.search(r'pc', os_name, re.IGNORECASE):
                return None  # Assuming "PC" alone is invalid/missing information
            elif os_name.lower() in ['os', 'vv11']:  # Gibberish cases
                return None  # Handle as invalid data

            # Return the original if no pattern matches (fallback)
            return os_name

        # Apply the normalization function to the DataFrame
        df['Operating_System'] = df['Operating_System'].apply(normalize_os)
    
        noOSCondition = df['Operating_System'].isnull()
        df = df[~noOSCondition]

        ramColumns = ['Product Details_Ram Memory Installed Size','Product Details_Memory Storage Capacity','New Product Details_Ram Memory Maximum Size','New Product Details_RAM Memory Installed','Technical Details_RAM','New Product Details_RAM']
        df = df.copy()
        df['RAM_Size'] = df[ramColumns].bfill(axis=1).iloc[:,0]

        noRAMCondition = df['RAM_Size'].isnull()
        df = df[~noRAMCondition]

        df = df.copy()
        df['RAM(GB)'] = df['RAM_Size'].str.extract(r'(\d+)').astype(int)
        storageColumns = ['Technical Details_Hard Drive','Additional Details_Hard Drive Size','Product Details_Hard Disk Size','New Product Details_Hard-Drive Size','New Product Details_Hard-Drive Size','Product Details_Memory Storage Capacity','New Product Details_Flash Memory Size','Other Technical Details_Flash Memory Size','New Product Details_Hard Drive']
        df = df.copy()
        df['Storage_Capacity'] = df[storageColumns].bfill(axis=1).iloc[:,0]

        nostorageCapacityCondition = df['Storage_Capacity'].isnull()
        df = df[~nostorageCapacityCondition]

        storageTypeColumns = ['New Product Details_Hard Disk Description','New Product Details_Hard Disk Interface']
        df = df.copy()
        df['Storage_Type'] = df[storageTypeColumns].bfill(axis=1).iloc[:,0]

        def determine_storage_type(storage, current_storage_type):
            # Convert the storage to string and handle NaN values
            if pd.isnull(storage):
                return current_storage_type  # Don't change the Storage_Type if it's already set

            if pd.notnull(current_storage_type):
                current_storage_type_str = str(current_storage_type).lower()
                if 'emmc' in current_storage_type_str:
                    return 'eMMC'
                elif 'nvme' in current_storage_type_str:
                    return 'NVMe SSD'
                elif 'Solid State Drive'.lower() in current_storage_type_str or 'ssd' in current_storage_type_str:
                    return 'SSD'
                elif 'hdd' in current_storage_type_str:
                    return 'HDD'
            
            storage_str = str(storage).lower()  # Convert to string

            # Check if the storage type matches known types
            if 'hdd' in storage_str:
                return 'HDD'
            elif 'nvme' in storage_str:
                return 'NVMe SSD'
            elif 'ssd' in storage_str:
                return 'SSD'
            elif 'emmc' in storage_str or 'Embedded MultiMediaCard'.lower() in storage_str:
                return 'eMMC'
            else:
                return current_storage_type  # Return the existing Storage_Type if no match
        
        # Apply the function to 'Storage_Capacity' and 'Storage_Type' columns
        df['Storage_Type'] = df.apply(
            lambda row: determine_storage_type(row['Storage_Capacity'], row['Storage_Type']), axis=1
        )

        nostorageTypeCondition = df['Storage_Type'].isnull()
        df = df[~nostorageTypeCondition]

        # Extract storage size into a new column 'Storage_Size'
        df = df.copy()
        df['Storage_Size'] = df['Storage_Capacity'].str.extract(r'(\d+\s*[KMG]B|\d+\s*TB|\d+\s*SSD)', expand=False)

        displaySizeColumns = ['Product Details_Screen Size','Technical Details_Standing screen display size','New Product Details_Screen Size','Additional Details_Standing screen display size']
        df = df.copy()

        df['Display_size'] = df[displaySizeColumns].bfill(axis=1).iloc[:,0]
        df = df.copy()
        df['Display_Size(Inches)'] = df['Display_size'].str.extract(r'(\d+(\.\d+)?)', expand=False)[0].fillna(0).astype(float)

        noDisplayCondition = df['Display_Size(Inches)'] == 0.0
        df = df[~noDisplayCondition]

        #Model Name
        modelNameColumns = ['Product Details_Model Name','New Product Details_Model Name','New Product Details_Series','Other Technical Details_Series']
        df = df.copy()
        df['Laptop_Model_Name'] = df[modelNameColumns].bfill(axis=1).iloc[:,0]

        #For Model Number
        modelNumberColumns = ['Additional Details_Item model number','New Product Details_Item model number','Other Technical Details_Item model number','Technical Details_Item model number','New Product Details_Model Number']
        df = df.copy()
        df['Laptop_Model_Number'] = df[modelNumberColumns].bfill(axis=1).iloc[:,0]

        colorColumns = ['Product Details_Color','New Product Details_Color','Other Technical Details_Color']

        df = df.copy()
        df['Laptop_Color'] = df[colorColumns].bfill(axis=1).iloc[:,0]

        reviewColumns = ['Additional Details_Customer Reviews', 'New Product Details_Customer Reviews']
        df = df.copy()
        df['Number_of_reviews'] = df[reviewColumns].bfill(axis=1).iloc[:,0]

        # Extract review counts from the column
        df = df.copy()
        df['reviews_count'] = df['Number_of_reviews'].str.extract(r'(\d+)\s+rating(?:s)?').fillna(0).astype(int)

        batteryColumns = ['Additional Details_Battery life', 'New Product Details_Average Battery Life (in hours)','New Product Details_Battery Average Life','New Product Details_Battery Average Life Standby','New Product Details_Battery life','Technical Details_Average Battery Life (in hours)']
        df = df.copy()
        df['Battery_Backup'] = df[batteryColumns].bfill(axis=1).iloc[:,0]

        # Define a function to normalize battery backup values
        def normalize_battery_backup(value):
            if pd.isna(value):
                return np.nan
            
            value = value.strip()
            
            # Handle values in years and months by replacing them with NaN
            if '\tyears' in value or '\tmonths' in value:
                return np.nan
            
            # Convert quarters to hours (1 quarter = 2160 hours)
            if 'quarters' in value:
                try:
                    quarters_value = float(value.split()[0])
                    return round(quarters_value * 2160,2)
                except ValueError:
                    return np.nan

            # Convert minutes to hours
            elif 'minutes' in value:
                try:
                    minutes_value = float(value.split()[0])
                    return round(minutes_value / 60,2)  # Convert minutes to hours
                except ValueError:
                    return np.nan

            # Extract numerical part and convert to hours
            elif 'Hours' in value:
                try:
                    return round(float(value.split()[0]),2)  # Convert hours directly
                except ValueError:
                    return np.nan

            return np.nan

        # Apply the normalization function to the column
        df = df.copy()
        df['Battery_Backup(Hours Upto)'] = df['Battery_Backup'].apply(normalize_battery_backup)
        # Convert the values in 'Battery_Backup(Hours Upto)' to string with 2 decimal places
        df['Battery_Backup(Hours Upto)'] = df['Battery_Backup(Hours Upto)'].apply(lambda x: f'{x:.2f}' if pd.notna(x) else x)

        # Extract the rating using REGEX
        df = df.copy()
        df['Extracted_Rating'] = df['Number_of_reviews'].str.extract(r'(\d+\.\d+|\d+)', expand=False).astype(float)

        resolutionColumns = [
        'Additional Details_Resolution','New Product Details_Display Resolution Maximum','New Product Details_Max Screen Resolution',
        'New Product Details_Native Resolution','New Product Details_Resolution','Product Details_Display Resolution Maximum',
        'Product Details_Display resolution',
        'Product Details_Resolution',
        'Technical Details_Max Screen Resolution',
        'Technical Details_Screen Resolution']

        df = df.copy()
        df['Display_Resolution'] = df[resolutionColumns].bfill(axis=1).iloc[:,0]

        # Function to normalize resolutions
        def normalize_resolution(value):
            if pd.isna(value):
                return np.nan

            # Remove leading/trailing spaces
            value = value.strip()

            # Replace all variants of 'x' (like '×') with a standard 'x'
            value = value.replace('×', 'x')

            # Replace common delimiters like '*' and '_' with 'x'
            value = re.sub(r'[\*\_]', 'x', value)

            # Remove all non-numeric characters except digits and 'x'
            value = re.sub(r'[^0-9x]', '', value)

            # Ensure there is exactly one 'x' between two numbers
            value = re.sub(r'(\d)(x)(\d)', r'\1x\3', value)

            # Handle cases where the resolution is just a single number (e.g., '1080p')
            if 'x' not in value:
                return np.nan

            # Check for valid resolution format and return normalized result
            match = re.match(r'(\d+)\s*x\s*(\d+)', value)
            if match:
                # Extract width and height and return in consistent format
                width, height = match.groups()
                return f"{width}x{height} Pixels"

            return np.nan  # Return NaN if the value doesn't match the expected format

        # Apply the normalization function to the column
        df = df.copy()
        df['Normalized_Resolution'] = df['Display_Resolution'].apply(normalize_resolution)

        dimensionsColumns = ['Additional Details_Product Dimensions','New Product Details_Item Dimensions  LxWxH','New Product Details_Item Dimensions L x W x Thickness','New Product Details_Product Dimensions',
        'Other Technical Details_Item Dimensions  LxWxH','Other Technical Details_Product Dimensions',
        'Technical Details_Product Dimensions']

        df = df.copy()
        df['Laptop_Dimensions'] = df[dimensionsColumns].bfill(axis=1).iloc[:,0]

        # Function to convert dimensions
        def convert_dimensions(dim_str):
            if pd.isnull(dim_str):
                return None 
            # Split the string by ' x ' to separate dimensions
            parts = dim_str.split(' x ')
            
            # Extract numbers, remove quotes and suffixes, and convert to float
            dimensions = []
            for part in parts:
                # Remove any units and convert to float
                dimension_value = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-', part))  # Keep digits, '.', and '-'
                dimensions.append(float(dimension_value))
            
            # Rearrange and format the dimensions
            return f'{dimensions[0]:.2f} x {dimensions[1]:.2f} x {dimensions[2]:.2f} inches'

        # Apply the function to the DataFrame
        df = df.copy()
        df['Formatted_Dimensions'] = df['Laptop_Dimensions'].apply(convert_dimensions)

        weightColumns = ['Additional Details_Item Weight',
        'New Product Details_Item Weight',
        'Other Technical Details_Item Weight',
        'Product Details_Item Weight',
        'Technical Details_Item Weight']
        df = df.copy()
        df['Laptop_Weight'] = df[weightColumns].bfill(axis=1).iloc[:,0]

        #Add Source
        df['Source'] = 'Amazon'

        # Renaming columns to ensure uniformity
        renaming_dict = {'Brand': 'Brand', 
                        'Laptop_Model_Name': 'Laptop_Model_Name', 
                        'Laptop_Model_Number': 'Laptop_Model_Number', 
                        'processor_and_memory_features.processor_brand': 'Processor_Brand', 
                        'Processor_Model': 'Processor_Model', 
                        'Storage_Type': 'Storage_Type', 
                        'Storage_Capacity': 'Storage_Capacity', 
                        'Operating_System': 'Operating_System', 
                        'RAM_Size': 'RAM', 
                        'Display_size': 'Display_Size', 
                        'Display_Resolution': 'Display_Resolution', 
                        'Extracted_Rating': 'Extracted_Rating', 
                        'Battery_Backup': 'Battery_Backup', 
                        'Laptop_Dimensions': 'Laptop_Dimensions', 
                        'Laptop_Weight': 'Laptop_Weight', 
                        'Number_of_reviews': 'No_Of_Reviews', 
                        'price': 'Price', 
                        'In Stock': 'Stock', 
                        'timestamp': 'Time_Of_Extraction', 
                        'url': 'URL', 
                        'Source': 'Source',
                        'image_url':'image_src',
                        'Storage_Size':'Storage_Size',
                        'RAM(GB)':'RAM(GB)',
                        'Formatted_Dimensions':'Formatted_Dimensions'
                        }
        df_renamed = df.rename(columns=renaming_dict)
        
        selectedColumns = list(renaming_dict.values())
        finaldf = df_renamed[selectedColumns]
        df2 = finaldf.dropna(subset=['Storage_Size'])
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

        df2 = df2.copy()
        df2['Storage_Capacity(GB)'] = df2['Storage_Size'].apply(convert_to_gb)
        df2['Storage_Capacity(GB)'] = df2['Storage_Capacity(GB)'].astype(int)
        # Remove 'inches' and keep only the number from Display Screen Size
        df2['Display_Size(Inches)'] = df2['Display_Size'].str.replace(r'\s*inches?', '', case=False, regex=True)

        df2['Display_Size(Inches)'] = df2['Display_Size(Inches)'].astype(float)

        # Extract review counts from the column
        df2 = df2.copy()
        df2['reviews_count'] = df2['No_Of_Reviews'].str.extract(r'(\d+)\s+rating(?:s)?')
        df2['reviews_count'] = df2['reviews_count'].fillna(0)
        df2['reviews_count'] = df2['reviews_count'].astype(int)
        
        df2 = df2.copy()
        df2['Laptop_Weight(Pounds)'] = df2['Laptop_Weight'].str.extract('(\d+(\.\d+)?)')[0].astype(float)

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
        df2 = df2.copy()
        df2['Battery_Life(Hours_Upto)'] = df2['Battery_Backup'].apply(extract_battery_life)

        finalColumns = ['Brand', 'Laptop_Model_Name', 'Laptop_Model_Number', 'Processor_Brand',
       'Processor_Model', 'Storage_Type',
       'Operating_System', 'Display_Resolution',
       'Extracted_Rating', 'Battery_Life(Hours_Upto)', 'Price', 'Stock',
       'Time_Of_Extraction', 'URL', 'Source',
       'Storage_Capacity(GB)', 'Display_Size(Inches)', 'RAM(GB)',
       'reviews_count', 'Formatted_Dimensions', 'Laptop_Weight(Pounds)','image_src']
        alignedDF = df2[finalColumns]
        alignRenaming = {
        'reviews_count':'No_Of_Reviews',
        'Formatted_Dimensions':'Laptop_Dimensions'
        }
        finalDF = alignedDF.rename(columns=alignRenaming)

        # Export DataFrame to CSV
        finalDF.to_csv(cleanedFilePath, index=False)
        return cleanedFilePath

