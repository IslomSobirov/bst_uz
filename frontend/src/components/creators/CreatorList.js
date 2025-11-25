import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Users, UserPlus, ArrowRight, Sparkles } from 'lucide-react';
import { getApiUrl } from '../../config/api';

function CreatorList({ onCreatorSelect, onViewFeed, user, selectedCategory }) {
  const [creators, setCreators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCreators = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      let url = getApiUrl('/api/profiles/creators/');
      if (selectedCategory) {
        url += `?category=${selectedCategory.id}`;
      }
      const response = await axios.get(url);
      const creatorsData = response.data.results || response.data || [];
      setCreators(Array.isArray(creatorsData) ? creatorsData : []);
      setLoading(false);
    } catch (err) {
      setError('Failed to load creators');
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchCreators();
  }, [fetchCreators]);

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
          onClick={fetchCreators}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-12 pb-12">
      {/* Hero Section */}
      {!selectedCategory && (
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 text-white shadow-2xl">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
          <div className="relative px-8 py-16 md:py-24 text-center space-y-6 max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-sm font-medium mb-4">
              <Sparkles className="w-4 h-4 text-yellow-300" />
              <span>Discover Exclusive Content</span>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Support Your Favorite <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-pink-200">
                Creators Directly
              </span>
            </h1>
            <p className="text-lg md:text-xl text-white/80 max-w-2xl mx-auto leading-relaxed">
              Join a community where creativity thrives. Subscribe to unlock exclusive posts,
              behind-the-scenes content, and direct access to the artists you love.
            </p>
            {user && (
              <div className="pt-4">
                <button
                  onClick={onViewFeed}
                  className="px-8 py-4 bg-white text-indigo-600 rounded-full font-bold text-lg hover:bg-indigo-50 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center gap-2 mx-auto"
                >
                  Go to My Feed
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight text-foreground">
          {selectedCategory ? `Creators in ${selectedCategory.name}` : 'Featured Creators'}
        </h2>
      </div>

      {/* Creators Grid */}
      {creators.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {creators.map((creator) => (
            <div
              key={creator.id}
              onClick={() => onCreatorSelect(creator)}
              className="group relative bg-card hover:bg-accent/5 border border-border/50 rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 cursor-pointer"
            >
              <div className="aspect-[4/3] bg-muted relative overflow-hidden">
                {creator.avatar ? (
                  <img
                    src={creator.avatar}
                    alt={creator.username}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/20 to-purple-500/20 text-4xl font-bold text-primary/50">
                    {creator.username.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                  <span className="text-white font-medium flex items-center gap-2">
                    View Profile <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </div>

              <div className="p-5 space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                    {creator.username}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                    {creator.bio || 'No bio available'}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-border/50">
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <Users className="w-4 h-4" />
                    <span className="font-medium text-foreground">{creator.subscriber_count}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <UserPlus className="w-4 h-4" />
                    <span className="font-medium text-foreground">{creator.following_count}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-muted/30 rounded-3xl border border-dashed border-border">
          <p className="text-xl text-muted-foreground">No creators found in this category.</p>
        </div>
      )}
    </div>
  );
}

export default CreatorList;
