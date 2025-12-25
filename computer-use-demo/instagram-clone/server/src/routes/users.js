const express = require('express');
const router = express.Router();
const {
  getUserProfile,
  updateProfile,
  searchUsers,
  toggleFollow,
  getFollowers,
  getFollowing
} = require('../controllers/userController');
const { protect } = require('../middleware/auth');
const upload = require('../middleware/upload');

router.get('/search', protect, searchUsers);
router.put('/profile', protect, upload.single('avatar'), updateProfile);
router.get('/:username', protect, getUserProfile);
router.post('/:userId/follow', protect, toggleFollow);
router.get('/:userId/followers', protect, getFollowers);
router.get('/:userId/following', protect, getFollowing);

module.exports = router;
