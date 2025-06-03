import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import EditProfile from './EditProfile';

// Mock the UserContext
const mockUpdateUser = vi.fn();
const mockUseUser = vi.fn();

vi.mock('../context/UserContext', () => ({
  useUser: () => mockUseUser()
}));

// Mock MUI components to avoid complex rendering issues in tests
vi.mock('@mui/material', () => ({
  Box: ({ children, ...props }) => <div data-testid="box" {...props}>{children}</div>,
  TextField: ({ label, value, onChange, ...props }) => (
    <input
      data-testid={`textfield-${label?.toLowerCase().replace(/\s+/g, '-')}`}
      placeholder={label}
      value={value}
      onChange={onChange}
      {...props}
    />
  ),
  Button: ({ children, onClick, disabled, ...props }) => (
    <button
      data-testid="save-button"
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  ),
  Typography: ({ children, color, ...props }) => (
    <div data-testid="typography" data-color={color} {...props}>{children}</div>
  ),
  Avatar: ({ src, alt, ...props }) => (
    <img data-testid="avatar" src={src} alt={alt} {...props} />
  ),
  Stack: ({ children, ...props }) => <div data-testid="stack" {...props}>{children}</div>,
  Paper: ({ children, ...props }) => <div data-testid="paper" {...props}>{children}</div>,
  IconButton: ({ children, onClick, ...props }) => (
    <button data-testid="close-button" onClick={onClick} {...props}>{children}</button>
  )
}));

vi.mock('@mui/icons-material/Close', () => ({
  default: () => <span data-testid="close-icon">×</span>
}));

describe('EditProfile', () => {
  const mockSetEditing = vi.fn();
  const mockUser = {
    userid: 'testuser',
    bio: 'Test bio',
    picture: 'https://example.com/avatar.jpg'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseUser.mockReturnValue({
      user: mockUser,
      updateUser: mockUpdateUser
    });
  });

  it('renders with user data pre-filled', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    expect(screen.getByDisplayValue('testuser')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test bio')).toBeInTheDocument();
    expect(screen.getByDisplayValue('https://example.com/avatar.jpg')).toBeInTheDocument();
  });

  it('renders with empty fields when user has no data', () => {
    mockUseUser.mockReturnValue({
      user: {},
      updateUser: mockUpdateUser
    });

    render(<EditProfile setEditing={mockSetEditing} />);
    
    expect(screen.getByPlaceholderText('Username (UserID)')).toHaveValue('');
    expect(screen.getByPlaceholderText('Bio')).toHaveValue('');
    expect(screen.getByPlaceholderText('Profile Picture URL')).toHaveValue('');
  });

  it('handles null user gracefully', () => {
    mockUseUser.mockReturnValue({
      user: null,
      updateUser: mockUpdateUser
    });

    render(<EditProfile setEditing={mockSetEditing} />);
    
    expect(screen.getByPlaceholderText('Username (UserID)')).toHaveValue('');
    expect(screen.getByPlaceholderText('Bio')).toHaveValue('');
    expect(screen.getByPlaceholderText('Profile Picture URL')).toHaveValue('');
  });

  it('updates input values when typing', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const useridInput = screen.getByDisplayValue('testuser');
    const bioInput = screen.getByDisplayValue('Test bio');
    const pictureInput = screen.getByDisplayValue('https://example.com/avatar.jpg');

    fireEvent.change(useridInput, { target: { value: 'newuser' } });
    fireEvent.change(bioInput, { target: { value: 'New bio' } });
    fireEvent.change(pictureInput, { target: { value: 'https://example.com/new.jpg' } });

    expect(useridInput).toHaveValue('newuser');
    expect(bioInput).toHaveValue('New bio');
    expect(pictureInput).toHaveValue('https://example.com/new.jpg');
  });

  it('calls setEditing(false) when close button is clicked', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const closeButton = screen.getByTestId('close-button');
    fireEvent.click(closeButton);
    
    expect(mockSetEditing).toHaveBeenCalledWith(false);
  });

  it('saves profile successfully', async () => {
    mockUpdateUser.mockResolvedValue();
    
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const saveButton = screen.getByTestId('save-button');
    fireEvent.click(saveButton);

    expect(saveButton).toHaveTextContent('Saving...');
    expect(saveButton).toBeDisabled();

    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({
        userid: 'testuser',
        bio: 'Test bio',
        picture: 'https://example.com/avatar.jpg'
      });
    });

    await waitFor(() => {
      expect(saveButton).toHaveTextContent('Save Changes');
      expect(saveButton).not.toBeDisabled();
    });
  });

  it('handles save error', async () => {
    mockUpdateUser.mockRejectedValue(new Error('API Error'));
    
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const saveButton = screen.getByTestId('save-button');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to update profile.')).toBeInTheDocument();
    });

    expect(saveButton).toHaveTextContent('Save Changes');
    expect(saveButton).not.toBeDisabled();
  });

  it('disables save button when userid is empty', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const useridInput = screen.getByDisplayValue('testuser');
    const saveButton = screen.getByTestId('save-button');

    fireEvent.change(useridInput, { target: { value: '' } });
    
    expect(saveButton).toBeDisabled();
  });

  it('disables save button when userid is only whitespace', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const useridInput = screen.getByDisplayValue('testuser');
    const saveButton = screen.getByTestId('save-button');

    fireEvent.change(useridInput, { target: { value: '   ' } });
    
    expect(saveButton).toBeDisabled();
  });

  it('displays avatar preview with current picture URL', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const avatar = screen.getByTestId('avatar');
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg');
    expect(avatar).toHaveAttribute('alt', 'testuser');
  });

  it('updates avatar preview when picture URL changes', () => {
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const pictureInput = screen.getByDisplayValue('https://example.com/avatar.jpg');
    const avatar = screen.getByTestId('avatar');

    fireEvent.change(pictureInput, { target: { value: 'https://example.com/new.jpg' } });
    
    expect(avatar).toHaveAttribute('src', 'https://example.com/new.jpg');
  });

  it('saves with modified values', async () => {
    mockUpdateUser.mockResolvedValue();
    
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const useridInput = screen.getByDisplayValue('testuser');
    const bioInput = screen.getByDisplayValue('Test bio');
    const pictureInput = screen.getByDisplayValue('https://example.com/avatar.jpg');

    fireEvent.change(useridInput, { target: { value: 'modifieduser' } });
    fireEvent.change(bioInput, { target: { value: 'Modified bio' } });
    fireEvent.change(pictureInput, { target: { value: 'https://example.com/modified.jpg' } });

    const saveButton = screen.getByTestId('save-button');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({
        userid: 'modifieduser',
        bio: 'Modified bio',
        picture: 'https://example.com/modified.jpg'
      });
    });
  });

  it('clears error when saving again after previous error', async () => {
    mockUpdateUser.mockRejectedValueOnce(new Error('API Error'))
                  .mockResolvedValueOnce();
    
    render(<EditProfile setEditing={mockSetEditing} />);
    
    const saveButton = screen.getByTestId('save-button');
    
    // First save - should error
    fireEvent.click(saveButton);
    await waitFor(() => {
      expect(screen.getByText('Failed to update profile.')).toBeInTheDocument();
    });

    // Second save - should clear error
    fireEvent.click(saveButton);
    await waitFor(() => {
      expect(screen.queryByText('Failed to update profile.')).not.toBeInTheDocument();
    });
  });
});