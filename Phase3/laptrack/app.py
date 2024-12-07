from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from difflib import SequenceMatcher
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os
import pickle
import cloudpickle
import sklearn

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://etl_user:etl_password@postgres_container:5432/etl_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route('/laptops', methods=['GET'])
def get_laptops():
    page = request.args.get('page', 1, type=int)  # Default page is 1
    per_page = request.args.get('limit', 24, type=int)  # Default items per page is 10
    sort_by = request.args.get('sortBy', None)  # Default is None (no sorting)
    order = request.args.get('order', 'asc').lower()  # Default order is ascending

    # laptops = Laptop.query.paginate(page=page, per_page=per_page, error_out=False)

    # Define a mapping for allowed sort fields to avoid SQL injection
    allowed_sort_fields = {
        'brand': Laptop.brand,
        'price': Laptop.price,
        'ram_gb': Laptop.ram_gb,
        'storage_capacity_gb': Laptop.storage_capacity_gb,
        'extracted_rating': Laptop.extracted_rating,
        'time_of_extraction': Laptop.time_of_extraction,
        'no_of_reviews':Laptop.no_of_reviews
    }

    # Apply sorting if sortBy is provided and valid
    query = Laptop.query
    if sort_by and sort_by in allowed_sort_fields:
        if order == 'desc':
            query = query.order_by(allowed_sort_fields[sort_by].desc())
        else:  # Default to ascending
            query = query.order_by(allowed_sort_fields[sort_by])

    laptops = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'laptops': [laptop.to_dict() for laptop in laptops.items],
        'total': laptops.total,
        'pages': laptops.pages,
        'current_page': laptops.page
    })

@app.route('/laptops/<int:id>', methods=['GET'])
def get_laptop_by_id(id):
    laptop = Laptop.query.get(id)
    if laptop is None:
        return jsonify({'error': 'Laptop not found'}), 404
    return jsonify(laptop.to_dict())

# Function to normalize model numbers
def normalize_model_number(model):
    model = str(model).lower()  # Convert to lowercase
    model = re.sub(r'\s+', '', model)  # Remove spaces
    model = re.sub(r'[^a-z0-9]', '', model)  # Remove non-alphanumeric characters
    return model

@app.route('/laptops/grouped', methods=['GET'])
def get_grouped_laptops():
    # Retrieve all laptops from the database
    laptops = Laptop.query.all()

    # Step 1: Normalize the model numbers
    def normalize_model_number(model):
        model = str(model).lower()  # Convert to lowercase
        model = re.sub(r'\s+', '', model)  # Remove spaces
        model = re.sub(r'[^a-z0-9]', '', model)  # Remove non-alphanumeric characters
        return model

    # Create a list of dictionaries from database objects
    laptops_data = [
        {
        **vars(laptop),  # Include all attributes of the laptop
        "normalized_model": normalize_model_number(laptop.laptop_model_number)
        }
        for laptop in laptops
    ]

    # Step 2: Group laptops by similarity in normalized model numbers
    grouped_laptops = []  # List of groups

    for laptop in laptops_data:
        match_found = False

        for group in grouped_laptops:
            if SequenceMatcher(None, laptop['normalized_model'], group['normalized_model']).ratio() >= 0.9:  # Similarity threshold
                group['laptops'].append(laptop)
                group['original_model_numbers'].append(laptop['laptop_model_number'])
                match_found = True
                break

        if not match_found:
            # Create a new group
            grouped_laptops.append(grouped_laptops.append({
        "normalized_model": laptop["normalized_model"],
        "original_model_numbers": [laptop["laptop_model_number"]],
        "laptops": [laptop]
        }))

    # Step 3: Format response for output
    response = [
        {
            "model_numbers": group["original_model_numbers"],
            "laptops": group["laptops"]
        }
        for group in grouped_laptops
    ]

    # Step 4: Apply Pagination
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Pagination logic
    start = (page - 1) * per_page
    end = start + per_page
    paginated_response = response[start:end]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_groups": len(response),
        "total_pages": -(-len(response) // per_page),  # Calculate total pages
        "data": paginated_response
    })

@app.route('/get_recommendations/<int:laptop_id>', methods=['GET'])
def get_recommendations(laptop_id,price_tolerance=0.2, top_n=10):
    
    # Query all laptops for specs
    laptops = Laptop.query.all()
    laptops_list = [laptop.to_dict() for laptop in laptops]
    laptops_df = pd.DataFrame(laptops_list)
    
    # Combine specifications into a single column for each laptop
    laptops_df['specs'] = laptops_df['processor_brand'] + ' ' + \
                          laptops_df['processor_model'] + ' ' + \
                          laptops_df['ram_gb'].astype(str) + ' GB ' + \
                          laptops_df['storage_capacity_gb'].astype(str) + ' GB ' + \
                          laptops_df['storage_type'] + ' ' + \
                          laptops_df['operating_system']
    
    laptops_df['specs'] = laptops_df['specs'].fillna('')

    # Initialize TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the specs column to get the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(laptops_df['specs'])
    
    # Calculate cosine similarity between all laptops
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Get the index of the selected laptop
    selected_idx = laptops_df[laptops_df['id'] == laptop_id].index[0]
    
    # Get similarity scores for the selected laptop
    sim_scores = list(enumerate(cosine_sim[selected_idx]))
    
    # Sort the laptops based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # # Get the top 10 most similar laptops (excluding the laptop itself)
    # sim_scores = sim_scores[1:11]
    # laptop_indices = [i[0] for i in sim_scores]
    
    # # Get the recommended laptop IDs
    # recommended_laptops = laptops_df['id'].iloc[laptop_indices].tolist()

    # Get the IDs of the most similar laptops (excluding the selected laptop)
    similar_laptops = [x[0] for x in sim_scores if x[0] != selected_idx]

    # Extract price of the selected laptop
    selected_price = laptops_df.iloc[selected_idx]['price']
    # Extract model name and number of the selected laptop
    selected_model_name = laptops_df.iloc[selected_idx]['laptop_model_name']
    selected_model_number = laptops_df.iloc[selected_idx]['laptop_model_number']

    # Calculate price difference
    price_differences = np.abs(laptops_df.iloc[similar_laptops]['price'].values - selected_price)

    # Normalize the price differences for weighting
    price_scaler = MinMaxScaler()
    normalized_price_differences = price_scaler.fit_transform(price_differences.reshape(-1, 1))

    # Filter laptops by price tolerance (e.g., ±20% of the selected price)
    filtered_laptops = []
    for idx, price_diff in zip(similar_laptops, normalized_price_differences):
        if price_diff <= price_tolerance:
            model_name = laptops_df.iloc[idx]['laptop_model_name']
            model_number = laptops_df.iloc[idx]['laptop_model_number']
            if model_name != selected_model_name and model_number != selected_model_number:
                filtered_laptops.append(idx)

    # Get the top N similar laptops based on both content and price similarity
    recommended_laptops = filtered_laptops[:top_n]
    
    # Extract the recommended laptop IDs (use the index for the IDs)
    recommended_laptop_ids = laptops_df.iloc[recommended_laptops]['id'].tolist()

    # Query the database again to fetch only the recommended laptops by their IDs
    recommended_laptops_data = Laptop.query.filter(Laptop.id.in_(recommended_laptop_ids)).all()

    # Convert the recommended laptops to a dictionary format for the response
    recommendations = [laptop.to_dict() for laptop in recommended_laptops_data]
    
    return jsonify({'recommended_laptops': recommendations})

@app.route('/plot-price-variation', methods=['POST'])
def plot_price_variation():

    # Query all laptops for specs
    laptops = Laptop.query.all()
    laptops_list = [laptop.to_dict() for laptop in laptops]
    laptops_df = pd.DataFrame(laptops_list)
    print('DF size',laptops_df.shape)

    # Get user input from the request
    data = request.json
    specific_processor = data.get('processor')
    specific_storage = int(data.get('storage')) if data.get('storage') else None
    specific_screen_size = float(data.get('screen_size')) if data.get('screen_size') else None
    specific_storage_type = data.get('storage_type')
    specific_RAM = int(data.get('RAM')) if data.get('RAM') else None
    top_n = int(data.get('top_n'))
    
    print(top_n)
    # Filter the DataFrame
    if top_n:
        top_n_brands = laptops_df['brand'].value_counts().head(top_n).index.tolist()
        filtered_df = laptops_df[laptops_df['brand'].isin(top_n_brands)]
        print(filtered_df.head())
    else:
        filtered_df = laptops_df
    # filtered_df = laptops_df
    print(filtered_df.columns)
    if specific_processor:
        print('1')
        filtered_df = filtered_df[filtered_df['processor_model'] == specific_processor]
        print('DF size',filtered_df.shape)
    if specific_storage:
        print('2')
        filtered_df = filtered_df[filtered_df['storage_capacity_gb'] == specific_storage]
        print('DF size',filtered_df.shape)
    if specific_screen_size:
        print('3')
        filtered_df = filtered_df[filtered_df['display_size_inches'] == specific_screen_size]
        print('DF size',filtered_df.shape)
    if specific_storage_type:
        print('4')
        filtered_df = filtered_df[filtered_df['storage_type'] == specific_storage_type]
        print('DF size',filtered_df.shape)
    if specific_RAM:
        print('5')
        filtered_df = filtered_df[filtered_df['ram_gb'] == specific_RAM]
        print('DF size',filtered_df.shape)

    if filtered_df.empty:
        return jsonify({'error': 'No data available for the specified filters.'}), 400

    # Create the plot
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=filtered_df, x='brand', y='price')
    plt.xticks(rotation=90)
    plt.ylabel('Price')
    plt.xlabel('Laptop Brand')
    plt.tight_layout()

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Encode the image to base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    print(filtered_df.describe())

    # Clean the data
    filtered_df = filtered_df.dropna(subset=['brand', 'price'])
    filtered_df['price'] = pd.to_numeric(filtered_df['price'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['price'])

    # Calculate min, max, and average price per brand
    price_stats = filtered_df.groupby('brand')['price'].agg(
        min_price='min', 
        max_price='max', 
        avg_price='mean'
    ).reset_index()

    # Convert the result to a dictionary for easy return as JSON
    price_stats_dict = price_stats.to_dict(orient='records')

    return jsonify({'graph': image_base64,'price_stats': price_stats_dict})

@app.route('/find-laptops', methods=['POST'])
def find_laptops():
    # Get the user input from the request
    data = request.json
    model_name = data.get('model_name')
    model_number = data.get('model_number')
    ram_size = data.get('ram_size')
    storage_capacity = data.get('storage_capacity')
    brand = data.get('brand')


    matching_laptops = Laptop.query.filter(
        Laptop.laptop_model_number == model_number,
        Laptop.ram_gb == ram_size,
        Laptop.storage_capacity_gb == storage_capacity,
        Laptop.brand == brand
    ).all()

    more_matching_laptops = Laptop.query.filter(
        Laptop.laptop_model_name == model_name,
        Laptop.ram_gb == ram_size,
        Laptop.storage_capacity_gb == storage_capacity,
        Laptop.brand == brand
    ).all()
    all_laptops = matching_laptops + more_matching_laptops

    # Sort the combined list by 'time_of_extraction' in descending order
    all_laptops_sorted = sorted(all_laptops, key=lambda laptop: laptop.time_of_extraction, reverse=True)
       
    if not matching_laptops:
        return jsonify({'message': 'No matching laptops found in the database.'}), 404
    
    # Prepare a list of laptops with their details
    laptops_data = []
    laptopIDs = set()
    unique_source = set()
    for laptop in all_laptops_sorted:
        laptop_dict = laptop.to_dict()
        laptop_id = laptop_dict.get('id')
        laptop_source = laptop_dict.get('source')
        if laptop_id not in laptopIDs and laptop_source not in unique_source:
            laptops_data.append(laptop_dict)
            laptopIDs.add(laptop_id)
            unique_source.add(laptop_source)
    
    return jsonify({'buying_options': laptops_data}), 200

def custom_load_model(filepath):
    def custom_random_state_ctor(seed=None):
        if seed is None:
            return np.random.RandomState()
        return np.random.RandomState(seed)

    # Temporarily patch the random state constructor
    original_check_random_state = sklearn.utils.check_random_state

    try:
        # Monkey patch the random state constructor
        sklearn.utils.check_random_state = custom_random_state_ctor

        # Try standard pickle first
        with open(filepath, 'rb') as file:
            model = pickle.load(file)
        return model

    except Exception as e:
        try:
            # Try cloudpickle as a fallback
            with open(filepath, 'rb') as file:
                model = cloudpickle.load(file)
            return model

        except Exception as load_error:
            print(f"Error loading {filepath}: {load_error}")
            raise

    finally:
        # Restore the original random state constructor
        sklearn.utils.check_random_state = original_check_random_state

ml_folder_path = './ml/'
# Load models
models = {}
model_files = [f for f in os.listdir(ml_folder_path) if f.endswith('_model.pkl')]
for model_file in model_files:
    model_name = model_file.replace('_model.pkl', '')
    filepath = os.path.join(ml_folder_path, model_file)
    print(f"Loading model: {model_file}")
    models[model_name] = custom_load_model(filepath)

# Load scaler
scaler = custom_load_model(f'{ml_folder_path}scaler.pkl')

# Load label encoders
label_encoders = custom_load_model(f'{ml_folder_path}label_encoders.pkl')

@app.route('/predict-price', methods=['POST'])
def predict_price():
    try:
        # Get the input data from the request
        data = request.get_json()

        # Define expected numerical and categorical features
        numerical_features = [
            'Storage_Capacity(GB)', 'RAM(GB)', 'Display_Size(Inches)',
            'Extracted_Rating', 'Laptop_Weight(Pounds)'
        ]
        categorical_features = [
            'Processor_Model', 'Brand', 'Storage_Type', 'Operating_System'
        ]

        # Prepare the input data for the model
        input_data = {
            'Storage_Capacity(GB)': data['storage_capacity'],
            'RAM(GB)': data['ram_gb'],
            'Display_Size(Inches)': data['display_size'],
            'Processor_Model': data['processor_model'],
            'Brand': data['brand'],
            'Storage_Type': data['storage_type'],
            'Operating_System': data['operating_system'],
            'Laptop_Weight(Pounds)': data['laptop_weight'],
            'Extracted_Rating': data['extracted_rating']
        }

        # Create DataFrame and ensure all required columns exist
        input_df = pd.DataFrame([input_data])

        # Add missing numerical columns with training defaults
        for col in numerical_features:
            if col not in input_df.columns:
                input_df[col] = 0  # Replace 0 with appropriate default values

        # Transform categorical features
        for col in categorical_features:
            if col in input_df.columns:
                input_df[col] = input_df[col].apply(
                    lambda x: label_encoders[col].transform([x])[0] 
                    if x in label_encoders[col].classes_ 
                    else label_encoders[col].transform([label_encoders[col].classes_[0]])[0]
                )
            else:
                input_df[col] = label_encoders[col].transform([label_encoders[col].classes_[0]])[0]

        # Ensure columns are in the correct order for the scaler
        input_df = input_df[numerical_features + categorical_features]

        # Scale numerical features
        input_df[numerical_features] = scaler.transform(input_df[numerical_features])

        # Generate predictions
        predictions = {}
        for name, model in models.items():
            predictions[name] = float(model.predict(input_df)[0])  # Ensure JSON serializability

        # Return the predicted price
        return jsonify({'predicted_price': predictions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/laptops/<int:laptop_id>', methods=['PUT'])
def update_laptop(laptop_id):
    # Get the laptop from the database
    laptop = Laptop.query.get(laptop_id)

    if not laptop:
        return jsonify({'error': 'Laptop not found'}), 404

    # Get the data from the request
    data = request.json

    # Update the fields if present in the request
    for key, value in data.items():
        if hasattr(laptop, key):
            setattr(laptop, key, value)

    try:
        # Commit the changes to the database
        db.session.commit()
        return jsonify({'message': 'Laptop updated successfully', 'laptop': laptop.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update laptop', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)  # Listen on all interfaces in the container