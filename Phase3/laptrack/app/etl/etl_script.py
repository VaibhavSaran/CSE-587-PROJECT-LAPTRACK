from pyspark.sql import SparkSession
from amazonScraper import AmazonScraper
from amazonCleaner import AmazonCleaner
from BestBuyCleaner import BestBuyCleaner
from FlipkartCleaner import FlipkartCleaner
from combinedCleaner import CombinedCleaner

# Spark session setup
spark = SparkSession.builder \
    .appName("ETL Pipeline") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.5.0.jar") \
    .getOrCreate()

# PostgreSQL connection details
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_DB = "etl_db"
POSTGRES_USER = "etl_user"
POSTGRES_PASSWORD = "etl_password"

def load_to_postgres(df):
    """Load Spark DataFrame into PostgreSQL."""
    # Convert all column names to lowercase
    # df = df.toDF(*[col.lower() for col in df.columns])
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
        .option("dbtable", "laptop_phase3") \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

def main():
    # Step 1: Scrape Amazon Data
    # amazonScraper = AmazonScraper('./laptopUrls/amazon_laptop_urls.txt')
    # amazonScraper.run()

    # Step 2: Transform
    amazonCleaner = AmazonCleaner()
    amazonCleanedFilePath = amazonCleaner.cleanDataAndExport()
    # print(amazonCleanedFilePath)

    bestbuyCleaner = BestBuyCleaner()
    bestbuyCleanedFilePath = bestbuyCleaner.cleanDataAndExport()

    flipkartCleaner = FlipkartCleaner()
    flipkartCleanedFilePath = flipkartCleaner.cleanDataAndExport()

    combinedCleaner = CombinedCleaner()
    outputFilePath = combinedCleaner.cleanDataAndExport()

    # Step 3: Load To PostgreSQL
    # Load CSV file into a Spark DataFrame
    df = spark.read.option("header", "true").csv(outputFilePath)
    load_to_postgres(df)
    print("ETL Pipeline Completed")

if __name__ == "__main__":
    main()