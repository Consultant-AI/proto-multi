const express = require('express');
const router = express.Router();
const {
  createStory,
  getStories,
  getUserStories,
  deleteStory
} = require('../controllers/storyController');
const { protect } = require('../middleware/auth');
const upload = require('../middleware/upload');

router.route('/')
  .get(protect, getStories)
  .post(protect, upload.single('image'), createStory);

router.get('/user/:userId', protect, getUserStories);
router.delete('/:id', protect, deleteStory);

module.exports = router;
