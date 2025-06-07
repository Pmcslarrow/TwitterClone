import React, { useState } from 'react';
import { Box, Container, Paper, Typography, Avatar, Divider, Link, CircularProgress } from '@mui/material';
import { GoogleLogin } from '@react-oauth/google';
import { useUser } from '../context/UserContext';
import { jwtDecode } from "jwt-decode";
import { useNavigate } from 'react-router-dom';
import LoginIcon from '@mui/icons-material/Login';
import axios from 'axios';

const LoginPage = () => {
    const { setUser } = useUser();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);

    return (
        <Box
            sx={{
                minHeight: '100vh',
                background: 'linear-gradient(to bottom, #ffffff, #f9fafb)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                overflow: 'hidden',
            }}
        >
            {/* Decorative blur circles */}
            <Box
                sx={{
                    position: 'absolute',
                    top: -100,
                    left: -100,
                    width: 256,
                    height: 256,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(7, 103, 11, 0.05)',
                    filter: 'blur(100px)',
                    zIndex: 0,
                }}
            />
            <Box
                sx={{
                    position: 'absolute',
                    bottom: -100,
                    right: -100,
                    width: 256,
                    height: 256,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(7, 103, 11, 0.05)',
                    filter: 'blur(100px)',
                    zIndex: 0,
                }}
            />

            {/* Card Container */}
            <Paper
                elevation={6}
                sx={{
                    position: 'relative',
                    zIndex: 1,
                    width: 350,
                    padding: 4,
                    borderRadius: 3,
                    border: '1px solid #e0e0e0',
                }}
            >
                {/* Logo/Icon */}
                <Box display="flex" justifyContent="center" mb={3}>
                    <Avatar
                        sx={{
                            bgcolor: 'rgba(7, 103, 11, 0.1)',
                            width: 64,
                            height: 64,
                        }}
                    >
                        <LoginIcon sx={{ color: '#07670B', fontSize: 32 }} />
                    </Avatar>
                </Box>

                {/* Title & Subtitle */}
                <Typography variant="h5" align="center" fontWeight="bold" gutterBottom>
                    Welcome
                </Typography>
                <Typography variant="body2" align="center" color="text.secondary" mb={3}>
                    Sign in to continue to your account
                </Typography>

                {/* Google Login Button or Loading */}
                <Box display="flex" justifyContent="center">
                    {isLoading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                            <CircularProgress sx={{ color: '#07670B' }} />
                        </Box>
                    ) : (
                        <GoogleLogin
                            onSuccess={async (credentialResponse) => {
                                setIsLoading(true);
                                try {
                                    let decoded = jwtDecode(credentialResponse.credential);
                                    let name = decoded.name.replace(/\s+/g, '').toLowerCase();
                                    const uniquePart = Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36);
                                    decoded.username = name + uniquePart;
                                    
                                    const baseurl = import.meta.env.VITE_API_BASE_URL;
                                    const endpoint = 'users/create/';
                                    const url = baseurl + endpoint;

                                    const response = await axios.post(
                                        url,
                                        { 
                                            userid: decoded.email,
                                            username: name + uniquePart,
                                            picture: decoded.picture
                                        },
                                        { headers: { 'Content-Type': 'application/json' } }
                                    );
                                    
                                    const { username, picture, bio } = response.data;

                                    if (username === "") {
                                        // NEW USER
                                        decoded.bio = bio;
                                    } else {
                                        // ALREADY EXISTS
                                        decoded.username = username;
                                        decoded.picture = picture;
                                        decoded.bio = bio;
                                    }

                                    setUser(decoded);
                                    navigate('/home');
                                } catch (error) {
                                    console.error('Login error:', error);
                                    setIsLoading(false);
                                }
                            }}
                            onError={() => {
                                console.log('Login Failed');
                                setIsLoading(false);
                            }}
                            theme="outline"
                            size="large"
                            width="100%"
                        />
                    )}
                </Box>

                {/* Bottom accent line */}
                <Divider
                    sx={{
                        mt: 4,
                        height: 4,
                        border: 'none',
                        background: 'linear-gradient(to right, #07670B, rgba(7,103,11,0.6))',
                        borderRadius: 2,
                    }}
                />
            </Paper>
        </Box>
    );
};

export default LoginPage;