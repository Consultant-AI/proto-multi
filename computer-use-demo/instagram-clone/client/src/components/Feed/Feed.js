import React, { useState, useEffect } from 'react';
import PostCard from '../Post/PostCard';
import Stories from '../Story/Stories';
import { postsAPI } from '../../services/api';
import './Feed.css';

const Feed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadFeed();
  }, [page]);

  const loadFeed = async () => {
    try {
      setLoading(true);
      const response = await postsAPI.getFeed(page);
      const newPosts = response.data.data.posts;
      
      if (page === 1) {
        setPosts(newPosts);
      } else {
        setPosts(prev => [...prev, ...newPosts]);
      }
      
      setHasMore(response.data.data.pagination.page < response.data.data.pagination.totalPages);
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  return (
    <div className="feed-container">
      <div className="feed-main">
        <Stories />
        
        {loading && page === 1 ? (
          <div className="feed-loading">
            <div className="loading-spinner"></div>
            <p>Loading feed...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="feed-empty">
            <h2>Welcome to InstaClone!</h2>
            <p>Follow users to see their posts in your feed.</p>
          </div>
        ) : (
          <>
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
            
            {hasMore && (
              <div className="feed-load-more">
                <button onClick={loadMore} disabled={loading}>
                  {loading ? 'Loading...' : 'Load More'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="feed-sidebar">
        <div className="sidebar-suggestions">
          <h3>Suggestions For You</h3>
          <p>Feature coming soon!</p>
        </div>
      </div>
    </div>
  );
};

export default Feed;
