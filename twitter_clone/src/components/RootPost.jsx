import React from 'react';
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
import CloseIcon from '@mui/icons-material/Close'; // <-- Import Close icon

/*

When a user clicks the comment (reply) button, 
it will make the post sticky to the top of the screen to see 
as the RootPost. 

The RootPost will show this Post, and will handle showing the 
comments within this individual post as well. 
*/

const RootPost = ({ post, setRootPost }) => {



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
        position: 'relative', // <-- Make relative for positioning close icon
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
        <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
          {post.poster[0].toUpperCase()}
        </Avatar>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'black' }}>
          @{post.poster}
        </Typography>
      </Box>

      <Typography variant="body1" sx={{ color: 'black', mb: 1 }}>
        {post.text}
      </Typography>

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
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small">
            {post.liked ? (
              <FavoriteIcon sx={{ fontSize: 20, color: 'red' }} />
            ) : (
              <FavoriteBorderIcon sx={{ fontSize: 20, color: 'gray' }} />
            )}
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {post.likes}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small">
            {post.retweeted ? (
              <RepeatIcon sx={{ fontSize: 20, color: 'green' }} />
            ) : (
              <RepeatOutlinedIcon sx={{ fontSize: 20, color: 'gray' }} />
            )}
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {post.retweets}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton size="small">
            <ChatBubbleOutlineIcon sx={{ fontSize: 20, color: 'gray' }} />
          </IconButton>
          <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
            {post.replies}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default RootPost;
