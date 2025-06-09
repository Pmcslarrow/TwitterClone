import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext'; // Import the hook to mock it
import Prompt from './Prompt';

// --- Test Setup ---

const mockCurrentUser = {
  email: 'Alice406@example.com',
  username: 'coder123',
};

// Mock the useUser hook
vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}));

// Spy on axios.post to check its arguments
vi.spyOn(axios, 'post');

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Prompt Integration Test', () => {

  beforeEach(() => {
    // Reset mocks and set the return value for the hook before each test
    axios.post.mockClear();
    useUser.mockReturnValue({ user: mockCurrentUser });
    // Assume the API call will succeed for these tests
    axios.post.mockResolvedValue({ status: 200, data: {} });
  });

  it('should send a new post to the create endpoint', async () => {
    // ARRANGE
    const mockSetReload = vi.fn();
    const postText = 'This is a new integration test post!';
    renderWithProviders(<Prompt setReload={mockSetReload} />);

    // ACT
    const textField = screen.getByPlaceholderText(/what's happening/i);
    await userEvent.type(textField, postText);

    const postButton = screen.getByRole('button', { name: /post/i });
    await userEvent.click(postButton);

    // ASSERT
    await waitFor(() => {
      // Verify axios was called with the correct payload for a new post
      const expectedPayload = {
        userid: mockCurrentUser.email,
        textcontent: postText,
      };
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/tweets/create'),
        expectedPayload,
        expect.anything()
      );
      
      // Verify the form was cleared and reloaded
      expect(mockSetReload).toHaveBeenCalledWith(true);
    });
  });
});