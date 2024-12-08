from flask import jsonify, request
from app import app, db
from models.laptop import Laptop

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
