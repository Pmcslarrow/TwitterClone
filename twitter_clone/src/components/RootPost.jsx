import React, { useState } from 'react';
import {
  Box,
  Typography,
  Avatar,
  IconButton,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import RepeatIcon from '@mui/icons-material/Repeat';
import RepeatOutlinedIcon from '@mui/icons-material/RepeatOutlined';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import { useUser } from '../context/UserContext';

const RootPost = ({ post, setRootPost }) => {
  const { user } = useUser();

  const [postState, setPostState] = useState({
    liked: post.liked,
    retweeted: post.retweeted,
    likes: post.likes,
    retweets: post.retweets,
    replies: post.replies,
  });

  if (!post || post === true) {
    return null;
  }

  const toggleLike = async () => {
    const isLiked = postState.liked;

    // Optimistically update UI
    setPostState(prev => ({
      ...prev,
      liked: !isLiked,
      likes: isLiked ? prev.likes - 1 : prev.likes + 1,
    }));

    try {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = isLiked ? 'tweets/unlike' : 'tweets/like';
      const url = baseurl + endpoint;

      await axios.post(url, {
        userid: user.email,
        postid: post.postid,
      }, {
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (error) {
      // Revert on error
      setPostState(prev => ({
        ...prev,
        liked: isLiked,
        likes: isLiked ? prev.likes + 1 : prev.likes - 1,
      }));
      console.error('Failed to toggle like:', error);
    }
  };

  const toggleRetweet = async () => {
    const isRetweeted = postState.retweeted;

    // Optimistically update UI
    setPostState(prev => ({
      ...prev,
      retweeted: !isRetweeted,
      retweets: isRetweeted ? prev.retweets - 1 : prev.retweets + 1,
    }));

    try {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = isRetweeted ? 'tweets/unretweet' : 'tweets/retweet';
      const url = baseurl + endpoint;

      await axios.post(url, {
        userid: user.email,
        postid: post.postid,
      }, {
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (error) {
      // Revert on error
      setPostState(prev => ({
        ...prev,
        retweeted: isRetweeted,
        retweets: isRetweeted ? prev.retweets + 1 : prev.retweets - 1,
      }));
      console.error('Failed to toggle retweet:', error);
    }
  };

  return (
    <Box
      sx={{
        bgcolor: 'white',
        p: 2,
        mb: 2,
        borderRadius: 2,
        boxShadow: 2,
        border: '2px solid #4CAF50',
        width: 600,
        mx: 'auto',
        position: 'relative',
      }}
    >
      {/* Close Button */}
      <IconButton
        size="small"
        onClick={() => setRootPost(null)}
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          color: 'gray',
        }}
      >
        <CloseIcon />
      </IconButton>

      {post.isRetweet && (
        <Typography variant="caption" sx={{ color: 'gray', mb: 1 }}>
          <RepeatIcon sx={{ fontSize: 16, verticalAlign: 'middle' }} /> Retweeted
        </Typography>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Avatar src={post?.image} sx={{ width: 32, height: 32, mr: 1 }}>
          {post.poster[0].toUpperCase()}
        </Avatar>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'black' }}>
          {post.username}
        </Typography>
      </Box>

      <Typography variant="body1" sx={{ color: 'black', mb: 1 }}>
        {post.text}
      </Typography>
{/* 
      {post.image && (
        <Box
          component="img"
          src={post.image}
          alt="Post"
          sx={{
            width: '100%',
            height: 'auto',
            borderRadius: 2,
            mb: 1,
          }}
        />
      )} */}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small" onClick={toggleLike}>
            {postState.liked ? (
              <FavoriteIcon sx={{ fontSize: 20, color: 'red' }} />
            ) : (
              <FavoriteBorderIcon sx={{ fontSize: 20, color: 'gray' }} />
            )}
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {postState.likes}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small" onClick={toggleRetweet}>
            {postState.retweeted ? (
              <RepeatIcon sx={{ fontSize: 20, color: 'green' }} />
            ) : (
              <RepeatOutlinedIcon sx={{ fontSize: 20, color: 'gray' }} />
            )}
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {postState.retweets}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small">
            <ChatBubbleOutlineIcon sx={{ fontSize: 20, color: 'gray' }} />
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {postState.replies}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default RootPost;
