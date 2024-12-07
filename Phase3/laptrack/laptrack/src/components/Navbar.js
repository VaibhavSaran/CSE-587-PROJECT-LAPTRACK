import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom'; // Assuming you're using React Router
import './Navbar.css'
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const [user,setUser] = useState('')
  const navigate = useNavigate();

  useEffect(() => {
    // Listen for auth changes
    const handleAuthChange = () => {
      console.log(localStorage.getItem('userRole'));
      
      setUser(localStorage.getItem('userRole'));
    };

    // Add event listener
    window.addEventListener('authChange', handleAuthChange);

    // Cleanup listener
    return () => {
      window.removeEventListener('authChange', handleAuthChange);
    };
  }, []);

const handleLogout = (e) =>{
  e.preventDefault()
  console.log('Here');
  const role = localStorage.getItem('userRole');
    console.log(role);
  localStorage.removeItem('userRole')
  setUser('')
  navigate('/login')
}

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link style={{color:'white',textDecoration:'none'}} to="/">Laptrack</Link>
      </div>
      <ul className="navbar-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/about">About</Link></li>
        <li><Link to="/contact">Contact</Link></li>
        {user === 'admin'? <li><Link to="/admin-dashboard">Admin Dashboard</Link></li> : <></>}
        {user === 'admin'? <li><Link to="/price-predictor">Price Predictor</Link></li> : <></>}
        <li><Link to="/login" onClick={handleLogout}>{user? 'Logout':'Login'}</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;