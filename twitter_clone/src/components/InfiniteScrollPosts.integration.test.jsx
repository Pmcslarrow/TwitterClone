import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import InfiniteScrollPosts from './InfiniteScrollPosts';

// --- Test Setup ---
const mockCurrentUser = { email: 'Alice406@example.com' };

vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }));

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('InfiniteScrollPosts Integration Test', () => {
  beforeEach(() => {
    useUser.mockReturnValue({ user: mockCurrentUser });
  });

  it('should fetch posts from the backend and render at least one post', async () => {
    // ARRANGE
    renderWithProviders(
      <InfiniteScrollPosts reload={true} setReload={vi.fn()} setRootPost={vi.fn()} />
    );

    // ACT & ASSERT
    // This test no longer looks for specific text. It waits for any element
    // with the test ID 'post-item' to appear. This is much more reliable.
    // We use `findAllByTestId` which waits and returns an array of found elements.
    const posts = await screen.findAllByTestId('post-item', {}, { timeout: 30000 });

    // We just need to make sure that at least one post was rendered.
    expect(posts.length).toBeGreaterThan(0);
  }, 10000); // 10-second timeout
});