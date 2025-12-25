import React, { useState, useEffect } from 'react';
import { storiesAPI } from '../../services/api';
import './Stories.css';

const Stories = () => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_URL.replace('/api', '');

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      const response = await storiesAPI.getStories();
      setStories(response.data.data);
    } catch (error) {
      console.error('Error loading stories:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="stories-container">
        <div className="stories-loading">Loading stories...</div>
      </div>
    );
  }

  if (stories.length === 0) {
    return null;
  }

  return (
    <div className="stories-container">
      <div className="stories-scroll">
        {stories.map((storyGroup) => (
          <div key={storyGroup.user.id} className="story-item">
            <div className="story-ring">
              <img
                src={`${API_BASE_URL}${storyGroup.user.avatar}`}
                alt={storyGroup.user.username}
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/56';
                }}
              />
            </div>
            <span className="story-username">
              {storyGroup.user.username.length > 10
                ? `${storyGroup.user.username.substring(0, 10)}...`
                : storyGroup.user.username}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Stories;
