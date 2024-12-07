import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css'

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Consider moving this to a more secure configuration
  const users = {
    user: { email: 'user@example.com', password: 'user123', role: 'user' },
    admin: { email: 'admin@example.com', password: 'admin123', role: 'admin' },
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Simulate an async login process
      await new Promise(resolve => setTimeout(resolve, 500));

      const user = Object.values(users).find(
        (u) => u.email === email && u.password === password
      );

      if (user) {
        // More comprehensive authentication storage
        localStorage.setItem('userRole', user.role);
        localStorage.setItem('isAuthenticated', 'true');

        // Optional: Store user info without sensitive data
        localStorage.setItem('userInfo', JSON.stringify({
          email: user.email,
          role: user.role
        }));
        window.dispatchEvent(new Event('authChange'))
        // Redirect based on role
        switch (user.role) {
          case 'admin':
            navigate('/admin-dashboard');
            break;
          case 'user':
            navigate('/');
            break;
          default:
            navigate('/dashboard');
        }
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Login to Laptrack</h2>
        <form onSubmit={handleSubmit} style={{display:'contents'}}>
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              autoComplete="email"
              disabled={isLoading}
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}

          <div className="button-group">
            <button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </form>

        <div className="login-footer">
          <p>
            <a href="/forgot-password">Forgot Password?</a>
          </p>
          <p>
            Don't have an account? <a href="/register">Sign Up</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;