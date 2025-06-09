import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, useParams } from 'react-router-dom';
import Profile from './Profile';

// Mock child components
vi.mock('../components/ProfileHeader', () => ({ default: () => <div data-testid="profile-header" /> }));
vi.mock('../components/RootPost', () => ({ default: () => <div data-testid="root-post" /> }));
vi.mock('../components/Prompt', () => ({ default: () => <div data-testid="prompt" /> }));
vi.mock('../components/InfiniteScrollPosts', () => ({ 
    default: ({ setRootPost }) => (
        <div data-testid="infinite-scroll-posts" onClick={() => setRootPost({ id: 'test-post' })}>
            Infinite Scroll Posts
        </div>
    )
}));
vi.mock('../components/LeftDrawer', () => ({ default: () => <div data-testid="left-drawer" /> }));
vi.mock('../components/RightDrawer', () => ({ default: () => <div data-testid="right-drawer" /> }));

// Mock react-router-dom's useParams hook
vi.mock('react-router-dom', async (importActual) => {
    const actual = await importActual();
    return {
        ...actual,
        useParams: vi.fn(),
    };
});

describe('Profile Page', () => {
  it('initially renders the ProfileHeader and InfiniteScrollPosts', () => {
    // ARRANGE
    useParams.mockReturnValue({ profileUsername: 'testuser' });
    render(<BrowserRouter><Profile /></BrowserRouter>);

    // ASSERT
    expect(screen.getByTestId('profile-header')).toBeInTheDocument();
    expect(screen.getByTestId('infinite-scroll-posts')).toBeInTheDocument();
    // RootPost and Prompt should not be visible initially
    expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
    expect(screen.queryByTestId('prompt')).not.toBeInTheDocument();
  });

  it('switches to the RootPost and Prompt view when a post is selected', async () => {
    // ARRANGE
    useParams.mockReturnValue({ profileUsername: 'testuser' });
    render(<BrowserRouter><Profile /></BrowserRouter>);

    // ACT
    const infiniteScroll = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScroll);

    // ASSERT
    await waitFor(() => {
        // The header should disappear
        expect(screen.queryByTestId('profile-header')).not.toBeInTheDocument();
        // RootPost and Prompt should now be visible
        expect(screen.getByTestId('root-post')).toBeInTheDocument();
        expect(screen.getByTestId('prompt')).toBeInTheDocument();
    });
  });
});