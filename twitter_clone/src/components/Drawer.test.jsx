import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LeftDrawer from './LeftDrawer';
import RightDrawer from './RightDrawer';

// Mock the UserContext
const mockUser = {
  userid: 'test123',
  username: 'testuser'
};

vi.mock('../context/UserContext', () => ({
  useUser: () => ({ user: mockUser })
}));

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

// Wrapper component for router context
const RouterWrapper = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('LeftDrawer Component', () => {
  const mockProps = {
    leftOpen: true,
    setLeftOpen: vi.fn(),
    setRootPost: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders when open', () => {
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    expect(screen.getByRole('presentation')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
  });

  test('does not render when closed', () => {
    const closedProps = { ...mockProps, leftOpen: false };
    
    render(
      <RouterWrapper>
        <LeftDrawer props={closedProps} />
      </RouterWrapper>
    );

    expect(screen.queryByText('Home')).not.toBeInTheDocument();
  });

  test('calls setLeftOpen(false) when close button clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    await user.click(screen.getByText('Close'));
    expect(mockProps.setLeftOpen).toHaveBeenCalledWith(false);
  });

  test('calls setLeftOpen(false) when drawer backdrop clicked', async () => {
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    const backdrop = document.querySelector('.MuiBackdrop-root');
    fireEvent.click(backdrop);
    expect(mockProps.setLeftOpen).toHaveBeenCalledWith(false);
  });

  test('navigates to home when Home button clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    await user.click(screen.getByText('Home'));
    expect(mockNavigate).toHaveBeenCalledWith('/home');
  });

  test('navigates to user profile when avatar clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    const avatar = screen.getByRole('img');
    await user.click(avatar);
    expect(mockNavigate).toHaveBeenCalledWith('/profile/test123');
  });

  test('renders avatar with correct attributes', () => {
    render(
      <RouterWrapper>
        <LeftDrawer props={mockProps} />
      </RouterWrapper>
    );

    const avatar = screen.getByRole('img');
    expect(avatar).toHaveAttribute('src', 'https://example.com/profile.jpg');
    expect(avatar).toHaveAttribute('alt', 'johndoe');
  });
});

describe('RightDrawer Component', () => {
  const mockProps = {
    rightOpen: true,
    setRightOpen: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders when open', () => {
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    expect(screen.getByRole('presentation')).toBeInTheDocument();
    expect(screen.getByText('Search Users')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search by username')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
  });

  test('does not render when closed', () => {
    const closedProps = { ...mockProps, rightOpen: false };
    
    render(
      <RouterWrapper>
        <RightDrawer props={closedProps} />
      </RouterWrapper>
    );

    expect(screen.queryByText('Search Users')).not.toBeInTheDocument();
  });

  test('displays all mock users initially', () => {
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    expect(screen.getByText('john_doe')).toBeInTheDocument();
    expect(screen.getByText('jane_smith')).toBeInTheDocument();
    expect(screen.getByText('sam_wilson')).toBeInTheDocument();
  });

  test('filters users based on search input', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search by username');
    await user.type(searchInput, 'john');

    expect(screen.getByText('john_doe')).toBeInTheDocument();
    expect(screen.queryByText('jane_smith')).not.toBeInTheDocument();
    expect(screen.queryByText('sam_wilson')).not.toBeInTheDocument();
  });

  test('shows no users when search matches none', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search by username');
    await user.type(searchInput, 'nonexistent');

    expect(screen.queryByText('john_doe')).not.toBeInTheDocument();
    expect(screen.queryByText('jane_smith')).not.toBeInTheDocument();
    expect(screen.queryByText('sam_wilson')).not.toBeInTheDocument();
  });

  test('search is case insensitive', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search by username');
    await user.type(searchInput, 'JOHN');

    expect(screen.getByText('john_doe')).toBeInTheDocument();
  });

  test('navigates to user profile when user item clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    await user.click(screen.getByText('john_doe'));
    expect(mockNavigate).toHaveBeenCalledWith('/profile/john123');
  });

  test('calls setRightOpen(false) when close button clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    await user.click(screen.getByText('Close'));
    expect(mockProps.setRightOpen).toHaveBeenCalledWith(false);
  });

  test('calls setRightOpen(false) when drawer backdrop clicked', async () => {
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const backdrop = document.querySelector('.MuiBackdrop-root');
    fireEvent.click(backdrop);
    expect(mockProps.setRightOpen).toHaveBeenCalledWith(false);
  });

  test('displays user bio information', () => {
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    expect(screen.getByText('Loves coding and coffee.')).toBeInTheDocument();
    expect(screen.getByText('Frontend developer and cat lover.')).toBeInTheDocument();
    expect(screen.getByText('Enjoys hiking and backend development.')).toBeInTheDocument();
  });

  test('renders user avatars with correct src attributes', () => {
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const avatars = screen.getAllByRole('img');
    expect(avatars[0]).toHaveAttribute('src', 'https://i.pravatar.cc/150?img=1');
    expect(avatars[1]).toHaveAttribute('src', 'https://i.pravatar.cc/150?img=2');
    expect(avatars[2]).toHaveAttribute('src', 'https://i.pravatar.cc/150?img=3');
  });

  test('clears search input', async () => {
    const user = userEvent.setup();
    
    render(
      <RouterWrapper>
        <RightDrawer props={mockProps} />
      </RouterWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search by username');
    await user.type(searchInput, 'test');
    await user.clear(searchInput);

    expect(searchInput).toHaveValue('');
    // All users should be visible again
    expect(screen.getByText('john_doe')).toBeInTheDocument();
    expect(screen.getByText('jane_smith')).toBeInTheDocument();
    expect(screen.getByText('sam_wilson')).toBeInTheDocument();
  });
});