import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from '../../config/api';
import './CreatePostModal.css';

function CreatePostModal({ onClose, onPostCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    status: 'draft'
  });
  const [categories, setCategories] = useState(null);
  const [loading, setLoading] = useState(false);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [error, setError] = useState('');

  console.log('CreatePostModal rendered with props:', { onClose, onPostCreated });
  console.log('Current state:', { formData, categories, loading, error });

  useEffect(() => {
    console.log('CreatePostModal useEffect triggered');
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    console.log('Fetching categories...');
    setCategoriesLoading(true);
    try {
      const token = localStorage.getItem('token');
      console.log('Token found:', !!token);

      if (!token) {
        console.error('No authentication token found');
        setError('No authentication token found');
        setCategoriesLoading(false);
        return;
      }

      const response = await axios.get(getApiUrl('/api/categories/'), {
        headers: { Authorization: `Token ${token}` }
      });
      console.log('Categories response:', response.data);
      setCategories(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Failed to load categories: ' + err.message);
    } finally {
      setCategoriesLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log('Input change:', name, value);
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted with data:', formData);
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      await axios.post(getApiUrl('/api/posts/'), formData, {
        headers: { Authorization: `Token ${token}` }
      });
      onPostCreated();
    } catch (err) {
      console.error('Error creating post:', err);
      setError(err.response?.data || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  console.log('About to render modal with categories:', categories);

  return (
    <div className="create-post-modal-overlay" onClick={onClose}>
      <div className="create-post-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Post</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="create-post-form">
          <p>DEBUG: Modal is rendering!</p>

          {error && <div className="error-message">{error}</div>}

          {loading && <div className="loading-message">Loading...</div>}

          <p>Categories loaded: {categoriesLoading ? 'loading...' : (categories && Array.isArray(categories) ? categories.length : 'error')}</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                placeholder="Enter post title"
              />
            </div>

            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
              >
                              <option value="">Select a category</option>
              {categories && Array.isArray(categories) && categories.length > 0 ? (
                categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>Loading categories...</option>
              )}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="content">Content *</label>
              <textarea
                id="content"
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                required
                placeholder="Write your post content..."
                rows="4"
              />
            </div>

            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Creating...' : 'Create Post'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CreatePostModal;
