import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import EditProfile from './EditProfile';

vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importActual) => {
    const actual = await importActual();
    return { ...actual, useNavigate: () => mockNavigate };
});
vi.spyOn(axios, 'post');

const mockCurrentUser = {
    email: 'Alice406@example.com',
    username: 'coder123',
    bio: 'Original bio here.',
    picture: 'https://example.com/original.jpg'
};
const mockSetUser = vi.fn(); // Declare mockSetUser in the outer scope

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('EditProfile Integration Test', () => {
  beforeEach(() => {
    axios.post.mockClear();
    mockSetUser.mockClear();
    mockNavigate.mockClear();
    useUser.mockReturnValue({ user: mockCurrentUser, setUser: mockSetUser });
    axios.post.mockResolvedValue({ status: 200, data: {} });
  });
  
  it('pre-fills the form with data from UserContext', () => {
    // ARRANGE
    renderWithProviders(<EditProfile setEditing={vi.fn()} />);
    
    // ASSERT
    expect(screen.getByLabelText('Username')).toHaveValue(mockCurrentUser.username);
    expect(screen.getByLabelText('Bio')).toHaveValue(mockCurrentUser.bio);
    expect(screen.getByLabelText('Profile Picture URL')).toHaveValue(mockCurrentUser.picture);
  });

  it('sends updated data to the backend on save', async () => {
    // ARRANGE
    renderWithProviders(<EditProfile setEditing={vi.fn()} />);
    const newUsername = 'coder_is_awesome';
    const newBio = 'This is my new and updated bio!';

    // ACT
    await userEvent.clear(screen.getByLabelText('Username'));
    await userEvent.type(screen.getByLabelText('Username'), newUsername);
    await userEvent.clear(screen.getByLabelText('Bio'));
    await userEvent.type(screen.getByLabelText('Bio'), newBio);
    
    await userEvent.click(screen.getByRole('button', { name: /save changes/i }));

    // ASSERT
    await waitFor(() => {
      const expectedPayload = {
        userid: mockCurrentUser.email,
        username: newUsername,
        bio: newBio,
        picture: mockCurrentUser.picture // Picture was not changed
      };

      // Verify the correct API endpoint and payload were used
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/users/update-profile'),
        expectedPayload,
        expect.anything()
      );

      // Verify the local user state was updated
      expect(mockSetUser).toHaveBeenCalledWith(expect.objectContaining({
        username: newUsername,
        bio: newBio
      }));

      // Verify navigation occurred
      expect(mockNavigate).toHaveBeenCalledWith(`/profile/${newUsername}`);
    });
  });
});