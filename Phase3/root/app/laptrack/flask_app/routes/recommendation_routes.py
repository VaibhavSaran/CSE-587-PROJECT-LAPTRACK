from flask import jsonify, request
from app import app, db
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from models.laptop import Laptop
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
import base64
from utils.ml_utils import load_ml_models

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

areMLModelsLoaded = False
try:
    print("Current Working Directory:", os.getcwd())
    ml_folder_path = './flask_app/ml/'
    models, scaler, label_encoders = load_ml_models(ml_folder_path)
    areMLModelsLoaded = True
except Exception as e:
    print(f"Failed to load ML models: {e}")

@app.route('/predict-price', methods=['POST'])
def predict_price():
    try:

        if not areMLModelsLoaded:
            return jsonify({'error': 'Failed to fetch ML Models'}), 500
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