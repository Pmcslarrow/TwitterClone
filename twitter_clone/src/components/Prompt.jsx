import React, { useState } from 'react';
import { TextField, Button, Box, Typography, CircularProgress } from '@mui/material';
import axios from 'axios';

const Prompt = ({ rootPost, setRootPost, reload, setReload }) => {
  const [prompt, setPrompt] = useState('');
  const maxChars = 500;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (prompt.trim()) {
      try {
        if (rootPost) {
          // REPLY
        } else {
          // POST
          const baseurl = import.meta.env.VITE_API_BASE_URL;
          const endpoint = 'tweets/create';
          const url = baseurl + endpoint;
          console.log(prompt)
          const response = await axios.post(url, { userid: 'Alice406@example.com', textcontent: prompt }, {
            headers: { 'Content-Type': 'application/json' }
          });
          console.log(response);
        }
        setPrompt('');

      } catch (error) {
        console.error('Error posting:', error);
      } finally {
        setReload(true)
      }
    }
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit} 
      sx={{ 
        mx: 'auto', 
        width: '100%', 
        maxWidth: '600px',
        p: 2,
        scrollbarWidth: 'none', // Firefox
        '&::-webkit-scrollbar': {
          display: 'none',       // Chrome, Safari, Edge
        },
      }}
    >
      <TextField
        fullWidth
        multiline
        minRows={3}
        maxRows={6}
        variant="outlined"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder={rootPost ? `Reply to ${rootPost?.poster}...` : "What's happening?"}
        InputLabelProps={{
          shrink: true,
        }}
        sx={{
          mb: 2,
          '& .MuiInputLabel-shrink': {
            transform: 'translate(14px, 10px) scale(0.75)',
          },
          '& .MuiOutlinedInput-root': {
            '&.Mui-focused fieldset': {
              borderColor: '#4CAF50', // Change this to your desired color
              borderWidth: '2px',     // Optional: make the border thicker
            }
          }
        }}
        inputProps={{
          maxLength: maxChars,
        }}
      />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography 
          variant="caption" 
          color={prompt.length >= maxChars * 0.9 ? "error" : "text.secondary"}
          sx={{ fontWeight: prompt.length >= maxChars * 0.9 ? 'bold' : 'normal' }}
        >
          {prompt.length}/{maxChars}
        </Typography>
        <Button 
          type="submit" 
          variant="contained" 
          disabled={!prompt.trim() || reload} 
          sx={{ 
            borderRadius: '20px',
            px: 3,
            bgcolor: '#4CAF50',
            '&:hover': {
              bgcolor: '#07670B',
            },
          }}
        >
          {reload ? <CircularProgress size={20} color="inherit" /> : (rootPost ? "Reply" : "Post")}
        </Button>
      </Box>
    </Box>
  );
};

export default Prompt;
