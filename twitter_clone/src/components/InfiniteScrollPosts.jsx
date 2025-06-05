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
import DeleteIcon from '@mui/icons-material/Delete';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useUser } from '../context/UserContext';

const getRecentTweets = async ({ postid }) => {
  const baseurl = import.meta.env.VITE_API_BASE_URL;
  const endpoint = 'tweets/recent';
  const url = baseurl + endpoint;

  try {
    const response = await axios.post(
      url,
      { userid: 'Alice406@example.com', postid },
      { headers: { 'Content-Type': 'application/json' } }
    );

    const tweets = response.data;

    const enrichedTweets = tweets.map(tweet => {
      return {
        postid: tweet.post_id,
        poster: tweet.username || tweet.userid,
        text: tweet.content || tweet.text,
        image: tweet.image_url || null,
        likes: 0,        // Set likes count to 0 for now
        retweets: 0,     // Set retweets count to 0 for now
        replies: tweet.replies || 0,
        isRetweet: tweet.is_retweet || false,
        liked: Boolean(Number(tweet.likes)),
        retweeted: Boolean(Number(tweet.retweets)),
        comment_ids: tweet.comment_ids || []
      };
    });

    console.log(enrichedTweets)

    return enrichedTweets;
  } catch (error) {
    console.error('API Error:', error);
    return [];
  }
};



/* 
This component creates the infinite scrolling effect that we know and love. 
If you pass in a rootPost (a single comment), then it will show only the 
replies to this comment you are looking at. 
*/
function InfiniteScrollPosts({ rootPost, setRootPost }) {
  const { logged_in_userid, updateUser } = useUser();
  const containerRef = useRef(null);
  const CHUNK_SIZE = 10;
  const [originalPosts, setOriginalPosts] = useState([]);
  const [allPosts, setAllPosts] = useState([]);
  const [visiblePosts, setVisiblePosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const tweets = await getRecentTweets({ postid: undefined });
      setOriginalPosts(tweets);
      setAllPosts(tweets);
      setVisiblePosts(tweets.slice(0, CHUNK_SIZE));
      setLoading(false);
    };

    fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (rootPost) {
        const tweets = await getRecentTweets({ postid: rootPost.postid });

        setAllPosts(tweets);
        setVisiblePosts(tweets);
      } else {
        // Set to original posts
        setAllPosts(originalPosts);
        setVisiblePosts(originalPosts.slice(0, CHUNK_SIZE));
      }
    }
    
    fetchData()
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
    console.log("USER CLICKED THE LIKE BUTTON")
    console.log("CHECK IF LIKE OR UNLIKE")
  };

  const toggleRetweet = (index) => {
    console.log("USER CLICKED THE RETWEET BUTTON")
    console.log("CHECK IF RETWEET OR UNRETWEET")
  };

  const handleReplyClick = (post) => {
    setRootPost(post);
  };

  if (loading) {
    return (
      <Box
        sx={{
          width: 600,
          height: 600,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mx: 'auto',
        }}
      >
        <Typography>Loading posts...</Typography>
      </Box>
    );
  }

  const handleDelete = async (postid) => {
    const baseurl = import.meta.env.VITE_API_BASE_URL;
    const endpoint = 'tweets/delete';
    const url = baseurl + endpoint;

    try {
      await axios.post(url, { postid }, {
        headers: { 'Content-Type': 'application/json' }
      });

      // Re-fetch updated tweets and update state
      const updatedTweets = await getRecentTweets();
      setOriginalPosts(updatedTweets);
      setAllPosts(updatedTweets);
      setVisiblePosts(updatedTweets.slice(0, CHUNK_SIZE));

    } catch (error) {
      console.error('Failed to delete post:', error);
    }
  };

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

         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'space-between' }}>
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
                onClick={() => handleReplyClick(post)}
              >
                <ChatBubbleOutlineIcon sx={{ fontSize: 20, color: 'gray' }} />
              </IconButton>
              <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
                {post.replies}
              </Typography>
            </Box>
          </Box>
        
        {String(post.poster) === String(logged_in_userid) && (
          <IconButton size="small" onClick={() => handleDelete(post.postid)}>
            <DeleteIcon sx={{ fontSize: 20, color: 'gray' }} />
          </IconButton>
        )} 
        </Box>

        </Box>
      ))}

      {visiblePosts.length === allPosts.length && visiblePosts.length > 0 && (
        <Typography textAlign="center" sx={{ mt: 2, color: 'gray' }}>
          🎉 You've reached the end!
        </Typography>
      )}
    </Box>
  );
}

export default InfiniteScrollPosts;