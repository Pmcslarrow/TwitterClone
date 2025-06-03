import React, { useState } from 'react';
import { Box, Button, Drawer, Typography, TextField, List, ListItem, Avatar, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const mockUsers = [
  {
    userid: 'john123',
    username: 'john_doe',
    bio: 'Loves coding and coffee.',
    picture: 'https://i.pravatar.cc/150?img=1'
  },
  {
    userid: 'jane456',
    username: 'jane_smith',
    bio: 'Frontend developer and cat lover.',
    picture: 'https://i.pravatar.cc/150?img=2'
  },
  {
    userid: 'sam789',
    username: 'sam_wilson',
    bio: 'Enjoys hiking and backend development.',
    picture: 'https://i.pravatar.cc/150?img=3'
  }
];

export default function RightDrawer({ props }) {
  const { rightOpen, setRightOpen } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const filteredUsers = mockUsers.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
        <List>
          {filteredUsers.map((user) => (
            <ListItem key={user.userid} onClick={() => navigate(`/profile/${user.userid}`)} sx={{ alignItems: 'flex-start', '&:hover': {bgcolor: '#4CAF50', cursor: 'pointer'}}}>
              <Avatar src={user.picture} alt={user.username} sx={{ mr: 2 }} />
              <ListItemText
                primary={user.username}
                secondary={user.bio}
              />
            </ListItem>
          ))}
        </List>
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
