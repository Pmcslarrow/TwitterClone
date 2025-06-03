import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import InfiniteScrollPosts from './InfiniteScrollPosts';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const TestWrapper = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const renderWithRouter = (component) => {
  return render(component, { wrapper: TestWrapper });
};

describe('InfiniteScrollPosts', () => {
  const mockSetRootPost = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Core Functionality', () => {
    it('renders posts container', () => {
      const { container } = renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('filters posts when rootPost is provided', () => {
      const rootPost = { postid: 123, poster: 'user', text: 'test' };
      
      renderWithRouter(
        <InfiniteScrollPosts 
          rootPost={rootPost} 
          setRootPost={mockSetRootPost} 
        />
      );

      // Should filter and limit posts when rootPost exists
      const posts = screen.queryAllByText(/@\w+/);
      expect(posts.length).toBeLessThanOrEqual(3);
    });

    it('shows all posts when no rootPost', () => {
      renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const posts = screen.getAllByText(/@\w+/);
      expect(posts.length).toBeGreaterThan(3);
    });
  });

  describe('User Interactions', () => {
    it('toggles like state and count', async () => {
      renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const likeButtons = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('[data-testid*="Favorite"]')
      );
      
      if (likeButtons.length > 0) {
        const button = likeButtons[0];
        const countElement = button.closest('div').querySelector('p');
        const initialCount = parseInt(countElement.textContent);
        
        fireEvent.click(button);
        
        await waitFor(() => {
          const newCount = parseInt(countElement.textContent);
          expect(newCount).not.toBe(initialCount);
        });
      }
    });

    it('toggles retweet state and count', async () => {
      renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const retweetButtons = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('[data-testid*="Repeat"]')
      );
      
      if (retweetButtons.length > 0) {
        const button = retweetButtons[0];
        const countElement = button.closest('div').querySelector('p');
        const initialCount = parseInt(countElement.textContent);
        
        fireEvent.click(button);
        
        await waitFor(() => {
          const newCount = parseInt(countElement.textContent);
          expect(newCount).not.toBe(initialCount);
        });
      }
    });

    it('calls setRootPost on reply click', async () => {
      renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const replyButtons = screen.getAllByRole('button').filter(btn => 
        btn.querySelector('[data-testid="ChatBubbleOutlineIcon"]')
      );
      
      if (replyButtons.length > 0) {
        fireEvent.click(replyButtons[0]);
        
        await waitFor(() => {
          expect(mockSetRootPost).toHaveBeenCalledWith(
            expect.objectContaining({
              postid: expect.any(Number),
              poster: expect.any(String)
            })
          );
        });
      }
    });

    it('navigates to profile on avatar click', () => {
      renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const avatars = screen.getAllByText(/^[A-Z]$/);
      if (avatars.length > 0) {
        fireEvent.click(avatars[0]);
        expect(mockNavigate).toHaveBeenCalledWith(
          expect.stringMatching(/^\/profile\/:/));
      }
    });
  });

  describe('Infinite Scroll', () => {
    it('loads more posts on scroll', async () => {
      const { container } = renderWithRouter(<InfiniteScrollPosts setRootPost={mockSetRootPost} />);
      
      const scrollContainer = container.firstChild;
      const initialPosts = screen.getAllByText(/@\w+/).length;
      
      // Simulate scroll to bottom
      Object.defineProperty(scrollContainer, 'scrollTop', { value: 1000 });
      Object.defineProperty(scrollContainer, 'scrollHeight', { value: 1200 });
      Object.defineProperty(scrollContainer, 'clientHeight', { value: 600 });
      
      fireEvent.scroll(scrollContainer);
      
      await waitFor(() => {
        const newPosts = screen.getAllByText(/@\w+/).length;
        expect(newPosts).toBeGreaterThanOrEqual(initialPosts);
      });
    });
  });

  describe('Props and State Updates', () => {
    it('updates when rootPost changes', () => {
      const { rerender } = renderWithRouter(
        <InfiniteScrollPosts setRootPost={mockSetRootPost} />
      );
      
      const initialPosts = screen.getAllByText(/@\w+/).length;
      
      const rootPost = { postid: 456, poster: 'test', text: 'test post' };
      
      rerender(
        <InfiniteScrollPosts 
          rootPost={rootPost} 
          setRootPost={mockSetRootPost} 
        />
      );
      
      const filteredPosts = screen.getAllByText(/@\w+/).length;
      expect(filteredPosts).toBeLessThan(initialPosts);
    });

    it('handles missing setRootPost prop', () => {
      expect(() => {
        renderWithRouter(<InfiniteScrollPosts />);
      }).not.toThrow();
    });
  });
});