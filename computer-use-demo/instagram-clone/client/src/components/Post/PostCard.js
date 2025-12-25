import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiHeart, FiMessageCircle, FiBookmark, FiMoreHorizontal } from 'react-icons/fi';
import { FaHeart } from 'react-icons/fa';
import { postsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './Post.css';

const PostCard = ({ post, onUpdate }) => {
  const { user } = useAuth();
  const [isLiked, setIsLiked] = useState(post.isLiked);
  const [likesCount, setLikesCount] = useState(post.likesCount);
  const [showComments, setShowComments] = useState(false);
  const [comment, setComment] = useState('');
  const [comments, setComments] = useState(post.comments || []);
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL.replace('/api', '');

  const handleLike = async () => {
    try {
      const response = await postsAPI.toggleLike(post.id);
      setIsLiked(response.data.data.isLiked);
      setLikesCount(prev => response.data.data.isLiked ? prev + 1 : prev - 1);
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;

    setLoading(true);
    try {
      const response = await postsAPI.addComment(post.id, comment);
      setComments([response.data.data, ...comments]);
      setComment('');
    } catch (error) {
      console.error('Error adding comment:', error);
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <Link to={`/${post.user.username}`} className="post-user">
          <img
            src={`${API_BASE_URL}${post.user.avatar}`}
            alt={post.user.username}
            className="post-avatar"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/40';
            }}
          />
          <span className="post-username">{post.user.username}</span>
        </Link>
        <button className="post-options">
          <FiMoreHorizontal />
        </button>
      </div>

      <div className="post-image-container">
        <img
          src={`${API_BASE_URL}${post.imageUrl}`}
          alt="Post"
          className="post-image"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/600';
          }}
        />
      </div>

      <div className="post-actions">
        <div className="post-actions-left">
          <button onClick={handleLike} className="post-action-btn">
            {isLiked ? (
              <FaHeart size={24} color="#ed4956" />
            ) : (
              <FiHeart size={24} />
            )}
          </button>
          <button
            onClick={() => setShowComments(!showComments)}
            className="post-action-btn"
          >
            <FiMessageCircle size={24} />
          </button>
        </div>
        <button className="post-action-btn">
          <FiBookmark size={24} />
        </button>
      </div>

      <div className="post-info">
        <div className="post-likes">
          {likesCount} {likesCount === 1 ? 'like' : 'likes'}
        </div>
        
        {post.caption && (
          <div className="post-caption">
            <Link to={`/${post.user.username}`} className="caption-username">
              {post.user.username}
            </Link>
            <span className="caption-text">{post.caption}</span>
          </div>
        )}

        {comments.length > 0 && (
          <button
            className="view-comments-btn"
            onClick={() => setShowComments(!showComments)}
          >
            View all {comments.length} comments
          </button>
        )}

        {showComments && (
          <div className="comments-section">
            {comments.map((c) => (
              <div key={c.id} className="comment">
                <Link to={`/${c.user.username}`} className="comment-username">
                  {c.user.username}
                </Link>
                <span className="comment-text">{c.text}</span>
              </div>
            ))}
          </div>
        )}

        <div className="post-date">{formatDate(post.createdAt)}</div>
      </div>

      <form className="add-comment" onSubmit={handleComment}>
        <input
          type="text"
          placeholder="Add a comment..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={!comment.trim() || loading}
          className={comment.trim() ? 'active' : ''}
        >
          Post
        </button>
      </form>
    </div>
  );
};

export default PostCard;
