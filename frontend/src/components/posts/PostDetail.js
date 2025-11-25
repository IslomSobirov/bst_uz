import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { ArrowLeft, Send, Calendar, Tag, MessageCircle } from 'lucide-react';
import { getApiUrl } from '../../config/api';

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
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <h2 className="text-2xl font-bold text-destructive">Post not found</h2>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-12">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Posts
      </button>

      <article className="bg-card border border-border/50 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-8 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {post.author?.avatar ? (
                <img
                  src={post.author.avatar}
                  alt={post.author.username}
                  className="w-12 h-12 rounded-full object-cover border-2 border-background shadow-sm"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
                  {post.author?.username?.charAt(0).toUpperCase() || '?'}
                </div>
              )}
              <div>
                <h3 className="font-bold text-lg text-foreground">
                  {post.author?.username || 'Unknown'}
                </h3>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="w-3 h-3" />
                  {new Date(post.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {post.category?.name && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-medium">
                  <Tag className="w-3 h-3" />
                  {post.category.name}
                </span>
              )}
              {post.is_free && (
                <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-600 text-xs font-bold uppercase tracking-wide border border-green-500/20">
                  Free
                </span>
              )}
            </div>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-foreground leading-tight">
            {post.title}
          </h1>

          <div className="prose prose-lg dark:prose-invert max-w-none text-foreground/90 leading-relaxed">
            <p className="whitespace-pre-wrap">{post.content}</p>
          </div>
        </div>

        {/* Comments Section */}
        <div className="bg-muted/30 border-t border-border/50 p-8">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-6">
            <MessageCircle className="w-5 h-5" />
            Comments ({comments.length})
          </h2>

          {user ? (
            <form onSubmit={handleSubmitComment} className="mb-8 space-y-3">
              <div className="relative">
                <textarea
                  className="w-full min-h-[100px] p-4 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-y"
                  placeholder="Write a thoughtful comment..."
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
                  required
                />
                <button
                  type="submit"
                  disabled={submitting || !commentContent.trim()}
                  className="absolute bottom-3 right-3 p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              {error && <p className="text-sm text-destructive font-medium">{error}</p>}
            </form>
          ) : (
            <div className="bg-primary/5 border border-primary/10 rounded-xl p-6 text-center mb-8">
              <p className="text-muted-foreground">
                Please <button onClick={() => { }} className="text-primary font-semibold hover:underline">log in</button> to join the conversation.
              </p>
            </div>
          )}

          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">Loading comments...</div>
            ) : comments.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground italic">
                No comments yet. Be the first to share your thoughts!
              </div>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="flex gap-4 p-4 rounded-xl bg-background border border-border/50">
                  <div className="flex-shrink-0">
                    {comment.author?.avatar ? (
                      <img
                        src={comment.author.avatar}
                        alt={comment.author.username}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground font-bold text-sm">
                        {comment.author?.username?.charAt(0).toUpperCase() || '?'}
                      </div>
                    )}
                  </div>
                  <div className="flex-grow space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm text-foreground">
                        {comment.author?.username || 'Unknown'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(comment.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-foreground/90 leading-relaxed">
                      {comment.content}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </article>
    </div>
  );
}

export default PostDetail;
