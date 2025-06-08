import React, { useContext, useEffect, useState } from 'react';
import { Box, Button, IconButton, Typography } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ExploreIcon from '@mui/icons-material/Explore';
import LeftDrawer from '../components/LeftDrawer';
import RightDrawer from '../components/RightDrawer';
import Prompt from '../components/Prompt';
import RootPost from '../components/RootPost';
import InfiniteScrollPosts from '../components/InfiniteScrollPosts';
import ProfileHeader from '../components/ProfileHeader'
import { useParams } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function Profile() {
    const [leftOpen, setLeftOpen] = useState(false);
    const [rightOpen, setRightOpen] = useState(false);
    const [rootPost, setRootPost] = useState(null);
    const [reload, setReload] = useState(false);
    const { profileUsername } = useParams(); // Profile who's page we are visiting
    
    return (
        <Box
            sx={{
                height: '100vh',
                width: '100vw',
                bgcolor: 'white',
                position: 'relative',
                color: 'white',
            }}
        >
            {/* Top Left Icon Button */}
            <IconButton
                onClick={() => setLeftOpen(true)}
                sx={{
                    position: 'absolute',
                    top: 16,
                    left: 16,
                    color: '#4CAF50',
                    '&:hover': {
                        color: '#07670B',
                    },                    
                    // bgcolor: 'rgba(255, 255, 255, 0.1)',
                    // '&:hover': {
                    //     bgcolor: 'rgba(255, 255, 255, 0.2)',
                    // },
                }}
            >
                <MenuIcon />
            </IconButton>

            {/* Top Right Icon Button */}
            <IconButton
                onClick={() => setRightOpen(true)}
                sx={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    color: '#4CAF50',
                    '&:hover': {
                        color: '#07670B',
                    },
                    // bgcolor: 'rgba(255, 255, 255, 0.1)',
                    // '&:hover': {
                    //     bgcolor: 'rgba(255, 255, 255, 0.2)',
                    // },
                }}
            >
                <ExploreIcon />
            </IconButton>

            {/* Centered Content */}
            <Box
                sx={{
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-around',
                    flexDirection: 'column',
                    gap: 2,
                    textAlign: 'center',
                }}
            >
            
            { /* If the comment section is selected, we only show the comment(s) and prompt */}
                { rootPost ? 
                    <>
                        <RootPost post={rootPost} setRootPost={setRootPost} />
                        <Prompt rootPost={rootPost}/>

                    </>
                :
                    <>
                        <ProfileHeader 
                            profileUsername={profileUsername} 
                            bio="Web3 enthusiast. Tweets about code, coffee, and cats." 
                            picture="https://example.com/profile.jpg" 
                        />
                    </>
                }

            {/* If comment is selected, rootPost has a value. This means it will only show the rootPost and comments for this post */}
                <InfiniteScrollPosts rootPost={rootPost} setRootPost={setRootPost} reload={reload} setReload={setReload}/>

            </Box>

            {/* Drawers */}
            <LeftDrawer props={{ leftOpen, setLeftOpen, setRootPost }} />
            <RightDrawer props={{ rightOpen, setRightOpen }} />
        </Box>
    );
}
