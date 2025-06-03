import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import RootPost from './RootPost';

describe('RootPost', () => {
  const mockSetRootPost = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const baseMockPost = {
    poster: 'testuser',
    text: 'This is a test post',
    likes: 5,
    retweets: 3,
    replies: 2,
    liked: false,
    retweeted: false,
    isRetweet: false,
    image: null,
  };

  describe('Basic rendering', () => {
    it('renders post content correctly', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('@testuser')).toBeInTheDocument();
      expect(screen.getByText('This is a test post')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('renders avatar with first letter of username', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('T')).toBeInTheDocument(); // First letter of 'testuser'
    });
  });

  describe('Retweet indicator', () => {
    it('shows retweet indicator when post is a retweet', () => {
      const retweetPost = { ...baseMockPost, isRetweet: true };

      render(<RootPost post={retweetPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('Retweeted')).toBeInTheDocument();
    });

    it('does not show retweet indicator when post is not a retweet', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      expect(screen.queryByText('Retweeted')).not.toBeInTheDocument();
    });
  });

  describe('Image rendering', () => {
    it('renders image when post has image', () => {
      const postWithImage = {
        ...baseMockPost,
        image: 'https://example.com/image.jpg',
      };

      render(<RootPost post={postWithImage} setRootPost={mockSetRootPost} />);

      const image = screen.getByRole('img', { name: 'Post' });
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', 'https://example.com/image.jpg');
    });

    it('does not render image when post has no image', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      expect(screen.queryByRole('img', { name: 'Post' })).not.toBeInTheDocument();
    });
  });

  describe('Interactive states', () => {
    it('shows filled heart icon when post is liked', () => {
      const likedPost = { ...baseMockPost, liked: true };

      render(<RootPost post={likedPost} setRootPost={mockSetRootPost} />);

      // Check for filled heart (red color)
      const heartIcon = screen.getByTestId('FavoriteIcon');
      expect(heartIcon).toBeInTheDocument();
    });

    it('shows outline heart icon when post is not liked', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      // Check for outline heart
      const heartIcon = screen.getByTestId('FavoriteBorderIcon');
      expect(heartIcon).toBeInTheDocument();
    });

    it('shows filled repeat icon when post is retweeted', () => {
      const retweetedPost = { ...baseMockPost, retweeted: true };

      render(<RootPost post={retweetedPost} setRootPost={mockSetRootPost} />);

      const repeatIcon = screen.getByTestId('RepeatIcon');
      expect(repeatIcon).toBeInTheDocument();
    });

    it('shows outline repeat icon when post is not retweeted', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      const repeatIcon = screen.getByTestId('RepeatOutlinedIcon');
      expect(repeatIcon).toBeInTheDocument();
    });
  });

  describe('Action buttons', () => {
    it('renders all action buttons', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      // Should have 4 buttons: close + 3 action buttons (like, retweet, comment)
      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(4);
    });

    it('displays comment icon', () => {
      render(<RootPost post={baseMockPost} setRootPost={mockSetRootPost} />);

      const commentIcon = screen.getByTestId('ChatBubbleOutlineIcon');
      expect(commentIcon).toBeInTheDocument();
    });
  });

  describe('Counter display', () => {
    it('displays zero values correctly', () => {
      const zeroPost = {
        ...baseMockPost,
        likes: 0,
        retweets: 0,
        replies: 0,
      };

      render(<RootPost post={zeroPost} setRootPost={mockSetRootPost} />);

      const zeroTexts = screen.getAllByText('0');
      expect(zeroTexts).toHaveLength(3);
    });

    it('displays large numbers correctly', () => {
      const popularPost = {
        ...baseMockPost,
        likes: 1000,
        retweets: 500,
        replies: 250,
      };

      render(<RootPost post={popularPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('1000')).toBeInTheDocument();
      expect(screen.getByText('500')).toBeInTheDocument();
      expect(screen.getByText('250')).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('handles empty text', () => {
      const emptyTextPost = { ...baseMockPost, text: '' };

      render(<RootPost post={emptyTextPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('@testuser')).toBeInTheDocument();
    });

    it('handles special characters in username', () => {
      const specialPost = { ...baseMockPost, poster: 'user_123' };

      render(<RootPost post={specialPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText('@user_123')).toBeInTheDocument();
      expect(screen.getByText('U')).toBeInTheDocument(); // Avatar
    });

    it('handles long text content', () => {
      const longTextPost = {
        ...baseMockPost,
        text: 'This is a very long post that contains multiple sentences and should be displayed properly even when it exceeds normal post length.',
      };

      render(<RootPost post={longTextPost} setRootPost={mockSetRootPost} />);

      expect(screen.getByText(longTextPost.text)).toBeInTheDocument();
    });
  });
});