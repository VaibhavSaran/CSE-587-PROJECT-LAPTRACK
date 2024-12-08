import pandas as pd
import numpy as np
import re
import os
from collections import defaultdict

class CombinedCleaner:
    def __init__(self,input_dir="./etl/clean_data",output_dir="./etl/clean_data"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_next_filenames(self):
        """Auto-increment the output file name."""
        existing_files = os.listdir("./etl/clean_data")
        print(existing_files)
        print("Current working directory:", os.getcwd())
        csv_files = [f for f in existing_files if f.startswith("amazon_cleaned_data_") and f.endswith(".csv")]
        indices = [
            int(f.replace("amazon_cleaned_data_", "").replace(".csv", ""))
            for f in csv_files if f.replace("amazon_cleaned_data_", "").replace(".csv", "").isdigit()
        ]
        latest_index = max(indices, default=1)
        return (os.path.join(self.input_dir, f"amazon_cleaned_data_{latest_index}.csv"),os.path.join(self.input_dir, f"bestbuy_cleaned_data_{latest_index}.csv"),os.path.join(self.input_dir, f"flipkart_cleaned_data_{latest_index}.csv"),os.path.join(self.input_dir, f"Laptrack_{latest_index}.csv"))
    
    def cleanDataAndExport(self):
        amazonDataFilePath ,bestbuyDataFilePath,flipkartDataFilePath,outputFilePath = self.get_next_filenames()

        amazonDF = pd.read_csv(amazonDataFilePath)
        bestbuyDF = pd.read_csv(bestbuyDataFilePath)
        flipkartDF = pd.read_csv(flipkartDataFilePath)

        df = pd.concat([amazonDF, flipkartDF,bestbuyDF], ignore_index=True, sort=False)
        df['Stock'] = df['Stock'].astype(bool)
        df['Time_Of_Extraction'] = pd.to_datetime(df['Time_Of_Extraction'])
        df.loc[df['Processor_Brand'] == 'INTE',['Processor_Brand']] = 'Intel'
        
        # Define the specific columns to check for NaN values
        columns_to_check = ['Price','Processor_Model']

        # Drop rows where any of the specified columns are null
        laptop_df_cleaned = df.dropna(subset=columns_to_check)
        laptop_df_cleaned = laptop_df_cleaned.copy()
        def extract_reviews_count(reviews_str):
            if pd.isna(reviews_str):
                return 0
            else:
                # Use regex to find the number in the string
                match = re.search(r'\d+(?:[,\.]?\d+)?', str(reviews_str))
                if match:
                    # Convert the matched string to a float and then to an integer
                    return int(float(match.group().replace(',', '')))
                else:
                    return 0
        laptop_df_cleaned['No_Of_Reviews'] = laptop_df_cleaned['No_Of_Reviews'].apply(extract_reviews_count)

        # Pattern to match Apple processors and their variants (case-insensitive)
    

        # Function to normalize Apple processor models
        def normalize_apple_processors(processor):
            # Convert the processor name to uppercase for consistent matching
            apple_pattern = r'\b(M\d+)(?:\s+(Pro|Max|Ultra|Plus))?\b'
            processor = processor.strip()  # Ensure the model is uppercase
            match = re.search(apple_pattern, processor, re.IGNORECASE)
            if match:
                base_model = match.group(1).upper()  # E.g., 'M1', 'M2', 'M3'
                variant = match.group(2)     # E.g., 'Pro', 'Max', 'Ultra'
                if variant:
                    normalized_processor = f"{base_model} {variant}"  # Combine model and variant
                else:
                    normalized_processor = base_model  # Just the model if no variant
                return (normalized_processor,True)
            else:
                return (processor,False)  # If no match, keep as is

        # Function to normalize processor names
        def normalize_processor(model):
            # Handle common patterns and normalize
            if pd.isna(model) or model == 'Unknown':
                return None
            
            # First, check if it's an Apple processor
            apple_normalized,status = normalize_apple_processors(model)
            if status:
                return apple_normalized

            # AMD Ryzen series
            amd_ryzen = re.search(r'(AMD )?(Ryzen \d)', model, re.IGNORECASE)
            if amd_ryzen:
                return amd_ryzen.group(2)

            # AMD Athlon or A-series
            amd_other = re.search(r'AMD (Athlon|A Series)', model, re.IGNORECASE)
            if amd_other:
                return 'AMD ' + amd_other.group(1)

            # Intel Core series
            intel_core = re.search(r'(Intel )?(Core i[3579])', model, re.IGNORECASE)
            if intel_core:
                # Normalize the 'Core iX' to 'Core iX' with lowercase 'i' for consistency
                core_model = intel_core.group(2).lower().capitalize()  # Converts 'Core I7' to 'Core i7'
                return core_model
            else:
                return model  # If no match, return the original model

        df = df.copy()
        # Apply the normalization function to the DataFrame
        df['Processor_Model'] = df['Processor_Model'].apply(normalize_processor)

        # Extract unique brands
        brands = df['Brand'].dropna().unique()
        # Dynamically create brand mapping using fuzzy matching (simple approach)
        brand_mapping = defaultdict(str)

        def normalize_brand_name(brand):
            # Check if the brand is not NaN
            if isinstance(brand, str):
                brand_lower = brand.lower()

                # Check for common brand patterns and group them
                for known_brand in brands:
                    if known_brand.lower() in brand_lower:
                        return known_brand  # Normalize to the known brand name

            return brand
        # Apply the normalization function to all brand names
        df['Brand'] = df['Brand'].apply(normalize_brand_name)
        # In pandas
        df['Extracted_Rating'] = df['Extracted_Rating'].fillna(0)

        # Renaming columns to ensure uniformity
        renaming_dict = {
                        'Brand': 'brand', 
                        'Laptop_Model_Name':'laptop_model_name', 
                        'Laptop_Model_Number':'laptop_model_number', 
                        'Processor_Brand':'processor_brand', 
                        'Processor_Model':'processor_model', 
                        'Storage_Type':'storage_type', 
                        'Storage_Capacity(GB)':'storage_capacity_gb', 
                        'Operating_System':'operating_system', 
                        'RAM(GB)':'ram_gb', 
                        'Display_Size(Inches)':'display_size_inches', 
                        'Display_Resolution':'display_resolution', 
                        'Extracted_Rating':'extracted_rating', 
                        'Battery_Life(Hours_Upto)':'battery_life_hours_upto', 
                        'Laptop_Dimensions':'laptop_dimensions', 
                        'Laptop_Weight(Pounds)':'laptop_weight_pounds', 
                        'No_Of_Reviews':'no_of_reviews', 
                        'Price':'price', 
                        'Stock':'stock', 
                        'Time_Of_Extraction':'time_of_extraction', 
                        'URL':'url', 
                        'Source':'source',
                        'image_src':'image_src'
                        }
        df_renamed = df.rename(columns=renaming_dict)
        # Export DataFrame to CSV
        
        df_renamed.to_csv(outputFilePath, index=False)
        return outputFilePath
