import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter, useParams } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import ProfileHeader from './ProfileHeader';

// --- Test Setup ---
const mockCurrentUser = {
  email: 'Alice406@example.com',
  username: 'coder123',
};

// Mock the hooks from external libraries
vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }));
vi.mock('react-router-dom', async (importActual) => {
  const actual = await importActual();
  return { ...actual, useParams: vi.fn() };
});

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ProfileHeader Integration Test', () => {

  beforeEach(() => {
    // Reset mocks before each test to ensure a clean slate
    vi.clearAllMocks();
  });
  
  // This test now has a 10-second timeout
  it('should fetch a user profile and display the action buttons', async () => {
    // ARRANGE
    // ⚠️ IMPORTANT: 'UserToView' must be a real username in your dev database.
    const profileUsername = 'bobster';
    useParams.mockReturnValue({ profileUsername });
    useUser.mockReturnValue({ user: mockCurrentUser });

    renderWithProviders(
      <ProfileHeader setIsUserFollowed={vi.fn()} setIsUserBlocked={vi.fn()} />
    );

    // ACT & ASSERT
    // This test is now more robust. Instead of looking for specific bio text,
    // we wait for the Follow/Unfollow button. This button ONLY appears after the
    // API call successfully completes, proving the integration works.
    const followButton = await screen.findByRole(
      'button', 
      { name: /follow|unfollow/i }, // Looks for a button with text "Follow" OR "Unfollow"
      { timeout: 10000 } // Wait up to 10 seconds
    );

    // Assert that the button (and therefore the whole header) has loaded.
    expect(followButton).toBeInTheDocument();
    expect(screen.getByText(profileUsername)).toBeInTheDocument();

  }, 10000); // <-- This increases the timeout for this specific test
});