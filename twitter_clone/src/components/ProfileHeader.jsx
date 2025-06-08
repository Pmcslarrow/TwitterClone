import React, { useEffect, useState } from 'react';
import { Box, Typography, Avatar, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useParams } from 'react-router-dom';
import EditProfile from '../pages/EditProfile';
import axios from 'axios';

export default function ProfileHeader({ reload, setReload }) {
    const navigate = useNavigate();
    const { user } = useUser(); // The user who is logged in
    const { profileUsername } = useParams(); // Profile who's page we are visiting
    const [editing, setEditing] = useState(false)
    const [bio, setBio] = useState('Bio Placeholder')
    const [picture, setPicture] = useState('Picture Placeholder')
    const canEdit = (user?.username === profileUsername )

    useEffect(() => {
        const fetchUser = async () => {
            if (!canEdit) {
                //
                // This means we are on the profile page of someone other than our own user
                // So, we need to actually pull this user's information 
                //
                const baseurl = import.meta.env.VITE_API_BASE_URL;
                const endpoint = 'users/get-user';
                const url = baseurl + endpoint;

                console.log(url)
                console.log(profileUsername)
                
                try {
                    const response = await axios.post(
                        url, 
                        { username: profileUsername }, 
                        { headers: { 'Content-Type': 'application/json' }}
                    );
                    console.log(response)
                    
                    if (response.data.length > 0) {
                        const [bio, picture] = response.data[0];
                        setBio(bio)
                        setPicture(picture)
                    } else {
                        throw Error("nexist")
                    }

                } catch (error) {
                    setBio("");
                    setPicture(null);
                }
            }
        }
        
        fetchUser()
    }, [profileUsername])

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
                alt={profileUsername}
                sx={{
                    width: 100,
                    height: 100,
                    border: '3px solid #4CAF50',
                }}
                onClick={() => navigate("/home")}
            />
            <Typography variant="h6" sx={{ color: 'black', fontWeight: 'bold' }}>
                {canEdit ? user?.username : profileUsername}
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
                {canEdit ? user?.bio : bio} 
            </Typography>
        </Box>
    );
}