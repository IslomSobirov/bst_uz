import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sparkles, MessageCircle, ArrowRight, Calendar, Tag } from 'lucide-react';
import { getApiUrl } from '../../config/api';

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
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <div className="text-destructive text-lg font-medium">{error}</div>
        <button
          onClick={fetchFreePosts}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-12 pb-12">
      <div className="text-center space-y-4 py-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Free Content</span>
        </div>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
          Discover Free Posts
        </h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Explore content shared by our community of creators. No subscription required.
        </p>
      </div>

      {posts.length === 0 ? (
        <div className="text-center py-20 bg-muted/30 rounded-3xl border border-dashed border-border">
          <p className="text-xl text-muted-foreground">No free posts available right now.</p>
          <p className="text-sm text-muted-foreground mt-2">Check back later!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {posts.map((post) => (
            <article
              key={post.id}
              className="group flex flex-col bg-card border border-border/50 rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer"
              onClick={() => onPostSelect && onPostSelect(post)}
            >
              <div className="p-6 flex-grow space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {post.author?.avatar ? (
                      <img
                        src={post.author.avatar}
                        alt={post.author.username}
                        className="w-10 h-10 rounded-full object-cover border border-border"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                        {post.author?.username?.charAt(0).toUpperCase() || '?'}
                      </div>
                    )}
                    <div>
                      <h4 className="font-semibold text-sm text-foreground">
                        {post.author?.username || 'Unknown'}
                      </h4>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        {new Date(post.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full bg-green-500/10 text-green-600 text-xs font-bold uppercase tracking-wide">
                    Free
                  </span>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                    {post.title}
                  </h3>

                  {post.category?.name && (
                    <div className="flex items-center gap-1.5 text-xs text-primary font-medium">
                      <Tag className="w-3 h-3" />
                      {post.category.name}
                    </div>
                  )}

                  <p className="text-muted-foreground line-clamp-3 text-sm leading-relaxed">
                    {post.content}
                  </p>
                </div>
              </div>

              <div className="px-6 py-4 bg-muted/30 border-t border-border/50 flex items-center justify-between mt-auto">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MessageCircle className="w-4 h-4" />
                  {post.comments_count || 0} comments
                </div>
                <span className="text-sm font-medium text-primary flex items-center gap-1 group-hover:gap-2 transition-all">
                  Read More <ArrowRight className="w-4 h-4" />
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default FreePosts;
