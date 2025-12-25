const express = require('express');
const router = express.Router();
const {
  createPost,
  getFeed,
  getPost,
  deletePost,
  toggleLike,
  addComment,
  deleteComment
} = require('../controllers/postController');
const { protect } = require('../middleware/auth');
const upload = require('../middleware/upload');

router.route('/')
  .post(protect, upload.single('image'), createPost);

router.get('/feed', protect, getFeed);

router.route('/:id')
  .get(protect, getPost)
  .delete(protect, deletePost);

router.post('/:id/like', protect, toggleLike);

router.route('/:id/comments')
  .post(protect, addComment);

router.delete('/:postId/comments/:commentId', protect, deleteComment);

module.exports = router;
