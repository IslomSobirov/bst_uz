import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Components
import Header from './components/Header';
import CategoryList from './components/CategoryList';
import CreatorList from './components/CreatorList';
import CreatorProfile from './components/CreatorProfile';
import PostFeed from './components/PostFeed';
import FreePosts from './components/FreePosts';
import PostDetail from './components/PostDetail';
import AuthModal from './components/AuthModal';
import CreatePostModal from './components/CreatePostModal';

function App() {
  const [currentView, setCurrentView] = useState('creators'); // creators, profile, feed, posts, postDetail
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
      const response = await axios.get('http://localhost:8000/api/profiles/me/', {
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
      const response = await axios.post('http://localhost:8000/api/auth/login/', credentials);
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
      const response = await axios.post('http://localhost:8000/api/auth/register/', userData);
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

  const handleViewPosts = () => {
    setCurrentView('posts');
    setSelectedPost(null);
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
      default:
        return <CreatorList onCreatorSelect={handleCreatorSelect} />;
    }
  };

  return (
    <div className="App">
      <Header
        user={user}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
        onCreatePost={handleCreatePost}
        currentView={currentView}
        onViewChange={setCurrentView}
      />

      <CategoryList
        onCategorySelect={handleCategorySelect}
        selectedCategory={selectedCategory}
      />

      <main className="main-content">
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
