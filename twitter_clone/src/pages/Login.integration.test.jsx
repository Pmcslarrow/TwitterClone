import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import LoginPage from './Login';
import { GoogleLogin } from '@react-oauth/google';

// --- Test Setup ---

const mockSetUser = vi.fn();
const mockNavigate = vi.fn();

// Mock all necessary dependencies
vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}));
vi.mock('react-router-dom', async (importActual) => {
    const actual = await importActual();
    return { ...actual, useNavigate: () => mockNavigate };
});
vi.mock('@react-oauth/google');
vi.mock('jwt-decode');
vi.spyOn(axios, 'post');

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('LoginPage Integration Test', () => {

  beforeEach(() => {
    vi.clearAllMocks();
    // For the login test, the component only needs the setUser function from the context
    useUser.mockReturnValue({ setUser: mockSetUser });
    
    // Mock the successful API response from our backend
    axios.post.mockResolvedValue({ 
        data: { username: 'johndoe1a2b3c', picture: 'https://example.com/pic.jpg', bio: 'A new user bio.' } 
    });
  });

  it('calls the create user endpoint after a successful Google sign-in', async () => {
    // ARRANGE
    let capturedOnSuccess;
    GoogleLogin.mockImplementation(({ onSuccess }) => {
        capturedOnSuccess = onSuccess; // Capture the function passed to the component
        return <button data-testid="mock-google-button">Sign In</button>;
    });
    
    const decodedToken = {
        name: 'John Doe',
        email: 'john.doe@example.com',
        picture: 'https://example.com/pic.jpg'
    };
    jwtDecode.mockReturnValue(decodedToken);
    
    renderWithProviders(<LoginPage />);

    // ACT: Simulate the Google login success callback being fired
    await capturedOnSuccess({ credential: 'mock-credential' });

    // ASSERT
    await waitFor(() => {
        // 1. Verify the create user API was called correctly
        expect(axios.post).toHaveBeenCalledWith(
            expect.stringContaining('/users/create/'),
            expect.objectContaining({ userid: decodedToken.email }),
            expect.anything()
        );

        // 2. Verify the user state was set and navigation occurred
        expect(mockSetUser).toHaveBeenCalled();
        expect(mockNavigate).toHaveBeenCalledWith('/home');
    });
  });
});