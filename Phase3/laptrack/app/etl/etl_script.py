from pyspark.sql import SparkSession
from amazonScraper import AmazonScraper
from amazonCleaner import AmazonCleaner

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
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
        .option("dbtable", "processed_data") \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

def main():
    # Step 1: Scrape Amazon Data
    amazonScraper = AmazonScraper('./laptopUrls/amazon_laptop_urls.txt')
    amazonScraper.run()

    # Step 2: Transform
    amazonCleaner = AmazonCleaner()
    amazonCleanedFilePath = amazonCleaner.cleanDataAndExport()
    print(amazonCleanedFilePath)

    # Step 3: Load To PostgreSQL
    # Load CSV file into a Spark DataFrame
    df = spark.read.option("header", "true").csv(amazonCleanedFilePath)
    load_to_postgres(df)
    print("ETL Pipeline Completed")

if __name__ == "__main__":
    main()