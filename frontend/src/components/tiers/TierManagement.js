import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from '../../config/api';
import './TierManagement.css';

function TierManagement({ user, onClose }) {
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTier, setEditingTier] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    order: 0,
    is_active: true,
  });
  const [imageFile, setImageFile] = useState(null);

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        getApiUrl('/api/tiers/my_tiers/'),
        { headers: { Authorization: `Token ${token}` } }
      );
      setTiers(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching tiers:', err);
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleImageChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (tiers.length >= 10 && !editingTier) {
      alert('You can only create up to 10 tiers');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const data = new FormData();

      data.append('name', formData.name);
      data.append('description', formData.description);
      data.append('price', formData.price);
      data.append('order', formData.order);
      data.append('is_active', formData.is_active);

      if (imageFile) {
        data.append('image', imageFile);
      }

      if (editingTier) {
        // Update existing tier
        await axios.patch(
          getApiUrl(`/api/tiers/${editingTier.id}/`),
          data,
          { headers: { Authorization: `Token ${token}` } }
        );
        alert('Tier updated successfully!');
      } else {
        // Create new tier
        await axios.post(
          getApiUrl('/api/tiers/'),
          data,
          { headers: { Authorization: `Token ${token}` } }
        );
        alert('Tier created successfully!');
      }

      // Reset form and refresh tiers
      setFormData({ name: '', description: '', price: '', order: 0, is_active: true });
      setImageFile(null);
      setEditingTier(null);
      setShowForm(false);
      fetchTiers();
    } catch (err) {
      console.error('Error saving tier:', err);
      alert(err.response?.data?.name?.[0] || 'Failed to save tier');
    }
  };

  const handleEdit = (tier) => {
    setEditingTier(tier);
    setFormData({
      name: tier.name,
      description: tier.description,
      price: tier.price,
      order: tier.order,
      is_active: tier.is_active,
    });
    setImageFile(null);
    setShowForm(true);
  };

  const handleDelete = async (tierId) => {
    if (!window.confirm('Are you sure you want to delete this tier? This cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        getApiUrl(`/api/tiers/${tierId}/`),
        { headers: { Authorization: `Token ${token}` } }
      );
      alert('Tier deleted successfully');
      fetchTiers();
    } catch (err) {
      console.error('Error deleting tier:', err);
      alert('Failed to delete tier');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTier(null);
    setFormData({ name: '', description: '', price: '', order: 0, is_active: true });
    setImageFile(null);
  };

  if (loading) {
    return (
      <div className="tier-management-modal">
        <div className="tier-management-content">
          <div className="loading">Loading tiers...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="tier-management-modal">
      <div className="tier-management-content">
        <div className="modal-header">
          <h2>Manage Subscription Tiers</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {!showForm ? (
            <>
              <div className="tiers-header">
                <p>You have {tiers.length}/10 tiers</p>
                {tiers.length < 10 && (
                  <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                    + Create New Tier
                  </button>
                )}
              </div>

              {tiers.length === 0 ? (
                <div className="no-tiers">
                  <p>You haven't created any subscription tiers yet.</p>
                  <p>Create your first tier to start monetizing your content!</p>
                </div>
              ) : (
                <div className="tiers-list">
                  {tiers.map((tier) => (
                    <div key={tier.id} className="tier-item">
                      <div className="tier-item-content">
                        {tier.image && (
                          <img src={tier.image} alt={tier.name} className="tier-item-image" />
                        )}
                        <div className="tier-item-details">
                          <h3>
                            {tier.name}
                            {!tier.is_active && <span className="inactive-badge">Inactive</span>}
                          </h3>
                          <p className="tier-item-price">${tier.price}/month</p>
                          <p className="tier-item-description">{tier.description}</p>
                          <div className="tier-item-stats">
                            <span>👥 {tier.subscriber_count} subscribers</span>
                            <span>📝 {tier.post_count} posts</span>
                            <span>📊 Order: {tier.order}</span>
                          </div>
                        </div>
                      </div>
                      <div className="tier-item-actions">
                        <button className="btn btn-secondary btn-sm" onClick={() => handleEdit(tier)}>
                          Edit
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(tier.id)}>
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <form onSubmit={handleSubmit} className="tier-form">
              <h3>{editingTier ? 'Edit Tier' : 'Create New Tier'}</h3>

              <div className="form-group">
                <label htmlFor="name">Tier Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Basic, Premium, VIP"
                  required
                  maxLength={100}
                />
              </div>

              <div className="form-group">
                <label htmlFor="price">Monthly Price (USD) *</label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  placeholder="9.99"
                  step="0.01"
                  min="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe what subscribers will get with this tier..."
                  required
                  maxLength={1000}
                  rows={4}
                />
              </div>

              <div className="form-group">
                <label htmlFor="order">Display Order</label>
                <input
                  type="number"
                  id="order"
                  name="order"
                  value={formData.order}
                  onChange={handleInputChange}
                  placeholder="0"
                  min="0"
                />
                <small>Lower numbers appear first</small>
              </div>

              <div className="form-group">
                <label htmlFor="image">Tier Image</label>
                <input
                  type="file"
                  id="image"
                  accept="image/*"
                  onChange={handleImageChange}
                />
                {editingTier && editingTier.image && !imageFile && (
                  <div className="current-image">
                    <img src={editingTier.image} alt="Current" />
                    <span>Current image</span>
                  </div>
                )}
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                  />
                  <span>Active (available for subscription)</span>
                </label>
              </div>

              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingTier ? 'Update Tier' : 'Create Tier'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default TierManagement;
