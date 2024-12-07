from app import db

# Laptop model class
class Laptop(db.Model):
    __tablename__ = 'laptop'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(255))
    laptop_model_name = db.Column(db.String(255))
    laptop_model_number = db.Column(db.String(255))
    processor_brand = db.Column(db.String(255))
    processor_model = db.Column(db.String(255))
    storage_type = db.Column(db.String(255))
    operating_system = db.Column(db.String(255))
    display_resolution = db.Column(db.String(255))
    extracted_rating = db.Column(db.Float)
    battery_life_hours_upto = db.Column(db.Float)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Boolean, nullable=False)
    time_of_extraction = db.Column(db.TIMESTAMP)
    url = db.Column(db.Text)
    source = db.Column(db.String(255))
    storage_capacity_gb = db.Column(db.Integer, nullable=False)
    display_size_inches = db.Column(db.Float)
    ram_gb = db.Column(db.Integer, nullable=False)
    no_of_reviews = db.Column(db.Integer, nullable=False)
    laptop_dimensions = db.Column(db.String(255))
    laptop_weight_pounds = db.Column(db.Float)
    image_src = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'laptop_model_name': self.laptop_model_name,
            'laptop_model_number': self.laptop_model_number,
            'processor_brand': self.processor_brand,
            'processor_model': self.processor_model,
            'storage_type': self.storage_type,
            'operating_system': self.operating_system,
            'display_resolution': self.display_resolution,
            'extracted_rating': self.extracted_rating,
            'battery_life_hours_upto': self.battery_life_hours_upto,
            'price': self.price,
            'stock': self.stock,
            'time_of_extraction': self.time_of_extraction,
            'url': self.url,
            'source': self.source,
            'storage_capacity_gb': self.storage_capacity_gb,
            'display_size_inches': self.display_size_inches,
            'ram_gb': self.ram_gb,
            'no_of_reviews': self.no_of_reviews,
            'laptop_dimensions': self.laptop_dimensions,
            'laptop_weight_pounds': self.laptop_weight_pounds,
            'image_src':self.image_src
        }
