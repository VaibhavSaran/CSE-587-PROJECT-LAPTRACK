import React, { useEffect, useState } from 'react';
import LaptopCard from '../components/LaptopCard';
import { getLaptops } from '../api';
import './Homepage.css'

const HomePage = () => {
  const [laptops, setLaptops] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages,setTotalPages] = useState(1)
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

  const changePage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const fetchLaptops = async (currentPage) => {
    const data = await getLaptops(currentPage, 24);
    console.log(data);
    setTotalPages(data.pages)
    setLaptops(data.laptops);
  };

  useEffect(() => {
    
    fetchLaptops(currentPage);
  }, [currentPage]);

  return (<>
    <div className="laptop-grid">
      {laptops.length > 0 ? (
        laptops.map(laptop => (
          <LaptopCard key={laptop.id} laptop={laptop} />
        ))
      ) : (
        <p>Loading laptops...</p>
      )}
    </div>
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
      )}</div></>

  );
};

export default HomePage;