import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { ArrowLeft, Users, UserPlus, FileText, Lock, Star, Calendar, Tag, MessageCircle } from 'lucide-react';
import { getApiUrl } from '../../config/api';
import TierManagement from '../tiers/TierManagement';

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
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <h2 className="text-2xl font-bold text-destructive">Creator not found</h2>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Back to Creators
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto pb-12 space-y-8">
      {/* Header */}
      <div className="relative">
        <button
          onClick={onBack}
          className="absolute left-0 top-0 flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors z-10"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Creators
        </button>

        <div className="pt-12 flex flex-col md:flex-row items-start gap-8">
          <div className="flex-shrink-0">
            {creator.avatar ? (
              <img
                src={creator.avatar}
                alt={creator.username}
                className="w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-background shadow-xl"
              />
            ) : (
              <div className="w-32 h-32 md:w-40 md:h-40 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center text-primary font-bold text-5xl border-4 border-background shadow-xl">
                {creator.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <div className="flex-grow space-y-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-foreground">{creator.username}</h1>
              <p className="text-lg text-muted-foreground mt-2 max-w-2xl">{creator.bio || 'No bio available'}</p>
            </div>

            <div className="flex flex-wrap gap-6 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Users className="w-4 h-4" />
                <span className="font-semibold text-foreground">{creator.subscriber_count}</span> subscribers
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <UserPlus className="w-4 h-4" />
                <span className="font-semibold text-foreground">{creator.following_count}</span> following
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="w-4 h-4" />
                <span className="font-semibold text-foreground">{posts.length}</span> posts
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              {user && user.id === creator.id && user.is_creator && (
                <>
                  {onCreatePost && (
                    <button
                      className="px-4 py-2 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
                      onClick={onCreatePost}
                    >
                      Create Post
                    </button>
                  )}
                  <button
                    className="px-4 py-2 bg-secondary text-secondary-foreground rounded-full font-medium hover:bg-secondary/80 transition-all"
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
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            Subscription Tiers
          </h2>

          {userSubscriptions.length > 0 && (
            <div className="bg-primary/5 border border-primary/10 rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-primary">Your Active Subscriptions:</h3>
              <div className="space-y-3">
                {userSubscriptions.map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between bg-background p-4 rounded-lg border border-border/50">
                    <div>
                      <span className="font-medium text-foreground">{sub.tier.name}</span>
                      <span className="text-muted-foreground mx-2">•</span>
                      <span className="text-muted-foreground">${sub.tier.price}/month</span>
                      <div className="text-xs text-muted-foreground mt-1">
                        Expires: {new Date(sub.end_date).toLocaleDateString()}
                      </div>
                    </div>
                    {!sub.cancelled_at ? (
                      <button
                        onClick={() => handleCancelSubscription(sub.id)}
                        className="px-3 py-1.5 text-xs font-medium text-destructive bg-destructive/10 rounded-md hover:bg-destructive/20 transition-colors"
                      >
                        Cancel
                      </button>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-muted text-muted-foreground rounded-md">
                        Cancelled
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tiers.map((tier) => (
              <div
                key={tier.id}
                className={`relative flex flex-col bg-card border rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${isSubscribedToTier(tier.id) ? 'border-primary ring-1 ring-primary' : 'border-border/50'
                  }`}
              >
                {tier.image && (
                  <div className="h-32 overflow-hidden">
                    <img src={tier.image} alt={tier.name} className="w-full h-full object-cover" />
                  </div>
                )}
                <div className="p-6 flex-grow space-y-4">
                  <div>
                    <h3 className="text-xl font-bold text-foreground">{tier.name}</h3>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-2xl font-bold text-primary">${tier.price}</span>
                      <span className="text-sm text-muted-foreground">/month</span>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {tier.description}
                  </p>

                  <div className="space-y-2 pt-4 border-t border-border/50">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="w-4 h-4 text-primary" />
                      <span>Access to {tier.post_count} posts</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users className="w-4 h-4 text-primary" />
                      <span>Join {tier.subscriber_count} subscribers</span>
                    </div>
                  </div>
                </div>

                <div className="p-6 pt-0 mt-auto">
                  {user && user.id !== creator.id && (
                    <button
                      className={`w-full py-2.5 rounded-xl font-medium transition-all ${isSubscribedToTier(tier.id)
                          ? 'bg-secondary text-secondary-foreground cursor-default'
                          : 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20'
                        }`}
                      onClick={() => handleSubscribeToTier(tier.id)}
                      disabled={subscriptionLoading || isSubscribedToTier(tier.id)}
                    >
                      {isSubscribedToTier(tier.id) ? '✓ Subscribed' : 'Subscribe'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Posts Section */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-foreground">Posts by {creator.username}</h2>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 space-y-4">
            <div className="text-destructive text-lg font-medium">{error}</div>
            <button
              onClick={fetchCreatorData}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Try Again
            </button>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-20 bg-muted/30 rounded-3xl border border-dashed border-border">
            <p className="text-xl text-muted-foreground">No posts available from this creator.</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {posts.map((post) => (
              <article
                key={post.id}
                className={`group relative bg-card border border-border/50 rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-lg ${post.is_locked ? 'bg-muted/10' : ''
                  }`}
              >
                <div className="p-6 space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors flex items-center gap-2">
                        {post.title}
                        {post.is_locked && <Lock className="w-4 h-4 text-muted-foreground" />}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(post.created_at).toLocaleDateString()}
                        </span>
                        {post.category?.name && (
                          <span className="flex items-center gap-1 text-primary">
                            <Tag className="w-3 h-3" />
                            {post.category.name}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {!post.is_free && post.tiers && post.tiers.length > 0 && (
                        <span className="px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-600 text-xs font-medium border border-purple-500/20 flex items-center gap-1">
                          <Star className="w-3 h-3" />
                          {post.tiers.map(t => t.name).join(', ')}
                        </span>
                      )}
                      {post.is_free && (
                        <span className="px-2.5 py-1 rounded-full bg-green-500/10 text-green-600 text-xs font-medium border border-green-500/20">
                          Free
                        </span>
                      )}
                    </div>
                  </div>

                  <div className={`prose prose-sm dark:prose-invert max-w-none text-muted-foreground ${post.is_locked ? 'blur-sm select-none' : ''}`}>
                    <p>{post.content}</p>
                  </div>

                  {post.is_locked && (
                    <div className="absolute inset-0 flex items-center justify-center bg-background/60 backdrop-blur-[2px]">
                      <div className="text-center p-6 bg-card border border-border rounded-2xl shadow-xl max-w-sm mx-4">
                        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                          <Lock className="w-6 h-6 text-primary" />
                        </div>
                        <h4 className="text-lg font-bold text-foreground mb-2">Unlock this post</h4>
                        <p className="text-sm text-muted-foreground mb-4">
                          Subscribe to one of the following tiers to view this content:
                        </p>
                        {post.tiers && post.tiers.length > 0 && (
                          <div className="flex flex-wrap justify-center gap-2">
                            {post.tiers.map(t => (
                              <span key={t.id} className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs font-medium">
                                {t.name} (${t.price})
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t border-border/50 flex items-center gap-2 text-sm text-muted-foreground">
                    <MessageCircle className="w-4 h-4" />
                    {post.comments_count || 0} comments
                  </div>
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
