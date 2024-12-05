import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getLaptopById } from '../api';
import SimilarProducts from './SimilarProducts';

const LaptopDetail = () => {
  const { id } = useParams();
  const [laptop, setLaptop] = useState(null);

  useEffect(() => {
    const fetchLaptopDetails = async () => {
      const data = await getLaptopById(id);
      console.log(data);
      
      setLaptop(data);
    };

    fetchLaptopDetails();
  }, [id]);

  if (!laptop) return <p>Loading details...</p>;

  return (
    <div className="laptop-detail" style={{padding:'5%',paddingTop:'1%'}}>
      <h1>{laptop.laptop_model_name} ({laptop.laptop_model_number})</h1>
      <div className="laptop-info">
        <div className="laptop-image">
          {/* You can add an image of the laptop here */}
          <img
            src="https://via.placeholder.com/300"
            alt={laptop.laptop_model_name}
            width="300"
          />
        </div>

        <div className="laptop-details">
          <p><strong>Brand:</strong> {laptop.brand}</p>
          <p><strong>Processor:</strong> {laptop.processor_brand} - {laptop.processor_model}</p>
          <p><strong>RAM:</strong> {laptop.ram_gb} GB</p>
          <p><strong>Storage:</strong> {laptop.storage_capacity_gb} GB {laptop.storage_type}</p>
          <p><strong>Operating System:</strong> {laptop.operating_system}</p>
          <p><strong>Display:</strong> {laptop.display_size_inches} inches - {laptop.display_resolution}</p>
          <p><strong>Battery Life:</strong> {laptop.battery_life_hours_upto ? `${laptop.battery_life_hours_upto} hours` : 'N/A'}</p>
          <p><strong>Weight:</strong> {laptop.laptop_weight_pounds} lbs</p>
          <p><strong>Dimensions:</strong> {laptop.laptop_dimensions}</p>
          <p><strong>Price:</strong> ${laptop.price}</p>
          <p><strong>Rating:</strong> {laptop.extracted_rating} / 5 ({laptop.no_of_reviews} reviews)</p>
          <p><strong>In Stock:</strong> {laptop.stock ? 'Yes' : 'No'}</p>
          <p><strong>Source:</strong> {laptop.source}</p>
          <p><strong>Time of Extraction:</strong> {new Date(laptop.time_of_extraction).toLocaleString()}</p>
          <a href={laptop.url} target="_blank" rel="noopener noreferrer">View on Amazon</a>
        </div>
      </div>

      <SimilarProducts laptopId={laptop.id}/>
    </div>
  );
};

export default LaptopDetail;