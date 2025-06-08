import React, { useEffect, useState } from 'react';
import { Box, Typography, Avatar, Button, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useParams } from 'react-router-dom';
import EditProfile from '../pages/EditProfile';
import axios from 'axios';

export default function ProfileHeader({ isUserFollowed, setIsUserFollowed, isUserBlocked, setIsUserBlocked }) {
    const navigate = useNavigate();
    const { user } = useUser(); // The user who is logged in
    const { profileUsername } = useParams(); // Profile whose page we are visiting
    const [editing, setEditing] = useState(false)
    const [bio, setBio] = useState('Bio Placeholder')
    const [picture, setPicture] = useState('Picture Placeholder')
    const [isLoading, setIsLoading] = useState(false)
    const [refresh, setRefresh] = useState(false) // To force re-fetching after an action
    const canEdit = (user?.username === profileUsername)
    const baseurl = import.meta.env.VITE_API_BASE_URL;

    useEffect(() => {
        const fetchUser = async () => {
            if (!canEdit) {
                const endpoint = 'users/get-user';
                const url = baseurl + endpoint;
                setIsLoading(true);

                try {
                    const response = await axios.post(
                        url,
                        { current_userid: user?.email, username: profileUsername },
                        { headers: { 'Content-Type': 'application/json' } }
                    );

                    const data = response.data;

                    if (data) {
                        setBio(data.bio);
                        setPicture(data.picture);
                        setIsUserFollowed(data.is_following);
                        setIsUserBlocked(data.is_blocked);
                    } else {
                        throw Error("User does not exist");
                    }
                } catch (error) {
                    setBio("");
                    setPicture(null);
                    setIsUserFollowed(null);
                    setIsUserBlocked(null);
                } finally {
                    setIsLoading(false);
                }
            }
        };

        fetchUser();
    }, [profileUsername, refresh]);

    // console.log(user)

    const handleFollow = async (follower, followee, action = 'follow') => {
        setIsLoading(true);
        const endpoint = action === 'unfollow' ? 'users/unfollow' : 'users/follow';
        const url = baseurl + endpoint;

        try {
            const response = await axios.post(
                url,
                { follower, followee_username: followee },
                { headers: { 'Content-Type': 'application/json' } }
            );
            // console.log(`${action} response:`, response.data);
            setRefresh(prev => !prev); // Trigger refetch
        } catch (error) {
            console.error(`Error during ${action}:`, error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleBlock = async (blocker, blockee, action = 'block') => {
        setIsLoading(true);
        const endpoint = action === 'unblock' ? 'users/unblock' : 'users/block';
        const url = baseurl + endpoint;

        try {
            const response = await axios.post(
                url,
                { blocker, blockee_username: blockee },
                { headers: { 'Content-Type': 'application/json' } }
            );
            // console.log(`${action} response:`, response.data);
            setRefresh(prev => !prev); // Trigger refetch
        } catch (error) {
            console.error(`Error during ${action}:`, error);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
                <CircularProgress sx={{ color: '#4CAF50' }}/>
            </Box>
        );
    }

    if (editing) {
        return <EditProfile setEditing={setEditing} />
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
                src={canEdit ? user?.picture : picture}
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

            {canEdit ? (
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
                    }}
                >
                    Edit
                </Button>
            ) : (
                (isUserFollowed !== null && isUserBlocked !== null) && (
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            onClick={async () =>
                                await handleFollow(user?.email, profileUsername, isUserFollowed ? "unfollow" : "follow")
                            }
                            sx={{
                                color: 'white',
                                width: 'max-content',
                                bgcolor: "#4CAF50",
                                '&:hover': {
                                    bgcolor: '#07670B',
                                    cursor: 'pointer',
                                }
                            }}
                        >
                            {isUserFollowed ? 'Unfollow' : 'Follow'}
                        </Button>
                        <Button
                            onClick={async () =>
                                await handleBlock(user?.email, profileUsername, isUserBlocked ? "unblock" : "block")
                            }
                            sx={{
                                color: 'white',
                                width: 'max-content',
                                bgcolor: "#f44336",
                                '&:hover': {
                                    bgcolor: '#c62828',
                                    cursor: 'pointer',
                                }
                            }}
                        >
                            {isUserBlocked ? 'Unblock' : 'Block'}
                        </Button>
                    </Box>
                )
            )}

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
