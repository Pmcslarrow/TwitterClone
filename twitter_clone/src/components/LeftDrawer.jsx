import React, { useContext, useState } from 'react';
import { Box, Button, Drawer, Typography, Avatar } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function LeftDrawer({props}) {
    let {leftOpen, setLeftOpen, setRootPost} = props
    const navigate = useNavigate();
    const { user, setUser } = useUser();
  
    return (
      <Drawer
      anchor="left"
      open={leftOpen}
      onClose={() => setLeftOpen(false)}
      PaperProps={{
        sx: { bgcolor: 'white', width: 250},
      }}
    >
      <Box sx={{ 
          p: 2, 
          height: "30%",
          display: "flex", 
          flexDirection: 'column',
          alignItems: 'left',
          justifyContent: 'space-around',

        }}>

      {/* Avatar button */}
         <Avatar
            src={"https://example.com/profile.jpg"}
            alt={user?.username}
            sx={{
                width: 50,
                height: 50,
                border: '3px solid #4CAF50',
                bgcolor: "#4CAF50",
                '&:hover': {
                  bgcolor: '#07670B',
                  cursor: 'pointer'
            }, 
            }}
            onClick={() => navigate(`/profile/${user?.userid}`)}
          />

      
      {/* Back home button */}
        <Button
          onClick={() => navigate("/home")}
          sx={{
            color: 'white',
            width: 'max-content',
            bgcolor: "#4CAF50",
            '&:hover': {
              bgcolor: '#07670B',
              cursor: 'pointer',
            }
          }}
          >Home
        </Button>

      {/* Close left drawer */}
        <Button
          onClick={() => setLeftOpen(false)}
          sx={{
            color: 'white',
            width: 'max-content',
            bgcolor: "#4CAF50",
            '&:hover': {
              bgcolor: '#07670B',
              cursor: 'pointer',
            }
          }}
          >Close</Button>

      {/* Logout button */}
        <Button
          onClick={() => {
            setUser(null);
            navigate("/");
          }}
          sx={{
            color: 'white',
            width: 'max-content',
            bgcolor: "#4CAF50",
            '&:hover': {
              bgcolor: '#07670B',
              cursor: 'pointer',
            }
          }}
          >Logout</Button>
      
      </Box>
    </Drawer>
    )
}