import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../../services/api';
import { FiImage, FiX } from 'react-icons/fi';
import './Upload.css';

const Upload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      setSelectedFile(file);
      setError('');
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('caption', caption);
      formData.append('location', location);

      await postsAPI.createPost(formData);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <h2>Create New Post</h2>

        {error && <div className="upload-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          {!preview ? (
            <div className="upload-dropzone">
              <input
                type="file"
                id="file-input"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
              />
              <label htmlFor="file-input" className="file-label">
                <FiImage size={48} />
                <p>Select photo from your computer</p>
                <span>Max file size: 5MB</span>
              </label>
            </div>
          ) : (
            <div className="upload-preview">
              <button
                type="button"
                onClick={handleRemoveFile}
                className="remove-preview"
              >
                <FiX size={24} />
              </button>
              <img src={preview} alt="Preview" />
            </div>
          )}

          <div className="upload-form-group">
            <textarea
              placeholder="Write a caption..."
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows="3"
              maxLength="2200"
            />
            <div className="char-count">
              {caption.length}/2200
            </div>
          </div>

          <div className="upload-form-group">
            <input
              type="text"
              placeholder="Add location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          <div className="upload-actions">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="upload-cancel"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="upload-submit"
              disabled={!selectedFile || loading}
            >
              {loading ? 'Posting...' : 'Share'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Upload;
