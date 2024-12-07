import React, { useEffect, useState } from 'react';
import Slider from 'react-slick';
import LaptopCard from './LaptopCard'
import { getRecommendedLaptops } from '../api';
import './SimilarProducts.css'

const CustomPrevArrow = ({ onClick }) => (
  <button onClick={onClick} className="slick-prev">
    <span>&lt;</span>
  </button>
);

const CustomNextArrow = ({ onClick }) => (
  <button onClick={onClick} className="slick-next">
    <span>&gt;</span>
  </button>
);

// Similar Products Section Component
const SimilarProducts = ({ laptopId }) => {
  const [similarLaptops, setSimilarLaptops] = useState([]);

  useEffect(() => {
    const fetchRecommendedLaptops = async () => {
      const data = await getRecommendedLaptops(laptopId);

      setSimilarLaptops(data.recommended_laptops);
    };

    fetchRecommendedLaptops();
  }, [laptopId]);

  // Carousel settings
  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 3, // Show 3 cards at once
    slidesToScroll: 1,
    prevArrow: <CustomPrevArrow />, // Pass custom prev button
    nextArrow: <CustomNextArrow />, // Pass custom next button
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2, // Show 2 cards on medium screens
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1, // Show 1 card on small screens
          slidesToScroll: 1,
        },
      },
    ],
  };

  return (
    <div className="similar-products-section">
      <h2>Similar Products</h2>
      <Slider {...settings}>
        {similarLaptops.length > 0 ? (
          similarLaptops.slice(0, 10).map((laptop) => (
            <LaptopCard key={laptop.id} laptop={laptop} />
          ))
        ) : (
          <p>Loading...</p>
        )}
      </Slider>
    </div>
  );
};

export default SimilarProducts;