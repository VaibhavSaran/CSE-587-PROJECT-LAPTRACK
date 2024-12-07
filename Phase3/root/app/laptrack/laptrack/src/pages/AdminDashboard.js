import React, { useEffect, useState } from 'react';
import { Tabs, Tab } from '@mui/material';
import { plotGraphsForSpecs, getLaptops, updateInventoryData, getLaptopsWithSorting } from '../api';
import PriceStatsTable from '../components/PriceStatsTable';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [priceStats, setPriceStats] = useState([]);
  const [totalPages,setTotalPages] = useState(1)
  const [inputs, setInputs] = useState({
    processor: '',
    storage: '',
    screen_size: '',
    storage_type: '',
    RAM: '',
    top_n: 10,
  });
  const [graph, setGraph] = useState(null);
  const [inventoryData, setInventoryData] = useState([]);

  const changePage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // Generate pagination buttons
  const getPaginationButtons = () => {
    const buttons = [];
    if (currentPage > 3) buttons.push(1); // Always show the first page
    if (currentPage > 4) buttons.push("..."); // Add ellipsis for skipped pages

    // Show the two pages before and after the current page
    for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
      buttons.push(i);
    }

    if (currentPage < totalPages - 3) buttons.push("..."); // Add ellipsis for skipped pages
    if (currentPage < totalPages - 2) buttons.push(totalPages); // Always show the last page

    return buttons;
  };

  useEffect(() => {
    if (activeTab === 1) {
      loadInventoryData(currentPage);
    }
  }, [activeTab,currentPage]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInputs((prev) => ({ ...prev, [name]: value }));
  };

  const fetchGraphAndStats = async () => {
    try {
      const response = await plotGraphsForSpecs(inputs);
      setPriceStats(response.price_stats);
      setGraph(response.graph);
    } catch (error) {
      console.error('Error fetching graph:', error);
    }
  };

  const loadInventoryData = async (currentPage) => {
    try {
      const data = await getLaptopsWithSorting(currentPage,24,'no_of_reviews','desc');
      setInventoryData(data.laptops);
      setTotalPages(data.pages)
    } catch (error) {
      console.error('Error fetching inventory data:', error);
    }
  };

  const handleEdit = (id) => {
    setInventoryData((prev) =>
      prev.map((row) =>
        row.id === id ? { ...row, isEditing: !row.isEditing } : row
      )
    );
  };

  const handleDelete = (id) => {
    setInventoryData((prev) =>
      prev.map((row) =>
        row.id === id ? { ...row, isEditing: !row.isEditing } : row
      )
    );
  };

  const handleSave = async (id) => {
    const row = inventoryData.find((row) => row.id === id);
    try {
      await updateInventoryData(id, row);
      setInventoryData((prev) =>
        prev.map((row) =>
          row.id === id ? { ...row, isEditing: false } : row
        )
      );
      alert('Inventory updated successfully!');
    } catch (error) {
      console.error('Error updating inventory:', error);
    }
  };

  const handleFieldChange = (id, field, value) => {
    setInventoryData((prev) =>
      prev.map((row) =>
        row.id === id ? { ...row, [field]: value } : row
      )
    );
  };

  const renderPricePredictor = () => (
    <div>
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
      {priceStats.length > 0 && <PriceStatsTable priceStats={priceStats} />}
    </div>
  );

  // const keyOrder = ['id','brand','laptop_model_name','laptop_model_number','processor_brand','processor_model','storage_type','operating_system',
  //   'display_resolution','extracted_rating','battery_life_hours_upto','storage_capacity_gb','display_size_inches','ram_gb','no_of_reviews','laptop_dimensions',
  // 'laptop_weight_pounds','time_of_extraction','price','source','stock']
  const keyOrder = ['id','brand','laptop_model_name','laptop_model_number','processor_brand','processor_model','storage_type','operating_system',
    'display_resolution','extracted_rating','battery_life_hours_upto','storage_capacity_gb','display_size_inches','ram_gb','no_of_reviews','laptop_dimensions',
  'laptop_weight_pounds','time_of_extraction','url','image_src','price','source','stock']

  const truncatableFields = ["url", "image_src"];


  const renderInventoryManager = () => (
    <div>
      <h2>Manage Inventory</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Brand</th>
            <th>Model Name</th>
            <th>Model Number</th>
            <th>Processor Brand</th>
            <th>Processor Model</th>
            <th>Storage Type</th>
            <th>OS</th>
            <th>Display Resolution</th>
            <th>Rating</th>
            <th>Battery Life (hrs)</th>
            <th>Storage (GB)</th>
            <th>Display (inches)</th>
            <th>RAM (GB)</th>
            <th>Reviews</th>
            <th>Dimensions</th>
            <th>Weight (lbs)</th>
            <th>Extraction Time</th>
            <th>URL</th> 
            <th>Image</th>
            <th>Price</th>
            <th>Source</th>
            <th>Stock</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {inventoryData.map((row) => (
            <tr key={row.id}>
              {keyOrder
                .filter((key) => key !== 'isEditing')
                .map((key) => (
                  <td key={row} className={truncatableFields.includes(row) ? "truncate" : ""}
                  title={truncatableFields.includes(row) ? row[row] : undefined}>
                    {row.isEditing ? (
                      <input
                        type="text"
                        value={row[key]}
                        onChange={(e) =>
                          handleFieldChange(row.id, key, e.target.value)
                        }
                      />
                    ) : (
                      row[key]
                    )}
                  </td>
                ))}
              <td>
                {row.isEditing ? (
                  <button onClick={() => handleSave(row.id)}>Save</button>
                ) : (
                  <button onClick={() => handleEdit(row.id)}>Edit</button>
                )}
                <button style={{'backgroundColor':'red'}} onClick={() => handleDelete(row.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* Pagination Controls */}
      <div className="pagination-container">
        {getPaginationButtons().map((btn, index) =>
          btn === "..." ? (
            <span key={index} className="pagination-ellipsis">
              ...
            </span>
          ) : (
            <button
              key={index}
              onClick={() => changePage(btn)}
              className={`pagination-button ${currentPage === btn ? "active" : ""}`}
            >
              {btn}
            </button>
          )
        )}
      </div>
    </div>
  );

  return (
    <div>
      <Tabs value={activeTab} onChange={(e, val) => setActiveTab(val)}>
        <Tab label="Price Analysis" />
        <Tab label="Manage Inventory" />
      </Tabs>
      {activeTab === 0 && renderPricePredictor()}
      {activeTab === 1 && renderInventoryManager()}
    </div>
  );
};

export default AdminDashboard;