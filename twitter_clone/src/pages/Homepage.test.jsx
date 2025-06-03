import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Homepage from './Homepage';

// Mock the child components
vi.mock('../components/LeftDrawer', () => ({
  default: ({ props }) => (
    <div data-testid="left-drawer" data-open={props.leftOpen}>
      Left Drawer
    </div>
  )
}));

vi.mock('../components/RightDrawer', () => ({
  default: ({ props }) => (
    <div data-testid="right-drawer" data-open={props.rightOpen}>
      Right Drawer
    </div>
  )
}));

vi.mock('../components/Prompt', () => ({
  default: ({ rootPost }) => (
    <div data-testid="prompt" data-root-post={rootPost?.id || 'null'}>
      Prompt Component
    </div>
  )
}));

vi.mock('../components/InfiniteScrollPosts', () => ({
  default: ({ rootPost, setRootPost }) => (
    <div 
      data-testid="infinite-scroll-posts" 
      data-root-post={rootPost?.id || 'null'}
      onClick={() => setRootPost({ id: 'test-post', title: 'Test Post' })}
    >
      Infinite Scroll Posts
    </div>
  )
}));

vi.mock('../components/RootPost', () => ({
  default: ({ post, setRootPost }) => (
    <div 
      data-testid="root-post" 
      data-post-id={post.id}
      onClick={() => setRootPost(null)}
    >
      Root Post: {post.title}
    </div>
  )
}));

describe('Homepage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.log = vi.fn();
  });

  it('renders without crashing', () => {
    render(<Homepage />);
    expect(screen.getByTestId('prompt')).toBeInTheDocument();
    expect(screen.getByTestId('infinite-scroll-posts')).toBeInTheDocument();
  });

  it('does not render RootPost component when rootPost is null', () => {
    render(<Homepage />);
    
    expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
  });

  it('renders RootPost component when rootPost is set', () => {
    render(<Homepage />);
    
    // Simulate setting a root post by clicking on infinite scroll posts
    const infiniteScrollPosts = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScrollPosts);
    
    expect(screen.getByTestId('root-post')).toBeInTheDocument();
    expect(screen.getByText('Root Post: Test Post')).toBeInTheDocument();
  });

  it('clears rootPost when clicking on RootPost component', () => {
    render(<Homepage />);
    
    // Set a root post first
    const infiniteScrollPosts = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScrollPosts);
    
    expect(screen.getByTestId('root-post')).toBeInTheDocument();
    
    // Click on root post to clear it
    const rootPost = screen.getByTestId('root-post');
    fireEvent.click(rootPost);
    
    expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
  });

  it('passes rootPost prop to child components', () => {
    render(<Homepage />);
    
    // Initially rootPost is null
    expect(screen.getByTestId('prompt')).toHaveAttribute('data-root-post', 'null');
    expect(screen.getByTestId('infinite-scroll-posts')).toHaveAttribute('data-root-post', 'null');
    
    // Set a root post
    const infiniteScrollPosts = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScrollPosts);
    
    expect(screen.getByTestId('prompt')).toHaveAttribute('data-root-post', 'test-post');
    expect(screen.getByTestId('infinite-scroll-posts')).toHaveAttribute('data-root-post', 'test-post');
  });

  it('logs initial page load message on mount', () => {
    render(<Homepage />);
    
    expect(console.log).toHaveBeenCalledWith('PAGE LOADED! Pulling all posts');
  });

  it('logs comment section message when rootPost changes', () => {
    render(<Homepage />);
    
    // Clear the initial console.log call
    vi.clearAllMocks();
    
    // Set a root post to trigger the effect
    const infiniteScrollPosts = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScrollPosts);
    
    expect(console.log).toHaveBeenCalledWith('New comment section selected! Pulling replies related to post');
  });

  it('has correct styling classes and structure', () => {
    const { container } = render(<Homepage />);
    
    // Check if the main container has the correct MUI Box structure
    const mainBox = container.firstChild;
    expect(mainBox).toHaveStyle({
      height: '100vh',
      width: '100vw',
      position: 'relative'
    });
  });
});