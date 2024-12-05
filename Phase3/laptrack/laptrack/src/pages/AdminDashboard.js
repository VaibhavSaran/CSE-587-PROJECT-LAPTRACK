import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { plotGraphsForSpecs } from '../api';
import PriceStatsTable from '../components/PriceStatsTable';

const AdminDashboard = () => {
  const [priceStats,setPriceStats] = useState([])
    const [inputs, setInputs] = useState({
        processor: '',
        storage: '',
        screen_size: '',
        storage_type: '',
        RAM: '',
        top_n:10
      });
      const [graph, setGraph] = useState(null);
    
      const handleChange = (e) => {
        const { name, value } = e.target;
        setInputs((prev) => ({ ...prev, [name]: value }));
      };
    
      const fetchGraphAndStats = async () => {
        try {
          const response = await plotGraphsForSpecs(inputs)
          console.log(response);
          setPriceStats(response.price_stats)
          setGraph(response.graph);
        } catch (error) {
          console.error('Error fetching graph:', error);
        }
      };

  return (<><div>
    <h2>Price Variation Graph</h2>
    <form>
      <label>
        Processor:
        <input type="text" name="processor" value={inputs.processor} onChange={handleChange} />
      </label>
      <label>
        Storage:
        <input type="text" name="storage" value={inputs.storage} onChange={handleChange} />
      </label>
      <label>
        Screen Size:
        <input type="text" name="screen_size" value={inputs.screen_size} onChange={handleChange} />
      </label>
      <label>
        Storage Type:
        <input type="text" name="storage_type" value={inputs.storage_type} onChange={handleChange} />
      </label>
      <label>
        RAM:
        <input type="text" name="RAM" value={inputs.RAM} onChange={handleChange} />
      </label>
      <label>
        Top Brands:
        <input type="number" name="top_n" value={inputs.top_n} onChange={handleChange} />
      </label>
      <button type="button" onClick={fetchGraphAndStats}>Generate Graph</button>
    </form>

    {graph && <img src={`data:image/png;base64,${graph}`} alt="Price Variation Graph" />}
  </div>
  {priceStats.length>0? <PriceStatsTable priceStats={priceStats}/>:<></>}</>
    
  );
};

export default AdminDashboard;