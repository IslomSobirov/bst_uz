import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { X, Bold, Italic, Link as LinkIcon, List, Image as ImageIcon, ChevronDown, Check, Lock, Globe } from 'lucide-react';
import { getApiUrl } from '../../config/api';

function CreatePostModal({ onClose, onPostCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    status: 'draft',
    is_free: true,
    tiers: []
  });
  const [categories, setCategories] = useState([]);
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [error, setError] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    fetchCategories();
    fetchTiers();
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const fetchCategories = async () => {
    setCategoriesLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        setCategoriesLoading(false);
        return;
      }

      const response = await axios.get(getApiUrl('/api/categories/'), {
        headers: { Authorization: `Token ${token}` }
      });
      setCategories(response.data.results || response.data || []);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Failed to load categories');
    } finally {
      setCategoriesLoading(false);
    }
  };

  const fetchTiers = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.get(getApiUrl('/api/tiers/my_tiers/'), {
        headers: { Authorization: `Token ${token}` }
      });
      setTiers(response.data || []);
    } catch (err) {
      console.error('Error fetching tiers:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (type === 'checkbox' && name === 'is_free') {
      setFormData(prev => ({
        ...prev,
        is_free: checked,
        tiers: checked ? [] : prev.tiers
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleTierToggle = (tierId) => {
    setFormData(prev => {
      const tiers = prev.tiers.includes(tierId)
        ? prev.tiers.filter(id => id !== tierId)
        : [...prev.tiers, tierId];
      return { ...prev, tiers };
    });
  };

  // Rich Text Toolbar Actions
  const insertFormat = (startTag, endTag = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = formData.content;
    const before = text.substring(0, start);
    const selection = text.substring(start, end);
    const after = text.substring(end);

    const newContent = before + startTag + selection + endTag + after;

    setFormData(prev => ({ ...prev, content: newContent }));

    // Restore focus and selection
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + startTag.length, end + startTag.length);
    }, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      onClose();
    } catch (err) {
      console.error('Error creating post:', err);
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-full max-w-3xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-xl font-bold text-foreground">Create New Post</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm font-medium">
              {error}
            </div>
          )}

          <form id="create-post-form" onSubmit={handleSubmit} className="space-y-6">
            {/* Title Input */}
            <div className="space-y-2">
              <label htmlFor="title" className="text-sm font-medium text-foreground">
                Post Title
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                placeholder="Give your post a catchy title"
                className="w-full px-4 py-2.5 rounded-xl border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              />
            </div>

            {/* Category & Status Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="category" className="text-sm font-medium text-foreground">
                  Category
                </label>
                <div className="relative">
                  <select
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-input bg-background text-foreground appearance-none focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all cursor-pointer"
                  >
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="status" className="text-sm font-medium text-foreground">
                  Status
                </label>
                <div className="relative">
                  <select
                    id="status"
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-input bg-background text-foreground appearance-none focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all cursor-pointer"
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Rich Text Editor */}
            <div className="space-y-2">
              <label htmlFor="content" className="text-sm font-medium text-foreground">
                Content
              </label>
              <div className="border border-input rounded-xl overflow-hidden bg-background focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
                {/* Toolbar */}
                <div className="flex items-center gap-1 p-2 border-b border-border bg-muted/30">
                  <button type="button" onClick={() => insertFormat('**', '**')} className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground" title="Bold">
                    <Bold className="w-4 h-4" />
                  </button>
                  <button type="button" onClick={() => insertFormat('*', '*')} className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground" title="Italic">
                    <Italic className="w-4 h-4" />
                  </button>
                  <div className="w-px h-4 bg-border mx-1" />
                  <button type="button" onClick={() => insertFormat('[', '](url)')} className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground" title="Link">
                    <LinkIcon className="w-4 h-4" />
                  </button>
                  <button type="button" onClick={() => insertFormat('![alt text](', ')')} className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground" title="Image">
                    <ImageIcon className="w-4 h-4" />
                  </button>
                  <button type="button" onClick={() => insertFormat('\n- ')} className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground" title="List">
                    <List className="w-4 h-4" />
                  </button>
                </div>
                <textarea
                  ref={textareaRef}
                  id="content"
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  required
                  placeholder="Share your thoughts..."
                  rows="8"
                  className="w-full p-4 bg-transparent border-none focus:ring-0 resize-y min-h-[200px]"
                />
              </div>
            </div>

            {/* Access Control */}
            <div className="space-y-4 pt-4 border-t border-border">
              <h3 className="text-sm font-medium text-foreground">Access Control</h3>

              <label className={`flex items-center gap-3 p-4 rounded-xl border cursor-pointer transition-all ${formData.is_free
                  ? 'bg-primary/5 border-primary ring-1 ring-primary'
                  : 'bg-card border-border hover:border-primary/50'
                }`}>
                <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${formData.is_free ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground'
                  }`}>
                  {formData.is_free && <Check className="w-3 h-3" />}
                </div>
                <input
                  type="checkbox"
                  name="is_free"
                  checked={formData.is_free}
                  onChange={handleInputChange}
                  className="hidden"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 font-medium text-foreground">
                    <Globe className="w-4 h-4 text-primary" />
                    Public Post
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">Visible to everyone, including non-subscribers</p>
                </div>
              </label>

              {!formData.is_free && tiers.length > 0 && (
                <div className="space-y-3 pl-2 animate-in slide-in-from-top-2 duration-200">
                  <label className="text-sm font-medium text-muted-foreground">
                    Select tiers that can access this post:
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {tiers.map(tier => (
                      <label
                        key={tier.id}
                        className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${formData.tiers.includes(tier.id)
                            ? 'bg-secondary/50 border-secondary ring-1 ring-secondary'
                            : 'bg-card border-border hover:border-border/80'
                          }`}
                      >
                        <input
                          type="checkbox"
                          checked={formData.tiers.includes(tier.id)}
                          onChange={() => handleTierToggle(tier.id)}
                          className="hidden"
                        />
                        <div className={`w-4 h-4 rounded border flex items-center justify-center ${formData.tiers.includes(tier.id) ? 'border-secondary bg-secondary text-secondary-foreground' : 'border-muted-foreground'
                          }`}>
                          {formData.tiers.includes(tier.id) && <Check className="w-2.5 h-2.5" />}
                        </div>
                        <span className="text-sm font-medium text-foreground flex items-center gap-2">
                          <Lock className="w-3 h-3 text-muted-foreground" />
                          {tier.name}
                        </span>
                        <span className="text-xs text-muted-foreground ml-auto">
                          ${tier.price}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border bg-muted/10">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => document.getElementById('create-post-form').requestSubmit()}
            disabled={loading}
            className="px-6 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-full hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Post'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CreatePostModal;
