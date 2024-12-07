import React, { useState } from 'react';
import './PricePredictor.css';
import { getPredictedPriceForSpecs } from '../api';

const PricePredictor = () => {
  const [formData, setFormData] = useState({
    storage_capacity: 2048,
    ram_gb: 16,
    display_size: 16,
    extracted_rating: 4.3,
    laptop_weight: 5.51,
    processor_model: 'Core i7',
    brand: 'ASUS',
    storage_type: 'SSD',
    operating_system: 'Windows 11',
  });

  const [predictedPrice, setPredictedPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await getPredictedPriceForSpecs(formData);
      setPredictedPrice(response); // Assuming the response has predicted_price field
    } catch (err) {
      setError('Error predicting price. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="price-predictor-container">
      <h2>Price Predictor</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Storage Capacity (GB):</label>
          <input
            type="number"
            name="storage_capacity"
            value={formData.storage_capacity}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>RAM (GB):</label>
          <input
            type="number"
            name="ram_gb"
            value={formData.ram_gb}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Display Size (Inches):</label>
          <input
            type="number"
            name="display_size"
            value={formData.display_size}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Extracted Rating:</label>
          <input
            type="number"
            name="extracted_rating"
            value={formData.extracted_rating}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Laptop Weight (Pounds):</label>
          <input
            type="number"
            name="laptop_weight"
            value={formData.laptop_weight}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Processor Model:</label>
          <input
            type="text"
            name="processor_model"
            value={formData.processor_model}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Brand:</label>
          <input
            type="text"
            name="brand"
            value={formData.brand}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Storage Type:</label>
          <input
            type="text"
            name="storage_type"
            value={formData.storage_type}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>Operating System:</label>
          <input
            type="text"
            name="operating_system"
            value={formData.operating_system}
            onChange={handleChange}
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Predicting...' : 'Predict Price'}
        </button>
      </form>

      {predictedPrice !== null && (
        <div className="results-container">
          <h3>Prediction Results:</h3>
          {Object.keys(predictedPrice).map((key) => (
            <div className="result" key={key}>
              <p>
                Predicted Price with <strong>{key}</strong> Model:
                <strong>${parseFloat(predictedPrice[key]).toFixed(2)}</strong>
              </p>
            </div>
          ))}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default PricePredictor;