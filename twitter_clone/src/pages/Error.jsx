import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function ErrorPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        height: '100vh',
        width: '100vw',
        bgcolor: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        textAlign: 'center',
        p: 3,
      }}
    >
      <Typography variant="h1" sx={{ fontSize: '8rem', fontWeight: 'bold', color: '#4CAF50' }}>
        404
      </Typography>
      <Typography variant="h5" sx={{ mb: 2, color: '#333' }}>
        Page Not Found
      </Typography>
      <Typography variant="body1" sx={{ mb: 4, color: 'gray' }}>
        Oops! The page you’re looking for doesn’t exist.
      </Typography>
      <Button
        variant="contained"
        sx={{
          bgcolor: '#4CAF50',
          '&:hover': { bgcolor: '#388E3C' },
          borderRadius: 2,
          px: 4,
          py: 1,
          fontWeight: 'bold',
        }}
        onClick={() => navigate('/home')}
      >
        Go Back Home
      </Button>
    </Box>
  );
}