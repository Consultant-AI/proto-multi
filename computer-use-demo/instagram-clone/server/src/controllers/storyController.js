const { Story, User } = require('../models');
const { Op } = require('sequelize');

// @desc    Create new story
// @route   POST /api/stories
// @access  Private
exports.createStory = async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'Please upload an image'
      });
    }

    const imageUrl = `/uploads/stories/${req.file.filename}`;
    
    // Stories expire after 24 hours
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    const story = await Story.create({
      userId: req.user.id,
      imageUrl,
      expiresAt
    });

    // Fetch story with user details
    const storyWithUser = await Story.findByPk(story.id, {
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
      data: storyWithUser
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get all active stories
// @route   GET /api/stories
// @access  Private
exports.getStories = async (req, res, next) => {
  try {
    const stories = await Story.findAll({
      where: {
        expiresAt: {
          [Op.gt]: new Date()
        }
      },
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar', 'fullName']
        }
      ],
      order: [['createdAt', 'DESC']]
    });

    // Group stories by user
    const storiesByUser = {};
    stories.forEach(story => {
      const userId = story.userId;
      if (!storiesByUser[userId]) {
        storiesByUser[userId] = {
          user: story.user,
          stories: []
        };
      }
      storiesByUser[userId].stories.push(story);
    });

    res.status(200).json({
      success: true,
      data: Object.values(storiesByUser)
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Get user's stories
// @route   GET /api/stories/user/:userId
// @access  Private
exports.getUserStories = async (req, res, next) => {
  try {
    const stories = await Story.findAll({
      where: {
        userId: req.params.userId,
        expiresAt: {
          [Op.gt]: new Date()
        }
      },
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'avatar', 'fullName']
        }
      ],
      order: [['createdAt', 'ASC']]
    });

    res.status(200).json({
      success: true,
      data: stories
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Delete story
// @route   DELETE /api/stories/:id
// @access  Private
exports.deleteStory = async (req, res, next) => {
  try {
    const story = await Story.findByPk(req.params.id);

    if (!story) {
      return res.status(404).json({
        success: false,
        message: 'Story not found'
      });
    }

    // Check ownership
    if (story.userId !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this story'
      });
    }

    await story.destroy();

    res.status(200).json({
      success: true,
      message: 'Story deleted successfully'
    });
  } catch (error) {
    next(error);
  }
};
