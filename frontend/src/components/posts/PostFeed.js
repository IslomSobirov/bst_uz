import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, ArrowRight, MessageCircle, Calendar, Tag } from 'lucide-react';
import { getApiUrl } from '../../config/api';

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

      const response = await axios.get(getApiUrl('/api/posts/feed/'), {
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
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-6 text-center">
        <h2 className="text-2xl font-bold text-foreground">Please log in to view your feed</h2>
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Creators
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Creators
        </button>
        <div className="text-right">
          <h2 className="text-3xl font-bold text-foreground">My Feed</h2>
          <p className="text-muted-foreground">Latest updates from creators you follow</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : error ? (
        <div className="text-center py-12 space-y-4">
          <div className="text-destructive text-lg font-medium">{error}</div>
          <button
            onClick={fetchFeed}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Try Again
          </button>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-20 bg-muted/30 rounded-3xl border border-dashed border-border space-y-6">
          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-foreground">No posts in your feed</h3>
            <p className="text-muted-foreground">Start following creators to see their posts here!</p>
          </div>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20"
          >
            Discover Creators
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {posts.map((post) => (
            <article
              key={post.id}
              className="group bg-card border border-border/50 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:border-primary/20"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0">
                  {post.author.avatar ? (
                    <img
                      src={post.author.avatar}
                      alt={post.author.username}
                      className="w-12 h-12 rounded-full object-cover border-2 border-background shadow-sm"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
                      {post.author.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="flex-grow">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {post.author.username}
                      </h4>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                        <Calendar className="w-3 h-3" />
                        {new Date(post.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    {post.status === 'published' && (
                      <span className="px-2 py-1 rounded-full bg-green-500/10 text-green-600 text-xs font-medium border border-green-500/20">
                        Published
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-2xl font-bold text-foreground">{post.title}</h3>

                {post.category?.name && (
                  <div className="flex items-center gap-1.5 text-sm text-primary font-medium">
                    <Tag className="w-4 h-4" />
                    {post.category.name}
                  </div>
                )}

                <div className="prose prose-sm dark:prose-invert max-w-none text-muted-foreground">
                  <p>{post.content.substring(0, 300)}...</p>
                </div>

                <div className="pt-4 flex items-center justify-between border-t border-border/50">
                  <div className="flex items-center gap-2 text-muted-foreground text-sm">
                    <MessageCircle className="w-4 h-4" />
                    {post.comments_count || 0} comments
                  </div>
                  <button className="text-sm font-medium text-primary hover:text-primary/80 transition-colors flex items-center gap-1">
                    Read More <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default PostFeed;
