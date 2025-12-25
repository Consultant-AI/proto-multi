const { User, Post, Follow } = require('../models');
const { Op } = require('sequelize');

// @desc    Get user profile
// @route   GET /api/users/:username
// @access  Private
exports.getUserProfile = async (req, res, next) => {
  try {
    const user = await User.findOne({
      where: { username: req.params.username },
      attributes: { exclude: ['password'] }
    });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Get user's posts
    const posts = await Post.findAll({
      where: { userId: user.id },
      order: [['createdAt', 'DESC']],
      attributes: ['id', 'imageUrl', 'likesCount', 'commentsCount', 'createdAt']
    });

    // Get followers count
    const followersCount = await Follow.count({
      where: { followingId: user.id }
    });

    // Get following count
    const followingCount = await Follow.count({
      where: { followerId: user.id }
    });

    // Check if current user follows this user
    const isFollowing = await Follow.findOne({
      where: {
        followerId: req.user.id,
        followingId: user.id
      }
    });

    res.status(200).json({
      success: true,
      data: {
        user: user.toJSON(),
        posts,
        postsCount: posts.length,
        followersCount,
        followingCount,
        isFollowing: !!isFollowing,
        isOwnProfile: user.id === req.user.id
      }
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
exports.updateProfile = async (req, res, next) => {
  try {
    const { fullName, bio, website } = req.body;

    const user = await User.findByPk(req.user.id);

    if (fullName) user.fullName = fullName;
    if (bio !== undefined) user.bio = bio;
    if (website !== undefined) user.website = website;

    if (req.file) {
      user.avatar = `/uploads/avatars/${req.file.filename}`;
    }

    await user.save();

    res.status(200).json({
      success: true,
      data: user.getPublicProfile()
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Search users
// @route   GET /api/users/search
// @access  Private
exports.searchUsers = async (req, res, next) => {
  try {
    const { q } = req.query;

    if (!q || q.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Search query is required'
      });
    }

    const users = await User.findAll({
      where: {
        [Op.or]: [
          { username: { [Op.iLike]: `%${q}%` } },
          { fullName: { [Op.iLike]: `%${q}%` } }
        ]
      },
      attributes: ['id', 'username', 'fullName', 'avatar'],
      limit: 20
    });

    res.status(200).json({
      success: true,
      data: users
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Follow/Unfollow user
// @route   POST /api/users/:userId/follow
// @access  Private
exports.toggleFollow = async (req, res, next) => {
  try {
    const { userId } = req.params;

    if (userId === req.user.id) {
      return res.status(400).json({
        success: false,
        message: 'You cannot follow yourself'
      });
    }

    const userToFollow = await User.findByPk(userId);

    if (!userToFollow) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Check if already following
    const existingFollow = await Follow.findOne({
      where: {
        followerId: req.user.id,
        followingId: userId
      }
    });

    if (existingFollow) {
      // Unfollow
      await existingFollow.destroy();
      
      res.status(200).json({
        success: true,
        data: { isFollowing: false }
      });
    } else {
      // Follow
      await Follow.create({
        followerId: req.user.id,
        followingId: userId
      });
      
      res.status(200).json({
        success: true,
        data: { isFollowing: true }
      });
    }
  } catch (error) {
    next(error);
  }
};

// @desc    Get user's followers
// @route   GET /api/users/:userId/followers
// @access  Private
exports.getFollowers = async (req, res, next) => {
  try {
    const follows = await Follow.findAll({
      where: { followingId: req.params.userId },
      include: [
        {
          model: User,
          as: 'follower',
          attributes: ['id', 'username', 'fullName', 'avatar']
        }
      ]
    });

    const followers = follows.map(f => f.follower);

    res.status(200).json({
      success: true,
      data: followers
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get user's following
// @route   GET /api/users/:userId/following
// @access  Private
exports.getFollowing = async (req, res, next) => {
  try {
    const follows = await Follow.findAll({
      where: { followerId: req.params.userId },
      include: [
        {
          model: User,
          as: 'following',
          attributes: ['id', 'username', 'fullName', 'avatar']
        }
      ]
    });

    const following = follows.map(f => f.following);

    res.status(200).json({
      success: true,
      data: following
    });
  } catch (error) {
    next(error);
  }
};
