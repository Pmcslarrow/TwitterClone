import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Homepage from './Homepage';

// Mock all child components to isolate the Homepage logic
vi.mock('../components/LeftDrawer', () => ({ default: (props) => <div data-testid="left-drawer" /> }));
vi.mock('../components/RightDrawer', () => ({ default: (props) => <div data-testid="right-drawer" /> }));
vi.mock('../components/Prompt', () => ({ default: (props) => <div data-testid="prompt" /> }));
vi.mock('../components/RootPost', () => ({ default: ({ post }) => <div data-testid="root-post">Root Post: {post.id}</div> }));
// For the test, we need to be able to simulate selecting a post.
vi.mock('../components/InfiniteScrollPosts', () => ({ 
    default: ({ setRootPost }) => (
        <div data-testid="infinite-scroll-posts" onClick={() => setRootPost({ id: 'test-post' })}>
            Infinite Scroll Posts
        </div>
    )
}));

describe('Homepage', () => {
  it('renders the main layout with Prompt and InfiniteScrollPosts', () => {
    // ARRANGE
    render(<BrowserRouter><Homepage /></BrowserRouter>);

    // ASSERT
    expect(screen.getByTestId('prompt')).toBeInTheDocument();
    expect(screen.getByTestId('infinite-scroll-posts')).toBeInTheDocument();
    // The RootPost should not be visible on initial render
    expect(screen.queryByTestId('root-post')).not.toBeInTheDocument();
  });

  it('shows the RootPost component when a post is selected', () => {
    // ARRANGE
    render(<BrowserRouter><Homepage /></BrowserRouter>);

    // ACT: Simulate a child component setting the root post
    const infiniteScroll = screen.getByTestId('infinite-scroll-posts');
    fireEvent.click(infiniteScroll);

    // ASSERT: The RootPost component should now be visible
    const rootPost = screen.getByTestId('root-post');
    expect(rootPost).toBeInTheDocument();
    expect(rootPost).toHaveTextContent('Root Post: test-post');
  });
});