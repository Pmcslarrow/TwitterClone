import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Typography,
  Avatar,
  IconButton,
  setRef,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import RepeatIcon from '@mui/icons-material/Repeat';
import RepeatOutlinedIcon from '@mui/icons-material/RepeatOutlined';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import { useNavigate } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import axios from 'axios';
import { useUser } from '../context/UserContext';

const getRecentTweets = async ({ userid, postid }) => {
  if (!userid || !postid) {
    return [];
  }

  const baseurl = import.meta.env.VITE_API_BASE_URL;
  const endpoint = 'tweets/recent';
  const url = baseurl + endpoint;

  try {
    const response = await axios.post(
      url,
      { userid: userid, postid },
      { headers: { 'Content-Type': 'application/json' } }
    );
    const tweets = response.data;

    const allPostIds = tweets.map(post => post.post_id);
    const countsUrl = baseurl + 'tweets/counts';
    const countsResponse = await axios.post(countsUrl, { postids: allPostIds }, {
      headers: { 'Content-Type': 'application/json' }
    });

    const { likes, retweets, comment_counts} = countsResponse.data;

    const enrichedTweets = tweets.map(tweet => {
      const postId = tweet.post_id;

      const likeEntry = likes.find(entry => entry.originalpost === postId);
      const likeCount = likeEntry ? likeEntry.like_count : 0;

      const retweetEntry = retweets.find(entry => entry.originalpost === postId);
      const retweetCount = retweetEntry ? retweetEntry.retweet_count : 0;

      const commentEntry = comment_counts.find(entry => entry.reply_to_postid === postId);
      const commentCount = commentEntry ? commentEntry.comment_count : 0;

      return {
        postid: postId,
        poster: tweet.userid,
        text: tweet.content || tweet.text,
        image: tweet.image_url || null,
        likes: likeCount,
        retweets: retweetCount,
        replies: commentCount,
        liked: Boolean(Number(tweet.liked)),
        retweeted: Boolean(Number(tweet.retweeted)),
        username: tweet.username
      };
    });

    return enrichedTweets;
  } catch (error) {
    console.error('API Error:', error);
    return [];
  }
};

function InfiniteScrollPosts({ rootPost, setRootPost, reload, setReload }) {
  const { user, updateUser } = useUser();
  const containerRef = useRef(null);
  const CHUNK_SIZE = 10;
  const [originalPosts, setOriginalPosts] = useState([]);
  const [allPosts, setAllPosts] = useState([]);
  const [visiblePosts, setVisiblePosts] = useState([]);
  const [isFetching, setIsFetching] = useState(false);
    
  // Add state for tracking post interactions
  const [postStates, setPostStates] = useState({});
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setIsFetching(true);

      const tweets = await getRecentTweets({ userid: user?.email, postid: rootPost ? rootPost.postid : undefined });

      setAllPosts(tweets);
      setVisiblePosts(tweets ? tweets.slice(0, CHUNK_SIZE) : null);
      
      // Initialize post states
      const initialStates = {};
      tweets.forEach(tweet => {
        initialStates[tweet.postid] = {
          liked: tweet.liked,
          retweeted: tweet.retweeted,
          likes: tweet.likes,
          retweets: tweet.retweets,
          replies: tweet.replies
        };
      });
      setPostStates(initialStates);
      
      setIsFetching(false);
    };

    if (reload || rootPost !== undefined) {
      fetchData();
      setReload(false);
    }
  }, [reload, rootPost]);

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

  const toggleLike = async (post) => {
    const currentState = postStates[post.postid];
    const isLiked = currentState?.liked ?? post.liked;
    
    // Optimistically update UI
    setPostStates(prev => ({
      ...prev,
      [post.postid]: {
        ...prev[post.postid],
        liked: !isLiked,
        likes: isLiked ? (prev[post.postid]?.likes ?? post.likes) - 1 : (prev[post.postid]?.likes ?? post.likes) + 1
      }
    }));

    try {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = isLiked ? 'tweets/unlike' : 'tweets/like';
      const url = baseurl + endpoint;

      const response = await axios.post(url, { 
        userid: user.email, 
        postid: post.postid 
      }, {
        headers: { 'Content-Type': 'application/json' }
      });

      console.log(response);
    } catch (error) {
      // Revert on error
      setPostStates(prev => ({
        ...prev,
        [post.postid]: {
          ...prev[post.postid],
          liked: isLiked,
          likes: isLiked ? (prev[post.postid]?.likes ?? post.likes) + 1 : (prev[post.postid]?.likes ?? post.likes) - 1
        }
      }));
      console.error('Failed to toggle like:', error);
    }
  };

  const toggleRetweet = async (post) => {
    const currentState = postStates[post.postid];
    const isRetweeted = currentState?.retweeted ?? post.retweeted;
    
    // Optimistically update UI
    setPostStates(prev => ({
      ...prev,
      [post.postid]: {
        ...prev[post.postid],
        retweeted: !isRetweeted,
        retweets: isRetweeted ? (prev[post.postid]?.retweets ?? post.retweets) - 1 : (prev[post.postid]?.retweets ?? post.retweets) + 1
      }
    }));

    try {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = isRetweeted ? 'tweets/unretweet' : 'tweets/retweet';
      const url = baseurl + endpoint;

      const response = await axios.post(url, { 
        userid: user.email, 
        postid: post.postid 
      }, {
        headers: { 'Content-Type': 'application/json' }
      });

      console.log(response);
    } catch (error) {
      // Revert on error
      setPostStates(prev => ({
        ...prev,
        [post.postid]: {
          ...prev[post.postid],
          retweeted: isRetweeted,
          retweets: isRetweeted ? (prev[post.postid]?.retweets ?? post.retweets) + 1 : (prev[post.postid]?.retweets ?? post.retweets) - 1
        }
      }));
      console.error('Failed to toggle retweet:', error);
    }
  };

  const handleReplyClick = (post) => {
    setRootPost(post);
  };

  const handleDelete = async (postid) => {
    const baseurl = import.meta.env.VITE_API_BASE_URL;
    const endpoint = 'tweets/delete';
    const url = baseurl + endpoint;

    try {
      await axios.post(url, { postid }, {
        headers: { 'Content-Type': 'application/json' }
      });

      const updatedTweets = await getRecentTweets({ userid: user.email, postid: undefined });
      setReload(true);
      setIsFetching(true);
      setOriginalPosts(updatedTweets);
      setAllPosts(updatedTweets);
      setVisiblePosts(updatedTweets.slice(0, CHUNK_SIZE));

    } catch (error) {
      console.error('Failed to delete post:', error);
    }
  };

  if (isFetching) {
    return (
      <CircularProgress sx={{ color: '#4CAF50' }}  />
    );
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
        scrollbarWidth: 'none',
        '&::-webkit-scrollbar': {
          display: 'none',
        },
      }}
    >
      {visiblePosts.map((post, idx) => {
        // Get current state or fall back to original post data
        const currentState = postStates[post.postid] || {
          liked: post.liked,
          retweeted: post.retweeted,
          likes: post.likes,
          retweets: post.retweets,
          replies: post.replies
        };

        return (
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
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Avatar onClick={() => navigate(`/profile/:${post.username}`)} sx={{ width: 32, height: 32, mr: 1, '&:hover': {bgcolor: '#4CAF50', cursor: 'pointer'}}}>
                {post.poster[0].toUpperCase()}
              </Avatar>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'black' }}>
                @{post.poster}
              </Typography>
              <Typography sx={{ fontWeight: 'bold', color: 'black' }}>
                {post.postid}
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
                  <IconButton size="small" onClick={() => toggleLike(post)}>
                    {currentState.liked ? (
                      <FavoriteIcon sx={{ fontSize: 20, color: 'red' }} />
                    ) : (
                      <FavoriteBorderIcon sx={{ fontSize: 20, color: 'gray' }} />
                    )}
                  </IconButton>
                  <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
                    {currentState.likes}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <IconButton size="small" onClick={() => toggleRetweet(post)}>
                    {currentState.retweeted ? (
                      <RepeatIcon sx={{ fontSize: 20, color: 'green' }} />
                    ) : (
                      <RepeatOutlinedIcon sx={{ fontSize: 20, color: 'gray' }} />
                    )}
                  </IconButton>
                  <Typography sx={{ color: 'black', mb: 1 }} variant="body2">
                    {currentState.retweets}
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
                    {currentState.replies}
                  </Typography>
                </Box>
              </Box>
            
              {String(post.poster) === String(user.email) && (
                <IconButton size="small" onClick={() => handleDelete(post.postid)}>
                  <DeleteIcon sx={{ fontSize: 20, color: 'gray' }} />
                </IconButton>
              )} 
            </Box>
          </Box>
        );
      })}

      {visiblePosts.length === allPosts.length && visiblePosts.length > 0 && (
        <Typography textAlign="center" sx={{ mt: 2, color: 'gray' }}>
          🎉 You've reached the end!
        </Typography>
      )}
    </Box>
  );
}

export default InfiniteScrollPosts;