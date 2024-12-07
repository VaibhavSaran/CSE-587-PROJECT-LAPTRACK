import os
import pickle
import cloudpickle
import numpy as np
import sklearn

def custom_load_model(filepath):
    """
    Load a machine learning model from a specified file path.
    Tries to load using pickle first, then cloudpickle as a fallback.
    """
    def custom_random_state_ctor(seed=None):
        """Custom random state constructor."""
        return np.random.RandomState(seed) if seed is not None else np.random.RandomState()

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


def load_ml_models(ml_folder_path='./flask_app/ml/'):
    """
    Load all machine learning models, scalers, and encoders from the specified directory.
    
    Returns:
        models (dict): A dictionary of loaded models.
        scaler: The loaded scaler.
        label_encoders: The loaded label encoders.
    """
    models = {}
    try:
        # Load models
        model_files = [f for f in os.listdir(ml_folder_path) if f.endswith('_model.pkl')]
        for model_file in model_files:
            model_name = model_file.replace('_model.pkl', '')
            filepath = os.path.join(ml_folder_path, model_file)
            print(f"Loading model: {model_file}")
            models[model_name] = custom_load_model(filepath)

        # Load scaler and label encoders
        scaler = custom_load_model(os.path.join(ml_folder_path, 'scaler.pkl'))
        label_encoders = custom_load_model(os.path.join(ml_folder_path, 'label_encoders.pkl'))

        return models, scaler, label_encoders

    except Exception as e:
        print(f'Error loading ML Pickle files: {e}')
        raise
