from pyspark.sql import SparkSession
import psycopg2
import scraper  # Your scraping module
import cleaner  # Your cleaning module

# Spark session setup
spark = SparkSession.builder \
    .appName("ETL Pipeline") \
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
        .mode("overwrite") \
        .save()

def main():
    # Step 1: Extract
    raw_data = scraper.scrape()  # Replace with your scraping logic

    # Step 2: Transform
    cleaned_data = cleaner.clean(raw_data)  # Replace with your cleaning logic
    df = spark.createDataFrame(cleaned_data)  # Convert to Spark DataFrame

    # Step 3: Load
    load_to_postgres(df)
    print("ETL Pipeline Completed")

if __name__ == "__main__":
    main()