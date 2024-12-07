from pyspark.sql import SparkSession
from amazonScraper import AmazonScraper
from amazonCleaner import AmazonCleaner
from BestBuyCleaner import BestBuyCleaner
from FlipkartCleaner import FlipkartCleaner
from combinedCleaner import CombinedCleaner
import psycopg2
from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType, IntegerType, TimestampType

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

# SQL for creating the laptop table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS laptop (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(255),
    laptop_model_name VARCHAR(255),
    laptop_model_number VARCHAR(255),
    processor_brand VARCHAR(255),
    processor_model VARCHAR(255),
    storage_type VARCHAR(255),
    operating_system VARCHAR(255),
    display_resolution VARCHAR(255),
    extracted_rating DOUBLE PRECISION,
    battery_life_hours_upto DOUBLE PRECISION,
    price DOUBLE PRECISION,
    stock VARCHAR(255),
    time_of_extraction TIMESTAMP,
    url VARCHAR(1000),
    source VARCHAR(255),
    storage_capacity_gb INTEGER,
    display_size_inches DOUBLE PRECISION,
    ram_gb INTEGER,
    no_of_reviews INTEGER,
    laptop_dimensions VARCHAR(255),
    laptop_weight_pounds DOUBLE PRECISION,
    image_src VARCHAR(1000)
);
"""

schema = StructType([
    StructField("brand", StringType(), True),
    StructField("laptop_model_name", StringType(), True),
    StructField("laptop_model_number", StringType(), True),
    StructField("processor_brand", StringType(), True),
    StructField("processor_model", StringType(), True),
    StructField("storage_type", StringType(), True),
    StructField("operating_system", StringType(), True),
    StructField("display_resolution", StringType(), True),
    StructField("extracted_rating", FloatType(), True),
    StructField("battery_life_hours_upto", FloatType(), True),
    StructField("price", FloatType(), True),
    StructField("stock", BooleanType(), True),
    StructField("time_of_extraction", TimestampType(), True),
    StructField("url", StringType(), True),
    StructField("source", StringType(), True),
    StructField("storage_capacity_gb", IntegerType(), True),
    StructField("display_size_inches", FloatType(), True),
    StructField("ram_gb", IntegerType(), True),
    StructField("no_of_reviews", IntegerType(), True),
    StructField("laptop_dimensions", StringType(), True),
    StructField("laptop_weight_pounds", FloatType(), True),
    StructField("image_src", StringType(), True)
])

def initPostgreSQL():
    """Initialize PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        # Automatically commit after each command
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        return (conn, cur)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

def load_to_postgres(conn, cur, df):
    """Load Spark DataFrame into PostgreSQL."""
    
    try:
        # Ensure the table exists
        cur.execute(CREATE_TABLE_SQL)

        # Use Spark to write the DataFrame to PostgreSQL
        df.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
            .option("dbtable", "laptop") \
            .option("user", POSTGRES_USER) \
            .option("password", POSTGRES_PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
    
    except Exception as e:
        print(f"Error in load_to_postgres: {e}")
        raise
    finally:
        # Close PostgreSQL connection
        if cur:
            cur.close()
        if conn:
            conn.close()

def load_to_postgres(conn,cur,df):
    """Load Spark DataFrame into PostgreSQL."""
    
    # Create the table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS laptop (
        id SERIAL PRIMARY KEY,
        brand VARCHAR(255),
        laptop_model_name VARCHAR(255),
        laptop_model_number VARCHAR(255),
        processor_brand VARCHAR(255),
        processor_model VARCHAR(255),
        storage_type VARCHAR(255),
        operating_system VARCHAR(255),
        display_resolution VARCHAR(255),
        extracted_rating DOUBLE PRECISION,
        battery_life_hours_upto DOUBLE PRECISION,
        price DOUBLE PRECISION,
        stock VARCHAR(255),
        time_of_extraction TIMESTAMP,
        url VARCHAR(1000),
        source VARCHAR(255),
        storage_capacity_gb INTEGER,
        display_size_inches DOUBLE PRECISION,
        ram_gb INTEGER,
        no_of_reviews INTEGER,
        laptop_dimensions VARCHAR(255),
        laptop_weight_pounds DOUBLE PRECISION,
        image_src VARCHAR(1000)
    );
    """
    cur.execute(create_table_sql)
    conn.commit()

    # Close PostgreSQL connection
    cur.close()
    conn.close()

    # Use Spark to write the DataFrame to PostgreSQL
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
        .option("dbtable", "laptop") \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
    
def isDBPopulated(conn, cur):
    """Check if the laptop table is populated."""
    try:
        # Check if the table exists first
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'laptop'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            return False
        
        # If table exists, check for records
        cur.execute("SELECT COUNT(*) FROM laptop")
        count = cur.fetchone()[0]
        return count > 0
    except psycopg2.Error as e:
        print(f"Error checking database population: {e}")
        return False

def main():

    # Initialize PostgreSQL connection
    conn, cur = initPostgreSQL()

    try:
        # Check if the database is already populated
        if isDBPopulated(conn, cur):
            print("Database already populated. Exiting.")
            return

    except Exception as e:
        print(f'Error checking database population: {e}')

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
    df = spark.read.option("header", "true").schema(schema).csv(outputFilePath)
    load_to_postgres(conn,cur,df)
    print("ETL Pipeline Completed")

if __name__ == "__main__":
    main()