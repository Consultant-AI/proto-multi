const { Post, User, Like, Comment, Follow } = require('../models');
const { Op } = require('sequelize');

// @desc    Create new post
// @route   POST /api/posts
// @access  Private
exports.createPost = async (req, res, next) => {
  try {
    const { caption, location } = req.body;

    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'Please upload an image'
      });
    }

    const imageUrl = `/uploads/posts/${req.file.filename}`;

    const post = await Post.create({
      userId: req.user.id,
      imageUrl,
      caption,
      location
    });

    // Fetch post with user details
    const postWithUser = await Post.findByPk(post.id, {
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar', 'fullName']
        }
      ]
    });

    res.status(201).json({
      success: true,
      data: postWithUser
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get feed posts
// @route   GET /api/posts/feed
// @access  Private
exports.getFeed = async (req, res, next) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    // Get users that current user follows
    const following = await Follow.findAll({
      where: { followerId: req.user.id },
      attributes: ['followingId']
    });

    const followingIds = following.map(f => f.followingId);
    followingIds.push(req.user.id); // Include own posts

    // Get posts from followed users
    const posts = await Post.findAndCountAll({
      where: {
        userId: {
          [Op.in]: followingIds
        }
      },
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar', 'fullName']
        },
        {
          model: Like,
          as: 'likes',
          attributes: ['userId'],
          required: false
        },
        {
          model: Comment,
          as: 'comments',
          attributes: ['id', 'text', 'userId', 'createdAt'],
          include: [
            {
              model: User,
              as: 'user',
              attributes: ['id', 'username', 'avatar']
            }
          ],
          limit: 3,
          order: [['createdAt', 'DESC']]
        }
      ],
      order: [['createdAt', 'DESC']],
      limit,
      offset
    });

    // Add isLiked flag for current user
    const postsWithLikeStatus = posts.rows.map(post => {
      const postData = post.toJSON();
      postData.isLiked = postData.likes.some(like => like.userId === req.user.id);
      return postData;
    });

    res.status(200).json({
      success: true,
      data: {
        posts: postsWithLikeStatus,
        pagination: {
          page,
          limit,
          totalPages: Math.ceil(posts.count / limit),
          totalPosts: posts.count
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get single post
// @route   GET /api/posts/:id
// @access  Private
exports.getPost = async (req, res, next) => {
  try {
    const post = await Post.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar', 'fullName']
        },
        {
          model: Like,
          as: 'likes',
          attributes: ['userId']
        },
        {
          model: Comment,
          as: 'comments',
          include: [
            {
              model: User,
              as: 'user',
              attributes: ['id', 'username', 'avatar']
            }
          ],
          order: [['createdAt', 'DESC']]
        }
      ]
    });

    if (!post) {
      return res.status(404).json({
        success: false,
        message: 'Post not found'
      });
    }

    const postData = post.toJSON();
    postData.isLiked = postData.likes.some(like => like.userId === req.user.id);

    res.status(200).json({
      success: true,
      data: postData
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Delete post
// @route   DELETE /api/posts/:id
// @access  Private
exports.deletePost = async (req, res, next) => {
  try {
    const post = await Post.findByPk(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        message: 'Post not found'
      });
    }

    // Check ownership
    if (post.userId !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this post'
      });
    }

    await post.destroy();

    res.status(200).json({
      success: true,
      message: 'Post deleted successfully'
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Like/Unlike post
// @route   POST /api/posts/:id/like
// @access  Private
exports.toggleLike = async (req, res, next) => {
  try {
    const post = await Post.findByPk(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        message: 'Post not found'
      });
    }

    // Check if already liked
    const existingLike = await Like.findOne({
      where: {
        postId: req.params.id,
        userId: req.user.id
      }
    });

    if (existingLike) {
      // Unlike
      await existingLike.destroy();
      await post.decrement('likesCount');
      
      res.status(200).json({
        success: true,
        data: { isLiked: false }
      });
    } else {
      // Like
      await Like.create({
        postId: req.params.id,
        userId: req.user.id
      });
      await post.increment('likesCount');
      
      res.status(200).json({
        success: true,
        data: { isLiked: true }
      });
    }
  } catch (error) {
    next(error);
  }
};

// @desc    Add comment to post
// @route   POST /api/posts/:id/comments
// @access  Private
exports.addComment = async (req, res, next) => {
  try {
    const { text } = req.body;

    if (!text || text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Comment text is required'
      });
    }

    const post = await Post.findByPk(req.params.id);

    if (!post) {
      return res.status(404).json({
        success: false,
        message: 'Post not found'
      });
    }

    const comment = await Comment.create({
      postId: req.params.id,
      userId: req.user.id,
      text
    });

    await post.increment('commentsCount');

    // Fetch comment with user details
    const commentWithUser = await Comment.findByPk(comment.id, {
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar']
        }
      ]
    });

    res.status(201).json({
      success: true,
      data: commentWithUser
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Delete comment
// @route   DELETE /api/posts/:postId/comments/:commentId
// @access  Private
exports.deleteComment = async (req, res, next) => {
  try {
    const comment = await Comment.findByPk(req.params.commentId);

    if (!comment) {
      return res.status(404).json({
        success: false,
        message: 'Comment not found'
      });
    }

    // Check ownership
    if (comment.userId !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this comment'
      });
    }

    const post = await Post.findByPk(comment.postId);
    await comment.destroy();
    
    if (post) {
      await post.decrement('commentsCount');
    }

    res.status(200).json({
      success: true,
      message: 'Comment deleted successfully'
    });
  } catch (error) {
    next(error);
  }
};
