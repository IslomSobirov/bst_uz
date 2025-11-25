import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from './config/api';

// Components
import Header from './components/layout/Header';
import CategoryList from './components/navigation/CategoryList';
import CreatorList from './components/creators/CreatorList';
import CreatorProfile from './components/creators/CreatorProfile';
import PostFeed from './components/posts/PostFeed';
import FreePosts from './components/posts/FreePosts';
import PostDetail from './components/posts/PostDetail';
import AuthModal from './components/modals/AuthModal';
import CreatePostModal from './components/modals/CreatePostModal';
import PricingPage from './components/pricing/PricingPage';

function App() {
  const [currentView, setCurrentView] = useState('creators'); // creators, profile, feed, posts, postDetail, pricing
  const [selectedCreator, setSelectedCreator] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCreatePost, setShowCreatePost] = useState(false);

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await axios.get(getApiUrl('/api/profiles/me/'), {
        headers: { Authorization: `Token ${token}` }
      });
      setUser(response.data);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    } catch (err) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const response = await axios.post(getApiUrl('/api/auth/login/'), credentials);
      const { token, user: userData } = response.data;

      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      setUser(userData);
      setShowAuthModal(false);

      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: err.response?.data?.error || 'Login failed'
      };
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await axios.post(getApiUrl('/api/auth/register/'), userData);
      const { token, user: newUser } = response.data;

      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      setUser(newUser);
      setShowAuthModal(false);

      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: err.response?.data || 'Registration failed'
      };
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setCurrentView('creators');
  };

  const handleCreatorSelect = (creator) => {
    setSelectedCreator(creator);
    setCurrentView('profile');
  };

  const handleViewMyProfile = () => {
    if (user && user.is_creator) {
      // Set the user's profile as selected creator
      setSelectedCreator(user);
      setCurrentView('profile');
    }
  };

  const handleBackToCreators = () => {
    setCurrentView('creators');
    setSelectedCreator(null);
    setSelectedCategory(null);
  };

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setCurrentView('creators');
    setSelectedCreator(null);
  };

  const handleViewFeed = () => {
    setCurrentView('feed');
  };

  const handlePostSelect = (post) => {
    setSelectedPost(post);
    setCurrentView('postDetail');
  };

  const handleBackToPosts = () => {
    setCurrentView('posts');
    setSelectedPost(null);
  };

  const handleCreatePost = () => {
    setShowCreatePost(true);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'creators':
        return (
          <CreatorList
            onCreatorSelect={handleCreatorSelect}
            onViewFeed={handleViewFeed}
            user={user}
            selectedCategory={selectedCategory}
          />
        );
      case 'profile':
        return (
          <CreatorProfile
            creator={selectedCreator}
            onBack={handleBackToCreators}
            user={user}
            onCreatePost={handleCreatePost}
            onSubscribe={() => {
              // Refresh creator data
              if (selectedCreator) {
                // This would refresh the creator data
              }
            }}
          />
        );
      case 'feed':
        return (
          <PostFeed
            onBack={handleBackToCreators}
            user={user}
          />
        );
      case 'posts':
        return (
          <FreePosts
            onPostSelect={handlePostSelect}
            user={user}
          />
        );
      case 'postDetail':
        return (
          <PostDetail
            post={selectedPost}
            onBack={handleBackToPosts}
            user={user}
          />
        );
      case 'pricing':
        return (
          <PricingPage
            onBack={handleBackToCreators}
          />
        );
      default:
        return <CreatorList onCreatorSelect={handleCreatorSelect} />;
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
      <Header
        user={user}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
        currentView={currentView}
        onViewChange={(view) => {
          if (view === 'myProfile') {
            handleViewMyProfile();
          } else {
            setCurrentView(view);
          }
        }}
      />

      <CategoryList
        onCategorySelect={handleCategorySelect}
        selectedCategory={selectedCategory}
      />

      <main className="flex-grow container mx-auto px-4 py-8">
        {renderCurrentView()}
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLogin}
          onRegister={handleRegister}
        />
      )}

      {/* Create Post Modal */}
      {showCreatePost && user?.is_creator && (
        <CreatePostModal
          onClose={() => setShowCreatePost(false)}
          onPostCreated={() => {
            setShowCreatePost(false);
            // Refresh current view
          }}
        />
      )}
    </div>
  );
}

export default App;
