import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getBuyingOptions, getLaptopById } from '../api';
import SimilarProducts from './SimilarProducts';
import BuyingOptions from './BuyingOptions';
import './LaptopDetail.css'

const LaptopDetail = () => {
  const { id } = useParams();
  const [laptop, setLaptop] = useState(null);
  const [buyingOptions, setBuyingOptions] = useState([])

  useEffect(() => {
    const fetchLaptopDetails = async () => {
      const data = await getLaptopById(id);
      console.log(data);

      setLaptop(data);
    };

    fetchLaptopDetails();
  }, [id]);

  useEffect(() => {
    if (!laptop) return;
    const fetchBuyingOptions = async () => {
      console.log(laptop);

      var obj = {
        model_name: laptop.laptop_model_name,
        model_number: laptop.laptop_model_number,
        ram_size: laptop.ram_gb,
        storage_capacity: laptop.storage_capacity_gb,
        brand: laptop.brand
      }
      const data = await getBuyingOptions(obj)
      setBuyingOptions(data)
    }
    fetchBuyingOptions()
  }, [laptop])

  if (!laptop) return <p>Loading details...</p>;

  return (
    <div className="laptop-detail" style={{ padding: '5%', paddingTop: '1%' }}>
      <h1>{laptop.laptop_model_name} ({laptop.laptop_model_number})</h1>
      <div className="laptop-info">
        <div className="laptop-image">
          {/* You can add an image of the laptop here */}
          <img
            src={laptop.image_src}
            alt={laptop.laptop_model_name}
            width="400"
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
          {laptop.laptop_weight_pounds ? (<p><strong>Weight:</strong> {laptop.laptop_weight_pounds.toFixed(2)} lbs</p>) : <></>}
          {laptop.laptop_dimensions ? (<p><strong>Dimensions:</strong> {laptop.laptop_dimensions}</p>) : <></>}
        </div>
      </div>
      <BuyingOptions buyingOptions={buyingOptions} />
      <SimilarProducts laptopId={laptop.id} />
    </div>
  );
};

export default LaptopDetail;