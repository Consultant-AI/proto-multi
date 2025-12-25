import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FiHome, FiSearch, FiPlusSquare, FiHeart, FiUser, FiLogOut } from 'react-icons/fi';
import './Layout.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/explore?q=${searchQuery}`);
      setSearchQuery('');
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <h1>InstaClone</h1>
        </Link>

        <form className="navbar-search" onSubmit={handleSearch}>
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        <div className="navbar-menu">
          <Link to="/" className="navbar-icon">
            <FiHome size={24} />
          </Link>
          <Link to="/upload" className="navbar-icon">
            <FiPlusSquare size={24} />
          </Link>
          <Link to="/notifications" className="navbar-icon">
            <FiHeart size={24} />
          </Link>
          <div className="navbar-profile">
            <button
              className="navbar-icon"
              onClick={() => setShowDropdown(!showDropdown)}
            >
              <FiUser size={24} />
            </button>
            {showDropdown && (
              <div className="profile-dropdown">
                <Link
                  to={`/${user?.username}`}
                  onClick={() => setShowDropdown(false)}
                >
                  <FiUser /> Profile
                </Link>
                <button onClick={handleLogout}>
                  <FiLogOut /> Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
