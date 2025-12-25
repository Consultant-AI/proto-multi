import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { usersAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { FiGrid, FiSettings } from 'react-icons/fi';
import './Profile.css';

const Profile = () => {
  const { username } = useParams();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL.replace('/api', '');

  useEffect(() => {
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    try {
      const response = await usersAPI.getUserProfile(username);
      setProfile(response.data.data);
      setIsFollowing(response.data.data.isFollowing);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    try {
      const response = await usersAPI.toggleFollow(profile.user.id);
      setIsFollowing(response.data.data.isFollowing);
      // Update followers count
      setProfile(prev => ({
        ...prev,
        followersCount: prev.followersCount + (response.data.data.isFollowing ? 1 : -1)
      }));
    } catch (error) {
      console.error('Error toggling follow:', error);
    }
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-error">
        <h2>User not found</h2>
      </div>
    );
  }

  const isOwnProfile = profile.isOwnProfile;

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar-container">
          <img
            src={`${API_BASE_URL}${profile.user.avatar}`}
            alt={profile.user.username}
            className="profile-avatar-large"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/150';
            }}
          />
        </div>

        <div className="profile-info">
          <div className="profile-info-header">
            <h1 className="profile-username">{profile.user.username}</h1>
            {isOwnProfile ? (
              <button className="profile-edit-btn">
                <FiSettings /> Edit Profile
              </button>
            ) : (
              <button
                className={`profile-follow-btn ${isFollowing ? 'following' : ''}`}
                onClick={handleFollow}
              >
                {isFollowing ? 'Following' : 'Follow'}
              </button>
            )}
          </div>

          <div className="profile-stats">
            <div className="stat">
              <span className="stat-value">{profile.postsCount}</span>
              <span className="stat-label">posts</span>
            </div>
            <div className="stat">
              <span className="stat-value">{profile.followersCount}</span>
              <span className="stat-label">followers</span>
            </div>
            <div className="stat">
              <span className="stat-value">{profile.followingCount}</span>
              <span className="stat-label">following</span>
            </div>
          </div>

          <div className="profile-bio">
            <p className="profile-fullname">{profile.user.fullName}</p>
            {profile.user.bio && <p className="profile-bio-text">{profile.user.bio}</p>}
            {profile.user.website && (
              <a
                href={profile.user.website}
                target="_blank"
                rel="noopener noreferrer"
                className="profile-website"
              >
                {profile.user.website}
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="profile-tabs">
        <button className="profile-tab active">
          <FiGrid /> POSTS
        </button>
      </div>

      <div className="profile-posts">
        {profile.posts.length === 0 ? (
          <div className="profile-no-posts">
            <h2>No Posts Yet</h2>
            {isOwnProfile && <p>Start sharing your moments!</p>}
          </div>
        ) : (
          <div className="profile-posts-grid">
            {profile.posts.map((post) => (
              <div key={post.id} className="profile-post-item">
                <img
                  src={`${API_BASE_URL}${post.imageUrl}`}
                  alt="Post"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/300';
                  }}
                />
                <div className="profile-post-overlay">
                  <div className="post-stat">
                    <span>❤️ {post.likesCount}</span>
                  </div>
                  <div className="post-stat">
                    <span>💬 {post.commentsCount}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
