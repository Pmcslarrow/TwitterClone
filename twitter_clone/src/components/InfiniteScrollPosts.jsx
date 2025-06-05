import React, { useEffect, useRef, useState } from 'react';
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
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// Utility to generate mock posts
const generateMockPosts = (count) => {
  const users = ['alice', 'bob', 'carol', 'dave'];
  const sampleTexts = [
    'Just enjoying the sunshine ☀️',
    'Building something cool in React!',
    'Anyone else watching the game tonight?',
    'Here’s a thought about software architecture...',
  ];

  return Array.from({ length: count }, (_, i) => {
    const isRetweet = Math.random() < 0.3;
    const hasImage = Math.random() < 0.4;
    return {
      postid: 20000 + i,
      poster: users[i % users.length],
      text: sampleTexts[i % sampleTexts.length],
      image: hasImage ? 'https://via.placeholder.com/400x200?text=Image' : null,
      likes: Math.floor(Math.random() * 50),
      retweets: Math.floor(Math.random() * 20),
      replies: Math.floor(Math.random() * 10),
      isRetweet,
      liked: Math.random() < 0.3,
      retweeted: Math.random() < 0.2,
    };
  });
};


/* 

This component creates the infinite scrolling effect that we know and love. 
If you pass in a rootPost (a single comment), then it will show only the 
replies to this comment you are looking at. 

*/
function InfiniteScrollPosts({ rootPost, setRootPost }) {
  const containerRef = useRef(null);
  const CHUNK_SIZE = 10;
  const [originalPosts] = useState(() => generateMockPosts(50));
  const [allPosts, setAllPosts] = useState(originalPosts);
  const [visiblePosts, setVisiblePosts] = useState(originalPosts.slice(0, CHUNK_SIZE));
  const navigate = useNavigate();

  // Getting all recent posts
  useEffect(() => {
    const baseurl = import.meta.env.VITE_API_BASE_URL;
    const endpoint = 'tweets/recent'
    const url = baseurl + endpoint

    axios.post(url, { userid: 'Alice406@example.com' }, {
      headers: { 'Content-Type': 'application/json' }
    }).then(response => {
      console.log(response.data);
    })
    .catch(error => {
      console.error('API Error:', error);
    });
  }, [])

  useEffect(() => {
    if (rootPost) {
      // Only posts associated to rootPost
      console.log("GET ALL COMMENTS FOR THIS rootPost");
      console.log(rootPost);

      const filteredPosts = originalPosts.filter(
        post => post.postid !== rootPost.postid
      );

      const trimmedPosts = filteredPosts.slice(0, 3);

      setAllPosts(trimmedPosts);
      setVisiblePosts(trimmedPosts);
    } else {
      // Set to original posts
      setAllPosts(originalPosts);
      setVisiblePosts(originalPosts.slice(0, CHUNK_SIZE));
    }
  }, [rootPost, originalPosts]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [visiblePosts]);

  const loadMorePosts = () => {
    setVisiblePosts((prev) => {
      const nextChunk = allPosts.slice(prev.length, prev.length + CHUNK_SIZE);
      return [...prev, ...nextChunk];
    });
  };

  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    if (scrollHeight - scrollTop - clientHeight < 100) {
      if (visiblePosts.length < allPosts.length) {
        loadMorePosts();
      }
    }
  };

  const toggleLike = (index) => {
    setVisiblePosts((prev) => {
      const updated = [...prev];
      const post = updated[index];
      post.liked = !post.liked;
      post.likes += post.liked ? 1 : -1;
      return updated;
    });
  };

  const toggleRetweet = (index) => {
    setVisiblePosts((prev) => {
      const updated = [...prev];
      const post = updated[index];
      post.retweeted = !post.retweeted;
      post.retweets += post.retweeted ? 1 : -1;
      return updated;
    });
  };

  const handleReplyClick = (post) => {
    setRootPost(post)
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        width: 600,
        height: 600,
        overflowY: 'auto',
        bgcolor: 'white',
        p: 2,
        mx: 'auto',
        scrollbarWidth: 'none', // Firefox
        '&::-webkit-scrollbar': {
          display: 'none', // Chrome, Safari, Edge
        },
      }}
    >
      {visiblePosts.map((post, idx) => (
        <Box
          key={post.postid}
          sx={{
            bgcolor: 'white',
            p: 2,
            mb: 2,
            borderRadius: 2,
            boxShadow: 2,
          }}
        >
          {post.isRetweet && (
            <Typography variant="caption" sx={{ color: 'gray', mb: 1 }}>
              <RepeatIcon sx={{ fontSize: 16, verticalAlign: 'middle' }} /> Retweeted
            </Typography>
          )}

          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Avatar onClick={() => navigate(`/profile/:${post.poster}`)} sx={{ width: 32, height: 32, mr: 1, '&:hover': {bgcolor: '#4CAF50', cursor: 'pointer'}}}>
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
              <IconButton size="small" onClick={() => toggleLike(idx)}>
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
              <IconButton size="small" onClick={() => toggleRetweet(idx)}>
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
              <IconButton
                size="small"
                onClick = {() => handleReplyClick(post) }
              >
                <ChatBubbleOutlineIcon sx={{ fontSize: 20, color: 'gray' }} />
              </IconButton>
              <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
                {post.replies}
              </Typography>
            </Box>
          </Box>
        </Box>
      ))}

      {visiblePosts.length === allPosts.length && (
        <Typography textAlign="center" sx={{ mt: 2, color: 'gray' }}>
          🎉 You've reached the end!
        </Typography>
      )}
    </Box>
  );
};

export default InfiniteScrollPosts;