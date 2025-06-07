import React, { useState, useEffect } from 'react';
import { Box, Button, Drawer, Typography, TextField, List, ListItem, Avatar, ListItemText, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const getUsers = async (currentUserId) => {
  const baseurl = import.meta.env.VITE_API_BASE_URL;
  const endpoint = 'users/';
  const url = baseurl + endpoint;

  try {
    const response = await axios.post(
      url,
      { userid: currentUserId },
      { headers: { 'Content-Type': 'application/json' } }
    );
    
    // Transform the response data to match expected format
    const users = response.data.map(user => ({
      userid: user[0], // First element from tuple
      username: user[1], // Second element from tuple
      bio: '', // Not provided by API
      picture: `https://i.pravatar.cc/150?u=${user[0]}` // Generate avatar based on userid
    }));
    
    return users;
  } catch (error) {
    console.error('API Error:', error);
    return [];
  }
};

export default function RightDrawer({ props }) {
  const { rightOpen, setRightOpen } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Fetch users when drawer opens
  useEffect(() => {
    const fetchUsers = async () => {
      if (rightOpen) {
        setIsLoading(true);
        const fetchedUsers = await getUsers('Alice406@example.com'); // Replace with actual current user ID
        setUsers(fetchedUsers);
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, [rightOpen]);

  const filteredUsers = users
    .filter(user =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .slice(0, 50);

  return (
    <Drawer
      anchor="right"
      open={rightOpen}
      onClose={() => setRightOpen(false)}
      PaperProps={{
        sx: { bgcolor: 'white', width: 300 },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Search Users
        </Typography>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by username"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 2 }}
        />
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress sx={{ color: '#4CAF50' }} />
          </Box>
        ) : (
          <List>
            {filteredUsers.map((user) => (
              <ListItem 
                key={user.userid} 
                onClick={() => navigate(`/profile/${user.username}`)} 
                sx={{ alignItems: 'flex-start', '&:hover': {bgcolor: '#4CAF50', cursor: 'pointer'}}}
              >
                <Avatar src={user.picture} alt={user.username} sx={{ mr: 2 }} />
                <ListItemText
                  primary={user.username}
                  secondary={user.bio || 'No bio available'}
                />
              </ListItem>
            ))}
          </List>
        )}
        
        <Button 
          variant="contained" 
          onClick={() => setRightOpen(false)} 
          sx={{ mt: 2, bgcolor: "#4CAF50", '&:hover': {bgcolor: '#07670B', cursor: 'pointer'}}}
        >
          Close
        </Button>
      </Box>
    </Drawer>
  );
}