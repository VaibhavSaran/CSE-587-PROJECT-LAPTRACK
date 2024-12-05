import React, { useEffect, useState } from 'react';
import LaptopCard from '../components/LaptopCard';
import { getLaptops } from '../api';
import './Homepage.css'

const HomePage = () => {
  const [laptops, setLaptops] = useState([]);

  useEffect(() => {
    const fetchLaptops = async () => {
      const data = await getLaptops(1,24);
      console.log(data);
      
      setLaptops(data.laptops);
    };

    fetchLaptops();
  }, []);

  return (
    <div className="laptop-grid">
      {laptops.length > 0 ? (
        laptops.map(laptop => (
          <LaptopCard key={laptop.id} laptop={laptop} />
        ))
      ) : (
        <p>Loading laptops...</p>
      )}
    </div>
  );
};

export default HomePage;