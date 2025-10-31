import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from '../config/api';
import './CreatorList.css';

function CreatorList({ onCreatorSelect, onViewFeed, user, selectedCategory }) {
  const [creators, setCreators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCreators();
  }, [selectedCategory]);

  const fetchCreators = async () => {
    try {
      setLoading(true);
      setError(null);
      // Build URL with category filter if selected
      let url = getApiUrl('/api/profiles/creators/');
      if (selectedCategory) {
        url += `?category=${selectedCategory.id}`;
      }
      console.log('Fetching creators from URL:', url);
      const response = await axios.get(url);

      // Handle both paginated (DRF) and non-paginated responses
      const creatorsData = response.data.results || response.data || [];
      setCreators(Array.isArray(creatorsData) ? creatorsData : []);
      setLoading(false);
    } catch (err) {
      const errorMessage = err.response?.status === 404
        ? 'Creators endpoint not found. Please check the API configuration.'
        : err.response?.data?.detail || err.message || 'Failed to fetch creators';

      setError(errorMessage);
      setLoading(false);
      console.error('Error fetching creators:', {
        error: err,
        status: err.response?.status,
        data: err.response?.data,
        url: getApiUrl('api/profiles/creators/')
      });
    }
  };

  if (loading) {
    return (
      <div className="creator-list-container">
        <div className="loading">
          <h2>Loading creators...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="creator-list-container">
        <div className="error">
          <h2>Error: {error}</h2>
          <button onClick={fetchCreators}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="creator-list-container">
      <div className="page-header">
        <h2>
          {selectedCategory ? `Creators in ${selectedCategory.name}` : 'Discover Creators'}
        </h2>
        {user && (
          <button className="btn btn-primary" onClick={onViewFeed}>
            View My Feed
          </button>
        )}
      </div>

      <div className="creators-grid">
        {creators.map((creator) => (
          <div key={creator.id} className="creator-card" onClick={() => onCreatorSelect(creator)}>
            <div className="creator-avatar">
              {creator.avatar ? (
                <img src={creator.avatar} alt={creator.username} />
              ) : (
                <div className="avatar-placeholder">
                  {creator.username.charAt(0).toUpperCase()}
                </div>
              )}
            </div>

            <div className="creator-info">
              <h3 className="creator-name">{creator.username}</h3>
              <p className="creator-bio">{creator.bio || 'No bio available'}</p>

              <div className="creator-stats">
                <span className="stat">
                  <strong>{creator.subscriber_count}</strong> subscribers
                </span>
                <span className="stat">
                  <strong>{creator.following_count}</strong> following
                </span>
              </div>

              <div className="creator-meta">
                <span className="creator-type">
                  {creator.is_creator ? 'Creator' : 'User'}
                </span>
                <span className="join-date">
                  Joined {new Date(creator.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="creator-actions">
              <button className="btn btn-outline">View Profile</button>
            </div>
          </div>
        ))}
      </div>

      {creators.length === 0 && (
        <div className="no-creators">
          <p>No creators available.</p>
        </div>
      )}
    </div>
  );
}

export default CreatorList;
