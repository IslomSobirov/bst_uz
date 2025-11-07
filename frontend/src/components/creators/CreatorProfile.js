import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getApiUrl } from '../../config/api';
import TierManagement from '../tiers/TierManagement';
import './CreatorProfile.css';

function CreatorProfile({ creator, onBack, user, onSubscribe, onCreatePost }) {
  const [posts, setPosts] = useState([]);
  const [tiers, setTiers] = useState([]);
  const [userSubscriptions, setUserSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subscriptionLoading, setSubscriptionLoading] = useState(false);
  const [showTierManagement, setShowTierManagement] = useState(false);

  const fetchCreatorData = useCallback(async () => {
    if (!creator) return;

    try {
      const token = localStorage.getItem('token');
      const config = token ? { headers: { Authorization: `Token ${token}` } } : {};

      // Fetch creator's posts
      const postsResponse = await axios.get(
        getApiUrl(`/api/profiles/${creator.id}/posts/`),
        config
      );
      setPosts(postsResponse.data);

      // Fetch creator's tiers
      const tiersResponse = await axios.get(
        getApiUrl(`/api/profiles/${creator.id}/tiers/`)
      );
      setTiers(tiersResponse.data);

      // Fetch user's subscriptions to this creator (if logged in)
      if (user && token) {
        const subsResponse = await axios.get(
          getApiUrl(`/api/tier-subscriptions/by_creator/?creator_id=${creator.id}`),
          config
        );
        setUserSubscriptions(subsResponse.data);
      }

      setLoading(false);
    } catch (err) {
      setError('Failed to fetch creator data');
      setLoading(false);
      console.error('Error fetching creator data:', err);
    }
  }, [creator, user]);

  useEffect(() => {
    if (creator) {
      fetchCreatorData();
    }
  }, [creator, fetchCreatorData]);

  const handleSubscribeToTier = async (tierId) => {
    if (!user) {
      alert('Please log in to subscribe');
      return;
    }

    setSubscriptionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        getApiUrl('/api/tier-subscriptions/'),
        { tier_id: tierId },
        { headers: { Authorization: `Token ${token}` } }
      );
      alert('Successfully subscribed!');
      fetchCreatorData(); // Refresh data
    } catch (err) {
      console.error('Error subscribing:', err);
      alert(err.response?.data?.tier_id?.[0] || 'Failed to subscribe');
    } finally {
      setSubscriptionLoading(false);
    }
  };

  const handleCancelSubscription = async (subscriptionId) => {
    if (!window.confirm('Are you sure you want to cancel this subscription?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        getApiUrl(`/api/tier-subscriptions/${subscriptionId}/cancel/`),
        {},
        { headers: { Authorization: `Token ${token}` } }
      );
      alert('Subscription cancelled successfully');
      fetchCreatorData(); // Refresh data
    } catch (err) {
      console.error('Error cancelling subscription:', err);
      alert('Failed to cancel subscription');
    }
  };

  const isSubscribedToTier = (tierId) => {
    return userSubscriptions.some(sub => sub.tier.id === tierId && sub.is_active);
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
              {user && user.id === creator.id && user.is_creator && (
                <>
                  {onCreatePost && (
                    <button
                      className="btn btn-primary"
                      onClick={onCreatePost}
                      style={{ marginRight: '10px' }}
                    >
                      Create Post
                    </button>
                  )}
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowTierManagement(true)}
                  >
                    Manage Tiers
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Tiers Section */}
      {tiers.length > 0 && (
        <div className="tiers-section">
          <h2>Subscription Tiers</h2>
          {userSubscriptions.length > 0 && (
            <div className="user-subscriptions">
              <h3>Your Active Subscriptions:</h3>
              <div className="subscriptions-list">
                {userSubscriptions.map((sub) => (
                  <div key={sub.id} className="subscription-item">
                    <span>{sub.tier.name} - ${sub.tier.price}/month</span>
                    <span>Expires: {new Date(sub.end_date).toLocaleDateString()}</span>
                    {!sub.cancelled_at && (
                      <button
                        onClick={() => handleCancelSubscription(sub.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Cancel
                      </button>
                    )}
                    {sub.cancelled_at && (
                      <span className="cancelled-badge">Cancelled</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="tiers-grid">
            {tiers.map((tier) => (
              <div key={tier.id} className={`tier-card ${isSubscribedToTier(tier.id) ? 'subscribed' : ''}`}>
                {tier.image && (
                  <img src={tier.image} alt={tier.name} className="tier-image" />
                )}
                <h3>{tier.name}</h3>
                <div className="tier-price">${tier.price}<span>/month</span></div>
                <p className="tier-description">{tier.description}</p>
                <div className="tier-stats">
                  <span>📝 {tier.post_count} posts</span>
                  <span>👥 {tier.subscriber_count} subscribers</span>
                </div>
                {user && user.id !== creator.id && (
                  <button
                    className={`btn ${isSubscribedToTier(tier.id) ? 'btn-secondary' : 'btn-primary'}`}
                    onClick={() => handleSubscribeToTier(tier.id)}
                    disabled={subscriptionLoading || isSubscribedToTier(tier.id)}
                  >
                    {isSubscribedToTier(tier.id) ? '✓ Subscribed' : 'Subscribe'}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Posts Section */}
      <div className="profile-content">
        <h2>Posts by {creator.username}</h2>

        {loading ? (
          <div className="loading">
            <h3>Loading posts...</h3>
          </div>
        ) : error ? (
          <div className="error">
            <h3>Error: {error}</h3>
            <button onClick={fetchCreatorData}>Try Again</button>
          </div>
        ) : posts.length === 0 ? (
          <div className="no-posts">
            <p>No posts available from this creator.</p>
          </div>
        ) : (
          <div className="posts-grid">
            {posts.map((post) => (
              <article key={post.id} className={`post-card ${post.is_locked ? 'locked' : ''}`}>
                <div className="post-header">
                  <div className="post-title-row">
                    <h3>{post.title}</h3>
                    {post.is_locked && <span className="lock-icon">🔒</span>}
                  </div>
                  <div className="post-meta">
                    {post.category?.name && (
                      <span className="category-tag">{post.category.name}</span>
                    )}
                    <span className="date">
                      {new Date(post.created_at).toLocaleDateString()}
                    </span>
                    {!post.is_free && post.tiers && post.tiers.length > 0 && (
                      <span className="tier-badge">
                        💎 {post.tiers.map(t => t.name).join(', ')}
                      </span>
                    )}
                    {post.is_free && <span className="free-badge">Free</span>}
                  </div>
                </div>

                <div className={`post-content ${post.is_locked ? 'blurred' : ''}`}>
                  <p>{post.content}</p>
                </div>

                {post.is_locked && (
                  <div className="locked-overlay">
                    <div className="locked-message">
                      <span className="lock-icon-large">🔒</span>
                      <p>Subscribe to unlock this content</p>
                      {post.tiers && post.tiers.length > 0 && (
                        <p className="required-tiers">
                          Available in: {post.tiers.map(t => `${t.name} ($${t.price})`).join(' or ')}
                        </p>
                      )}
                    </div>
                  </div>
                )}

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

      {/* Tier Management Modal */}
      {showTierManagement && (
        <TierManagement
          user={user}
          onClose={() => {
            setShowTierManagement(false);
            fetchCreatorData(); // Refresh tiers after closing
          }}
        />
      )}
    </div>
  );
}

export default CreatorProfile;
