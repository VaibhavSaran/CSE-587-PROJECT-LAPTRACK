import React from 'react'

function PriceStatsTable({ priceStats }) {
  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h2>Price Statistics per Brand</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Brand</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Min Price</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Max Price</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Average Price</th>
          </tr>
        </thead>
        <tbody>
          {priceStats.map((stat, index) => (
            <tr key={index}>
              <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>{stat.brand}</td>
              <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>${stat.min_price.toFixed(2)}</td>
              <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>${stat.max_price.toFixed(2)}</td>
              <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>${stat.avg_price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PriceStatsTable