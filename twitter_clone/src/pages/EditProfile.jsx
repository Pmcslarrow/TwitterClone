import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import {
  Box,
  TextField,
  Button,
  Typography,
  Avatar,
  Stack,
  Paper,
  IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios'
import { useNavigate } from 'react-router-dom';

export default function EditProfile({ setEditing }) {
  const { user, setUser } = useUser(); // assume updateUser is provided
  const navigate = useNavigate()
  const [username, setUsername] = useState(user?.username || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [picture, setPicture] = useState(user?.picture || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      const baseurl = import.meta.env.VITE_API_BASE_URL;
      const endpoint = 'users/update-profile';
      const url = baseurl + endpoint;

      console.log(user.email, bio, username, picture)

      const response = await axios.post(
        url,
        {
          userid: user?.email,
          bio: bio,
          username: username,
          picture: picture
        },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );

      //
      // On Success I want to update the state of the user so that it reflects
      // the changes everywhere without having to hit the DB
      //
      if (String(response.status) === "200") {
          const updatedUser = {
            ...user,
            username: username,
            bio: bio,
            picture: picture, 
          };
          setUser(updatedUser);
          navigate(`/profile/${username}`)
      }
    
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setSaving(false);
      setEditing(false);
    }
  };

  return (
    <Box sx={{ width: '100%', mx: 'auto', mt: 4, p: 3 }}>
      <Paper sx={{ p: 3, position: 'relative' }}>
        {/* Close Button */}
        <IconButton
          onClick={() => setEditing(false)}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            color: '#4CAF50',

            '&:hover': {
                bgcolor: '#07670B',
                cursor: 'pointer',
            },
          }}
        >
          <CloseIcon />
        </IconButton>

        <Typography variant="h5" sx={{ mb: 2, color: 'black' }}>
          Edit Profile
        </Typography>

        <Stack spacing={2}>
          <TextField
            label="Username"
            variant="outlined"
            fullWidth
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <TextField
            label="Bio"
            variant="outlined"
            multiline
            rows={4}
            fullWidth
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />

          <TextField
            label="Profile Picture URL"
            variant="outlined"
            fullWidth
            value={picture}
            onChange={(e) => setPicture(e.target.value)}
          />

          <Box sx={{ textAlign: 'center' }}>
            <Avatar
              src={picture}
              alt={username}
              sx={{ width: 80, height: 80, mx: 'auto', mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              Preview
            </Typography>
          </Box>

          {error && (
            <Typography color="error" sx={{ mt: 1 }}>
              {error}
            </Typography>
          )}

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving || !username.trim()}
            sx={{
              mx: 2,
              color: 'white',
              bgcolor: "#4CAF50",
              '&:hover': {
                bgcolor: '#07670B',
                cursor: 'pointer',
              }
            }}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
