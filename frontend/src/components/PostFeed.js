import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PostFeed.css';

function PostFeed({ onBack, user }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchFeed();
    }
  }, [user]);

  const fetchFeed = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        setLoading(false);
        return;
      }
      
      const response = await axios.get('http://localhost:8000/api/posts/feed/', {
        headers: { Authorization: `Token ${token}` }
      });
      setPosts(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch feed');
      setLoading(false);
      console.error('Error fetching feed:', err);
    }
  };

  if (!user) {
    return (
      <div className="post-feed-container">
        <div className="error">
          <h2>Please log in to view your feed</h2>
          <button onClick={onBack}>Back to Creators</button>
        </div>
      </div>
    );
  }

  return (
    <div className="post-feed-container">
      <div className="feed-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Creators
        </button>
        <h2>My Feed</h2>
        <p>Posts from creators you follow</p>
      </div>
      
      {loading ? (
        <div className="loading">
          <h3>Loading your feed...</h3>
        </div>
      ) : error ? (
        <div className="error">
          <h3>Error: {error}</h3>
          <button onClick={fetchFeed}>Try Again</button>
        </div>
      ) : posts.length === 0 ? (
        <div className="no-posts">
          <h3>No posts in your feed</h3>
          <p>Start following creators to see their posts here!</p>
          <button className="btn btn-primary" onClick={onBack}>
            Discover Creators
          </button>
        </div>
      ) : (
        <div className="feed-content">
          <div className="posts-grid">
            {posts.map((post) => (
              <article key={post.id} className="post-card">
                <div className="post-header">
                  <div className="post-author">
                    <div className="author-avatar">
                      {post.author.avatar ? (
                        <img src={post.author.avatar} alt={post.author.username} />
                      ) : (
                        <div className="avatar-placeholder small">
                          {post.author.username.charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="author-info">
                      <h4 className="author-name">{post.author.username}</h4>
                      <span className="post-date">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="post-title">{post.title}</h3>
                  
                  <div className="post-meta">
                    <span className="category">
                      {post.category?.name && (
                        <span className="category-tag">{post.category.name}</span>
                      )}
                    </span>
                    <span className="status">
                      {post.status === 'published' && <span className="published-badge">Published</span>}
                    </span>
                  </div>
                </div>
                
                <div className="post-content">
                  <p>{post.content.substring(0, 300)}...</p>
                </div>
                
                <div className="post-footer">
                  <span className="comments-count">
                    💬 {post.comments_count || 0} comments
                  </span>
                  <button className="btn btn-outline">Read More</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PostFeed;
