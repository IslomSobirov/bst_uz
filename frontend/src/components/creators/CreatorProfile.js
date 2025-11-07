import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getApiUrl } from '../../config/api';
import './CreatorProfile.css';

function CreatorProfile({ creator, onBack, user, onSubscribe, onCreatePost }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscriptionLoading, setSubscriptionLoading] = useState(false);

  const fetchCreatorPosts = useCallback(async () => {
    if (!creator) return;

    try {
      // Get posts by this specific creator
      const response = await axios.get(getApiUrl('/api/posts/'));
      const creatorPosts = response.data.results?.filter(post =>
        post.author.id === creator.id
      ) || [];
      setPosts(creatorPosts);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch posts');
      setLoading(false);
      console.error('Error fetching posts:', err);
    }
  }, [creator]);

  const checkSubscriptionStatus = useCallback(async () => {
    if (!user || !creator) return;

    try {
      // Check if user is subscribed to this creator
      // This would need a proper subscription check endpoint
      // For now, we'll assume not subscribed
      setIsSubscribed(false);
    } catch (err) {
      console.error('Error checking subscription status:', err);
    }
  }, [user, creator]);

  useEffect(() => {
    if (creator) {
      fetchCreatorPosts();
      checkSubscriptionStatus();
    }
  }, [creator, fetchCreatorPosts, checkSubscriptionStatus]);

  const handleSubscribe = async () => {
    if (!user) return;

    setSubscriptionLoading(true);
    try {
      if (isSubscribed) {
        // Unsubscribe
        await axios.delete(getApiUrl(`/api/profiles/${creator.id}/unsubscribe/`));
        setIsSubscribed(false);
      } else {
        // Subscribe
        await axios.post(getApiUrl(`/api/profiles/${creator.id}/subscribe/`));
        setIsSubscribed(true);
      }
      onSubscribe(); // Refresh creator data
    } catch (err) {
      console.error('Error updating subscription:', err);
    } finally {
      setSubscriptionLoading(false);
    }
  };

  if (!creator) {
    return (
      <div className="creator-profile-container">
        <div className="error">
          <h2>Creator not found</h2>
          <button onClick={onBack}>Back to Creators</button>
        </div>
      </div>
    );
  }

  return (
    <div className="creator-profile-container">
      <div className="profile-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Creators
        </button>

        <div className="profile-info">
          <div className="profile-avatar">
            {creator.avatar ? (
              <img src={creator.avatar} alt={creator.username} />
            ) : (
              <div className="avatar-placeholder large">
                {creator.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <div className="profile-details">
            <h1 className="profile-name">{creator.username}</h1>
            <p className="profile-bio">{creator.bio || 'No bio available'}</p>

            <div className="profile-stats">
              <div className="stat">
                <strong>{creator.subscriber_count}</strong>
                <span>subscribers</span>
              </div>
              <div className="stat">
                <strong>{creator.following_count}</strong>
                <span>following</span>
              </div>
              <div className="stat">
                <strong>{posts.length}</strong>
                <span>posts</span>
              </div>
            </div>

            <div className="profile-actions">
              {user && user.id === creator.id && user.is_creator && onCreatePost && (
                <button
                  className="btn btn-primary"
                  onClick={onCreatePost}
                  style={{ marginRight: '10px' }}
                >
                  Create Post
                </button>
              )}
              {user && user.id !== creator.id && (
                <button
                  className={`btn ${isSubscribed ? 'btn-secondary' : 'btn-primary'}`}
                  onClick={handleSubscribe}
                  disabled={subscriptionLoading}
                >
                  {subscriptionLoading ? '...' : isSubscribed ? 'Unsubscribe' : 'Subscribe'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="profile-content">
        <h2>Posts by {creator.username}</h2>

        {loading ? (
          <div className="loading">
            <h3>Loading posts...</h3>
          </div>
        ) : error ? (
          <div className="error">
            <h3>Error: {error}</h3>
            <button onClick={fetchCreatorPosts}>Try Again</button>
          </div>
        ) : posts.length === 0 ? (
          <div className="no-posts">
            <p>No posts available from this creator.</p>
          </div>
        ) : (
          <div className="posts-grid">
            {posts.map((post) => (
              <article key={post.id} className="post-card">
                <div className="post-header">
                  <h3>{post.title}</h3>
                  <div className="post-meta">
                    <span className="category">
                      {post.category?.name && (
                        <span className="category-tag">{post.category.name}</span>
                      )}
                    </span>
                    <span className="date">
                      {new Date(post.created_at).toLocaleDateString()}
                    </span>
                    <span className="status">
                      {post.status === 'draft' && <span className="draft-badge">Draft</span>}
                      {post.status === 'published' && <span className="published-badge">Published</span>}
                    </span>
                  </div>
                </div>

                <div className="post-content">
                  <p>{post.content.substring(0, 200)}...</p>
                </div>

                <div className="post-footer">
                  <span className="comments-count">
                    💬 {post.comments_count || 0} comments
                  </span>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CreatorProfile;
