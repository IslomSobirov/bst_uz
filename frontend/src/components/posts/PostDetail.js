import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getApiUrl } from '../../config/api';
import './PostDetail.css';

function PostDetail({ post, onBack, user }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentContent, setCommentContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fetchComments = useCallback(async () => {
    if (!post) return;
    try {
      setLoading(true);
      const response = await axios.get(getApiUrl(`/api/posts/${post.id}/comments/`));
      setComments(response.data.results || response.data || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch comments');
      setLoading(false);
      console.error('Error fetching comments:', err);
    }
  }, [post]);

  useEffect(() => {
    if (post) {
      fetchComments();
    }
  }, [post, fetchComments]);

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!user || !commentContent.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      const token = localStorage.getItem('token');

      const response = await axios.post(
        getApiUrl('/api/comments/'),
        {
          post: post.id,
          content: commentContent
        },
        {
          headers: { Authorization: `Token ${token}` }
        }
      );

      setComments([...comments, response.data]);
      setCommentContent('');
      setSubmitting(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post comment');
      setSubmitting(false);
    }
  };

  if (!post) {
    return (
      <div className="post-detail-container">
        <div className="error">
          <h2>Post not found</h2>
          <button onClick={onBack}>Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="post-detail-container">
      <button className="back-button" onClick={onBack}>
        ← Back to Posts
      </button>

      <article className="post-detail">
        <div className="post-detail-header">
          <div className="post-author">
            <div className="author-avatar">
              {post.author?.avatar ? (
                <img src={post.author.avatar} alt={post.author.username} />
              ) : (
                <div className="avatar-placeholder">
                  {post.author?.username?.charAt(0).toUpperCase() || '?'}
                </div>
              )}
            </div>
            <div className="author-info">
              <h3 className="author-name">{post.author?.username || 'Unknown'}</h3>
              <span className="post-date">
                {new Date(post.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="post-meta">
            {post.category?.name && (
              <span className="category-tag">{post.category.name}</span>
            )}
            {post.is_free && <span className="free-badge">FREE</span>}
          </div>

          <h1 className="post-title">{post.title}</h1>
        </div>

        <div className="post-content-full">
          <p>{post.content}</p>
        </div>

        <div className="comments-section">
          <h2 className="comments-heading">
            Comments ({comments.length})
          </h2>

          {user ? (
            <form className="comment-form" onSubmit={handleSubmitComment}>
              <textarea
                className="comment-input"
                placeholder="Write a comment..."
                value={commentContent}
                onChange={(e) => setCommentContent(e.target.value)}
                rows="3"
                required
              />
              {error && <div className="error-message">{error}</div>}
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || !commentContent.trim()}
              >
                {submitting ? 'Posting...' : 'Post Comment'}
              </button>
            </form>
          ) : (
            <div className="login-prompt">
              <p>Please log in to comment on this post.</p>
            </div>
          )}

          {loading ? (
            <div className="loading-comments">Loading comments...</div>
          ) : comments.length === 0 ? (
            <div className="no-comments">
              <p>No comments yet. Be the first to comment!</p>
            </div>
          ) : (
            <div className="comments-list">
              {comments.map((comment) => (
                <div key={comment.id} className="comment-item">
                  <div className="comment-author">
                    <div className="comment-avatar">
                      {comment.author?.avatar ? (
                        <img src={comment.author.avatar} alt={comment.author.username} />
                      ) : (
                        <div className="avatar-placeholder tiny">
                          {comment.author?.username?.charAt(0).toUpperCase() || '?'}
                        </div>
                      )}
                    </div>
                    <div className="comment-info">
                      <span className="comment-author-name">
                        {comment.author?.username || 'Unknown'}
                      </span>
                      <span className="comment-date">
                        {new Date(comment.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <p className="comment-content">{comment.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </article>
    </div>
  );
}

export default PostDetail;
