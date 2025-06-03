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

export default function EditProfile({ setEditing }) {
  const { user, updateUser } = useUser(); // assume updateUser is provided
  const [userid, setUserid] = useState(user?.userid || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [picture, setPicture] = useState(user?.picture || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      // Example: Replace this with your real API call
      await updateUser({ userid, bio, picture });
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setSaving(false);
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
            label="Username (UserID)"
            variant="outlined"
            fullWidth
            value={userid}
            onChange={(e) => setUserid(e.target.value)}
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
              alt={userid}
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
            disabled={saving || !userid.trim()}
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
