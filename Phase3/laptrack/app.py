from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://etl_user:etl_password@postgres_container:5432/etl_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Laptop model class
class Laptop(db.Model):
    __tablename__ = 'laptops'
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
            'laptop_weight_pounds': self.laptop_weight_pounds
        }

@app.route('/laptops', methods=['GET'])
def get_laptops():
    page = request.args.get('page', 1, type=int)  # Default page is 1
    per_page = request.args.get('per_page', 10, type=int)  # Default items per page is 10
    laptops = Laptop.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'laptops': [laptop.to_dict() for laptop in laptops.items],
        'total': laptops.total,
        'pages': laptops.pages,
        'current_page': laptops.page
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Listen on all interfaces in the container