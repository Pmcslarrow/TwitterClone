import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import LoginPage from './Login';

// Mock dependencies
vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(() => ({
    setUser: vi.fn()
  }))
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(() => vi.fn())
  };
});

vi.mock('@react-oauth/google', () => ({
  GoogleLogin: vi.fn(({ onSuccess, onError }) => (
    <div data-testid="google-login">
      <button 
        onClick={() => onSuccess({ credential: 'mock-credential' })}
        data-testid="google-login-success"
      >
        Sign in with Google
      </button>
      <button 
        onClick={onError}
        data-testid="google-login-error"
      >
        Trigger Error
      </button>
    </div>
  ))
}));

vi.mock('jwt-decode', () => ({
  jwtDecode: vi.fn(() => ({
    name: 'John Doe',
    email: 'john.doe@example.com'
  }))
}));

const theme = createTheme();

const renderWithProviders = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </ThemeProvider>
  );
};

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders welcome text and login elements', () => {
    renderWithProviders(<LoginPage />);
    
    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText('Sign in to continue to your account')).toBeInTheDocument();
    expect(screen.getByTestId('google-login')).toBeInTheDocument();
  });

  it('handles successful Google login', async () => {
    const { useUser } = await import('../context/UserContext');
    const { useNavigate } = await import('react-router-dom');
    const { jwtDecode } = await import('jwt-decode');
    
    const mockSetUser = vi.fn();
    const mockNavigate = vi.fn();
    
    useUser.mockReturnValue({ setUser: mockSetUser });
    useNavigate.mockReturnValue(mockNavigate);
    
    renderWithProviders(<LoginPage />);
    
    const successButton = screen.getByTestId('google-login-success');
    successButton.click();
    
    expect(jwtDecode).toHaveBeenCalledWith('mock-credential');
    expect(mockSetUser).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/home');
    
    // Verify userid generation
    const userCall = mockSetUser.mock.calls[0][0];
    expect(userCall).toHaveProperty('userid');
    expect(userCall.userid).toMatch(/johndoe[a-z0-9]+/);
  });

  it('handles Google login error', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    
    renderWithProviders(<LoginPage />);
    
    const errorButton = screen.getByTestId('google-login-error');
    errorButton.click();
    
    expect(consoleSpy).toHaveBeenCalledWith('Login Failed');
    
    consoleSpy.mockRestore();
  });

  it('generates unique userid for each login', async () => {
    const { useUser } = await import('../context/UserContext');
    const mockSetUser = vi.fn();
    useUser.mockReturnValue({ setUser: mockSetUser });
    
    renderWithProviders(<LoginPage />);
    
    const successButton = screen.getByTestId('google-login-success');
    
    // Simulate multiple logins
    successButton.click();
    const firstUserId = mockSetUser.mock.calls[0][0].userid;
    
    // Small delay to ensure different timestamp
    await new Promise(resolve => setTimeout(resolve, 1));
    
    successButton.click();
    const secondUserId = mockSetUser.mock.calls[1][0].userid;
    
    expect(firstUserId).not.toBe(secondUserId);
  });
});