import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/Homepage';
import LaptopDetail from './components/LaptopDetail';
import Layout from './layout/Layout';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import LoginPage from './pages/LoginPage'
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoutes';
import PricePredictor from './pages/PricePredictor';

const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/admin-dashboard" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
          <Route path="/price-predictor" element={<ProtectedRoute><PricePredictor /></ProtectedRoute>} />
          <Route path="/laptop/:id" element={<LaptopDetail />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;