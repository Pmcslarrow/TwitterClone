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

const getRecentTweets = async ({ postid }) => {
  const baseurl = import.meta.env.VITE_API_BASE_URL;
  const endpoint = 'tweets/recent';
  const url = baseurl + endpoint;

  try {
    //
    // Getting the posts and their info from PostInfo
    //
    const response = await axios.post(
      url,
      { userid: 'Alice406@example.com', postid },
      { headers: { 'Content-Type': 'application/json' } }
    );
    const tweets = response.data;

    /*
    [{
        "post_id": row[0],
        "userid": row[1],
        "dateposted": row[2].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row[2], datetime) else row[2],
        "content": row[3],
        "liked": row[6],
        "retweeted": row[7]
    }]
    */

    //
    // Getting the counts for each 
    //
    const allPostIds = tweets.map(post => post.post_id);
    const countsUrl = baseurl + 'tweets/counts';
    const countsResponse = await axios.post(countsUrl, { postids: allPostIds }, {
      headers: { 'Content-Type': 'application/json' }
    });

    const { likes, retweets, comment_counts} = countsResponse.data;

    /*
      "likes": [
          {
            "originalpost": "123",
            "like_count": 3
          },
          {
            "originalpost": "456",
            "like_count": 1
          }
        ],
        "retweets": [
          {
            "originalpost": "123",
            "retweet_count": 2
          }
        ],
        "comment_counts": [
          {
            "reply_to_postid": "123",
            "comment_count": 1
          },
          {
            "reply_to_postid": "456",
            "comment_count": 2
          }
        ],
    */

    const enrichedTweets = tweets.map(tweet => {
      const postId = tweet.post_id;

      // Find matching like count or default to 0
      const likeEntry = likes.find(entry => entry.originalpost === postId);
      const likeCount = likeEntry ? likeEntry.like_count : 0;

      // Find matching retweet count or default to 0
      const retweetEntry = retweets.find(entry => entry.originalpost === postId);
      const retweetCount = retweetEntry ? retweetEntry.retweet_count : 0;

      // Find matching comment count or default to 0
      const commentEntry = comment_counts.find(entry => entry.reply_to_postid === postId);
      const commentCount = commentEntry ? commentEntry.comment_count : 0;

      return {
        postid: postId,
        poster: tweet.username || tweet.userid,
        text: tweet.content || tweet.text,
        image: tweet.image_url || null,
        likes: likeCount,
        retweets: retweetCount,
        replies: commentCount,
        liked: Boolean(Number(tweet.liked)),
        retweeted: Boolean(Number(tweet.retweeted)),
      };
    });

    // console.log(enrichedTweets)

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
function InfiniteScrollPosts({ rootPost, setRootPost, reload, setReload }) {
  const { logged_in_userid, updateUser } = useUser();
  const containerRef = useRef(null);
  const CHUNK_SIZE = 10;
  const [originalPosts, setOriginalPosts] = useState([]);
  const [allPosts, setAllPosts] = useState([]);
  const [visiblePosts, setVisiblePosts] = useState([]);
  const [isFetching, setIsFetching] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setIsFetching(true);

      const tweets = await getRecentTweets({ postid: rootPost ? rootPost.postid : undefined });

      setAllPosts(tweets);
      setVisiblePosts(tweets.slice(0, CHUNK_SIZE));
      setIsFetching(false);
    };

    // Trigger fetch only if `reload` is true OR rootPost has changed
    if (reload || rootPost !== undefined) {
      fetchData();
      setReload(false); // Reset reload state
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
    if (Boolean(post.liked)) {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = 'tweets/unlike';
      const url = baseurl + endpoint;

      const unlikeResponse = await axios.post(url, { userid: 'Alice406@example.com', postid: post.postid }, {
        headers: { 'Content-Type': 'application/json' }
      });

      console.log(unlikeResponse)
    } else {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = 'tweets/like';
      const url = baseurl + endpoint;

      const likeResponse = await axios.post(url, { userid: 'Alice406@example.com', postid: post.postid }, {
        headers: { 'Content-Type': 'application/json' }
      });

      console.log(likeResponse)
    }
  };

  const toggleRetweet = (post) => {
    console.log("USER CLICKED THE RETWEET BUTTON")
    console.log("CHECK IF RETWEET OR UNRETWEET")
  };

  const handleReplyClick = (post) => {
    setRootPost(post);
  };

  if (isFetching) {
    return (
      <CircularProgress sx={{ color: '#4CAF50' }}  />
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
      const updatedTweets = await getRecentTweets({ postid: undefined });
      setReload(true);
      setIsFetching(true);
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
          {/* {post.isRetweet && (
            <Typography variant="caption" sx={{ color: 'gray', mb: 1 }}>
              <RepeatIcon sx={{ fontSize: 16, verticalAlign: 'middle' }} /> Retweeted
            </Typography>
          )} */}

          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Avatar onClick={() => navigate(`/profile/:${post.poster}`)} sx={{ width: 32, height: 32, mr: 1, '&:hover': {bgcolor: '#4CAF50', cursor: 'pointer'}}}>
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
              <IconButton size="small" onClick={() => toggleRetweet(post)}>
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
        
        {String(post.poster) === String('Alice406@example.com') && (
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