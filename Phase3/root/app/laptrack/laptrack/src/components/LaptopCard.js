import React from 'react';
import { Link } from 'react-router-dom';
import './LaptopCard.css';  // For custom styling

const LaptopCard = ({ laptop }) => {
  return (
    <div className="laptop-card">
      <img src={laptop.image_src} alt={laptop.name} className="laptop-card-image" />
      <h4>{laptop.brand} </h4>
      <h3>{laptop.laptop_model_name}</h3>
      {/* <p>Price: ${laptop.price}</p> */}
      <Link to={`/laptop/${laptop.id}`} className="view-details-btn">View Details</Link>
    </div>
  );
};

export default LaptopCard;