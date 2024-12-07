class Config:
    # PostgreSQL database configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://etl_user:etl_password@postgres_container:5432/etl_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False