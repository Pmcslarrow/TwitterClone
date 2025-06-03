import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Profile from './Profile';

// Mock the components
vi.mock('../components/LeftDrawer', () => ({
  default: ({ props }) => (
    <div data-testid="left-drawer" style={{ display: props.leftOpen ? 'block' : 'none' }}>
      Left Drawer
    </div>
  )
}));

vi.mock('../components/RightDrawer', () => ({
  default: ({ props }) => (
    <div data-testid="right-drawer" style={{ display: props.rightOpen ? 'block' : 'none' }}>
      Right Drawer
    </div>
  )
}));

vi.mock('../components/Prompt', () => ({
  default: ({ rootPost }) => (
    <div data-testid="prompt">Prompt Component {rootPost?.id}</div>
  )
}));

vi.mock('../components/RootPost', () => ({
  default: ({ post, setRootPost }) => (
    <div data-testid="root-post">
      Root Post: {post?.id}
      <button onClick={() => setRootPost(null)}>Close</button>
    </div>
  )
}));

vi.mock('../components/InfiniteScrollPosts', () => ({
  default: ({ rootPost, setRootPost }) => (
    <div data-testid="infinite-scroll-posts">
      Infinite Scroll Posts
      <button onClick={() => setRootPost({ id: 'test-post' })}>Set Root Post</button>
    </div>
  )
}));

vi.mock('../components/ProfileHeader', () => ({
  default: ({ profileUserId, bio, picture }) => (
    <div data-testid="profile-header">
      Profile Header - User: {profileUserId}, Bio: {bio}
    </div>
  )
}));

// Mock react-router-dom useParams
const mockUseParams = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => mockUseParams()
  };
});

const ProfileWrapper = ({ profileuserid = 'test-user' }) => {
  mockUseParams.mockReturnValue({ profileuserid });
  return (
    <BrowserRouter>
      <Profile />
    </BrowserRouter>
  );
};

describe('Profile', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the profile page with basic elements', () => {
    render(<ProfileWrapper />);
    
    expect(screen.getByTestId('profile-header')).toBeInTheDocument();
    expect(screen.getByTestId('infinite-scroll-posts')).toBeInTheDocument();
  });

  it('displays profile header with correct props', () => {
    render(<ProfileWrapper profileuserid="john123" />);
    
    expect(screen.getByTestId('profile-header')).toHaveTextContent('User: john123');
    expect(screen.getByTestId('profile-header')).toHaveTextContent('Bio: Web3 enthusiast');
  });

  it('shows profile header when no root post is selected', () => {
    render(<ProfileWrapper />);
    
    expect(screen.getByTestId('profile-header')).toBeInTheDocument();
    expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
    expect(screen.queryByTestId('prompt')).not.toBeInTheDocument();
  });

  it('shows root post and prompt when root post is selected', async () => {
    render(<ProfileWrapper />);
    
    const setRootPostButton = screen.getByRole('button', { name: /set root post/i });
    fireEvent.click(setRootPostButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('root-post')).toBeInTheDocument();
      expect(screen.getByTestId('prompt')).toBeInTheDocument();
      expect(screen.queryByTestId('profile-header')).not.toBeInTheDocument();
    });
  });

  it('can close root post view and return to profile view', async () => {
    render(<ProfileWrapper />);
    
    // Set root post
    const setRootPostButton = screen.getByRole('button', { name: /set root post/i });
    fireEvent.click(setRootPostButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('root-post')).toBeInTheDocument();
    });
    
    // Close root post
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    await waitFor(() => {
      expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
      expect(screen.getByTestId('profile-header')).toBeInTheDocument();
    });
  });

  it('passes correct props to components', () => {
    render(<ProfileWrapper profileuserid="user123" />);
    
    expect(screen.getByTestId('profile-header')).toHaveTextContent('User: user123');
    expect(screen.getByTestId('infinite-scroll-posts')).toBeInTheDocument();
  });

  it('handles different profile user IDs from URL params', () => {
    mockUseParams.mockReturnValue({ profileuserid: 'different-user' });
    
    render(
      <BrowserRouter>
        <Profile />
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('profile-header')).toHaveTextContent('User: different-user');
  });
});