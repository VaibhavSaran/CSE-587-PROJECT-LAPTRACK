import pandas as pd
import numpy as np
import re
import os

class CombinedCleaner:
    def __init__(self,input_dir="clean_data",output_dir="clean_data"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # def get_next_filenames(self):
    #     """Auto-increment the output file name."""
    #     existing_files = os.listdir("scraped_data")
    #     csv_files = [f for f in existing_files if f.startswith("amazon_scraped_data_") and f.endswith(".csv")]
    #     indices = [
    #         int(f.replace("amazon_scraped_data_", "").replace(".csv", ""))
    #         for f in csv_files if f.replace("amazon_scraped_data_", "").replace(".csv", "").isdigit()
    #     ]
    #     amazon_latest_index = max(indices, default=1)
    #     return (os.path.join(self.input_dir, f"amazon_scraped_data_{latest_index}.csv"),os.path.join(self.output_dir, f"amazon_cleaned_data_{latest_index}.csv"))
    
    def cleanDataAndExport(self):
        amazonDataFilePath = './clean_data/amazon_cleaned_data_1.csv'
        bestbuyDataFilePath = './clean_data/bestbuy_cleaned_data_1.csv'
        flipkartDataFilePath = './clean_data/flipkart_cleaned_data_1.csv'

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
        # Export DataFrame to CSV
        outputFilePath = './clean_data/LaptrackPhase3_2.csv'
        laptop_df_cleaned.to_csv(outputFilePath, index=False)
        return outputFilePath

