import React from 'react';
import { Box, Container, Paper, Typography, Avatar, Divider, Link } from '@mui/material';
import { GoogleLogin } from '@react-oauth/google';
import { useUser } from '../context/UserContext';
import { jwtDecode } from "jwt-decode";
import { useNavigate } from 'react-router-dom';
import LoginIcon from '@mui/icons-material/Login';

const LoginPage = () => {
    const { setUser } = useUser();
    const navigate = useNavigate();

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

                {/* Google Login Button */}
                <Box display="flex" justifyContent="center">
                    <GoogleLogin
                        onSuccess={(credentialResponse) => {
                            let decoded = jwtDecode(credentialResponse.credential);
                            let name = decoded.name.replace(/\s+/g, '').toLowerCase();
                            const uniquePart = Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36);
                            const userid = name + uniquePart;
                            decoded.userid = userid;
                            setUser(decoded);
                            navigate('/home');
                            /*
                            NOTE: 

                            Right now we ALWAYS add a new userid... 
                            We need to udpate this to check if the decoded.email
                            exists in the database. If it does, use that userid. 

                            Otherwise it is new and we can store it into the database
                            
                            Pseudo:

                            if (user email exists in database) {
                                decoded[userid] = userid in database
                                
                            } else {
                                decoded[userid] = generate new id;
                            }
                            setUser()
                            navigate()
                            */
                        
                        }}
                        onError={() => {
                            console.log('Login Failed');
                        }}
                        theme="outline"
                        size="large"
                        width="100%"
                    />
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
