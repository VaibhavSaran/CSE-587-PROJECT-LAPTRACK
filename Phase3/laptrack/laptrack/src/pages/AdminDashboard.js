import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if the user is an admin
    const role = localStorage.getItem('userRole');
    if (role !== 'admin') {
      // Redirect non-admin users
      alert('Invalid User')
      navigate('/');
    }
  }, [navigate]);

  return (
    <div>
      <h2>Admin Dashboard</h2>
      <p>Welcome, Admin!</p>
    </div>
  );
};

export default AdminDashboard;