import React from 'react';
import './BuyingOptions.css'

const BuyingOptions = ({ buyingOptions }) => {
  return (
    <div className="buying-options-container">
      <h2>Buying Options</h2>
      <div className="buying-options-list">
        {buyingOptions && buyingOptions.length > 0 ? (
          buyingOptions.map((option) => (
            <div key={option.id} className="buying-option-card">
              <div className="buying-option-body">
                <p><strong>Source:</strong> {option.source}</p>
                <p><strong>Price:</strong> ${option.price.toFixed(2)}</p>
                <p><strong>Stock:</strong> {option.stock ? "In Stock" : "Out of Stock"}</p>
                <p><strong>Date Last Checked:</strong> {option.time_of_extraction}</p>
                <p><strong>Rating:</strong> {option.extracted_rating.toFixed(1)}/5 (from {option.no_of_reviews ? option.no_of_reviews : 0} reviews)</p>
              </div>
              <div className="buying-option-footer">
                <a href={option.url} target="_blank" rel="noopener noreferrer" className="buy-now-button">
                  Buy Now
                </a>
              </div>
            </div>
          ))
        ) : (
          <p>No buying options available for this laptop.</p>
        )}
      </div>
    </div>
  );
};

export default BuyingOptions;