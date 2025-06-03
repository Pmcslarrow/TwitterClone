import React, { useState } from 'react';
import { Box, Typography, Avatar, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import EditProfile from '../pages/EditProfile';

export default function ProfileHeader({ profileUserId, bio, picture }) {
    const navigate = useNavigate();
    const [editing, setEditing] = useState(false);
    const { user } = useUser(); // The user who is logged in
    const canEdit = (profileUserId === user?.userid);

    if (editing) {
        return <EditProfile setEditing={setEditing}/>
    }

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                width: '100%',
                px: 2,
            }}
        >
            <Avatar
                src={picture}
                alt={profileUserId}
                sx={{
                    width: 100,
                    height: 100,
                    border: '3px solid #4CAF50',
                }}
                onClick={() => navigate("/home")}
            />
            <Typography variant="h6" sx={{ color: 'black', fontWeight: 'bold' }}>
                {profileUserId}
            </Typography>
        
        {/* Edit button logic */}
            {canEdit ? 
                <Button   
                    onClick={() => setEditing(!editing)}         
                    sx={{
                        color: 'white',
                        width: 'max-content',
                        bgcolor: "#4CAF50",
                        '&:hover': {
                        bgcolor: '#07670B',
                        cursor: 'pointer',
                        }
                    }}>Edit</Button> 
                : null
            }

            <Typography
                variant="body1"
                sx={{
                    color: 'gray',
                    fontStyle: 'italic',
                    textAlign: 'center',
                    maxWidth: 400,
                }}
            >
                {bio || 'No bio yet.'}
            </Typography>
        </Box>
    );
}