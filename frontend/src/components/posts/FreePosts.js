import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from '../config/api';
import './FreePosts.css';

function FreePosts({ onPostSelect, user }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFreePosts();
  }, []);

  const fetchFreePosts = async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetch free posts - accessible to everyone
      const response = await axios.get(getApiUrl('/api/posts/'));
      const postsData = response.data.results || response.data || [];
      // Filter for free posts
      const freePosts = postsData.filter(post => post.is_free);
      setPosts(freePosts);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch posts');
      setLoading(false);
      console.error('Error fetching free posts:', err);
    }
  };

  if (loading) {
    return (
      <div className="free-posts-container">
        <div className="loading">
          <h2>Loading posts...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="free-posts-container">
        <div className="error">
          <h2>Error: {error}</h2>
          <button onClick={fetchFreePosts}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="free-posts-container">
      <div className="page-header">
        <h2>Free Posts</h2>
        <p>Discover free content from all creators</p>
      </div>

      <div className="posts-grid">
        {posts.map((post) => (
          <article
            key={post.id}
            className="post-card clickable"
            onClick={() => onPostSelect && onPostSelect(post)}
          >
            <div className="post-header">
              <div className="post-author">
                <div className="author-avatar">
                  {post.author?.avatar ? (
                    <img src={post.author.avatar} alt={post.author.username} />
                  ) : (
                    <div className="avatar-placeholder small">
                      {post.author?.username?.charAt(0).toUpperCase() || '?'}
                    </div>
                  )}
                </div>
                <div className="author-info">
                  <h4 className="author-name">{post.author?.username || 'Unknown'}</h4>
                  <span className="post-date">
                    {new Date(post.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <h3 className="post-title">{post.title}</h3>

              <div className="post-meta">
                {post.category?.name && (
                  <span className="category-tag">{post.category.name}</span>
                )}
                <span className="free-badge">FREE</span>
              </div>
            </div>

            <div className="post-content">
              <p>{post.content.substring(0, 300)}{post.content.length > 300 ? '...' : ''}</p>
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

      {posts.length === 0 && (
        <div className="no-posts">
          <h3>No free posts available</h3>
          <p>Check back later for free content from creators!</p>
        </div>
      )}
    </div>
  );
}

export default FreePosts;
