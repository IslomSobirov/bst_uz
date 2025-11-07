import React from 'react';
import './Header.css';

function Header({ user, onLogin, onLogout, currentView, onViewChange }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo" onClick={() => onViewChange('creators')}>
            Boosty Uzbekistan
          </h1>
          <nav className="nav-menu">
            <button
              className={`nav-item ${currentView === 'creators' ? 'active' : ''}`}
              onClick={() => onViewChange('creators')}
            >
              Creators
            </button>
            <button
              className={`nav-item ${currentView === 'posts' ? 'active' : ''}`}
              onClick={() => onViewChange('posts')}
            >
              Posts
            </button>
            <button
              className={`nav-item ${currentView === 'pricing' ? 'active' : ''}`}
              onClick={() => onViewChange('pricing')}
            >
              Pricing
            </button>
            {user && (
              <button
                className={`nav-item ${currentView === 'feed' ? 'active' : ''}`}
                onClick={() => onViewChange('feed')}
              >
                My Feed
              </button>
            )}
          </nav>
        </div>

        <div className="header-right">
          {user ? (
            <div className="user-controls">
              <div className="user-info">
                {user.is_creator ? (
                  <span
                    className="username clickable"
                    onClick={() => onViewChange('myProfile')}
                  >
                    {user.username}
                  </span>
                ) : (
                  <span className="username">{user.username}</span>
                )}
                {user.is_creator && <span className="creator-badge">Creator</span>}
                <button className="btn btn-secondary" onClick={onLogout}>
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <button className="btn btn-primary" onClick={onLogin}>
              Login / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
