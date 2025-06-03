import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import ProfileHeader from './ProfileHeader';

// Mock the UserContext
const mockUseUser = vi.fn();
vi.mock('../context/UserContext', () => ({
  useUser: () => mockUseUser()
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

// Wrapper component for providers
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('ProfileHeader', () => {
  const defaultProps = {
    profileUserId: 'testuser123',
    bio: 'Web3 enthusiast. Tweets about code, coffee, and cats.',
    picture: 'https://example.com/profile.jpg'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock default user context
    mockUseUser.mockReturnValue({
      user: { userid: 'currentuser' }
    });
  });

  it('renders without crashing', () => {
    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
  });

  it('displays user ID', () => {
    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    expect(screen.getByText('testuser123')).toBeInTheDocument();
  });

  it('displays bio text', () => {
    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    expect(screen.getByText('Web3 enthusiast. Tweets about code, coffee, and cats.')).toBeInTheDocument();
  });

  it('displays profile picture', () => {
    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    const profileImage = screen.getByRole('img');
    expect(profileImage).toHaveAttribute('src', 'https://example.com/profile.jpg');
  });

  it('shows edit button for own profile', () => {
    mockUseUser.mockReturnValue({
      user: { userid: 'testuser123' }
    });

    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    expect(screen.getByText('Edit')).toBeInTheDocument();
  });

  it('hides edit button for other profiles', () => {
    mockUseUser.mockReturnValue({
      user: { userid: 'differentuser' }
    });

    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });

  it('navigates to home when avatar is clicked', () => {
    render(<ProfileHeader {...defaultProps} />, { wrapper: TestWrapper });
    
    const avatar = screen.getByRole('img');
    fireEvent.click(avatar);
    
    expect(mockNavigate).toHaveBeenCalledWith('/home');
  });

  it('shows default bio when none provided', () => {
    render(<ProfileHeader {...defaultProps} bio="" />, { wrapper: TestWrapper });
    
    expect(screen.getByText('No bio yet.')).toBeInTheDocument();
  });
});