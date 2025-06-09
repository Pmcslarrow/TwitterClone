import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import LeftDrawer from './LeftDrawer';
import RightDrawer from './RightDrawer';

// --- Test Setup ---
const mockCurrentUser = {
  email: 'Alice406@example.com',
  username: 'coder123',
  picture: 'https://example.com/pic.jpg',
};

// Mock the useUser hook
vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importActual) => {
  const actual = await importActual();
  return { ...actual, useNavigate: () => mockNavigate };
});

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('LeftDrawer', () => {
  const mockSetUser = vi.fn();
  const mockProps = { leftOpen: true, setLeftOpen: vi.fn() };

  beforeEach(() => {
    vi.clearAllMocks();
    // Set the return value for the mock hook before each test
    useUser.mockReturnValue({ user: mockCurrentUser, setUser: mockSetUser });
  });

  it('navigates to the user profile when the avatar is clicked', async () => {
    renderWithProviders(<LeftDrawer props={mockProps} />);
    await userEvent.click(screen.getByAltText(mockCurrentUser.username));
    expect(mockNavigate).toHaveBeenCalledWith(`/profile/${mockCurrentUser.username}`);
  });
});

// describe('RightDrawer', () => {
//     const mockProps = { rightOpen: true, setRightOpen: vi.fn() };

//     beforeEach(() => {
//         vi.clearAllMocks();
//         useUser.mockReturnValue({ user: mockCurrentUser });
//     });
  
//     it('should fetch users from the backend and display them', async () => {
//       renderWithProviders(<RightDrawer props={mockProps} />);
//       expect(await screen.findByRole('progressbar')).toBeInTheDocument();

//     // Then, wait for a specific user to appear.
//     // ⚠️ IMPORTANT: Replace 'A-Username-From-Your-DB' with a real username
//     // that exists in your database and is NOT the same as `mockUser.username`.
//     const someOtherUser = await screen.findByText('coder123', {}, { timeout: 20000 });
//     expect(someOtherUser).toBeInTheDocument();

//     // Verify the currently logged-in user is NOT in the list
//     expect(screen.queryByText(mockUser.username)).not.toBeInTheDocument();
//   });

//   // it('should filter the fetched users based on search input', async () => {
//   //   // ARRANGE: Render and wait for the initial user list to load
//   //   renderWithProviders(<RightDrawer props={mockProps} />, { value: { user: mockUser } });
    
//   //   // ⚠️ IMPORTANT: Use two real, different usernames from your database here.
//   //   const userToFind = 'bobster';
//   //   const userToHide = 'claireBear';

//   //   await screen.findByText(userToFind, {}, { timeout: 20000 });
//   //   await screen.findByText(userToHide, {}, { timeout: 20000 });

//   //   // ACT: Type into the search input
//   //   const searchInput = screen.getByPlaceholderText(/search by username/i);
//   //   await userEvent.type(searchInput, userToFind);

//   //   // ASSERT: Check that the correct user is still visible and the other is hidden
//   //   expect(screen.getByText(userToFind)).toBeInTheDocument();
//   //   expect(screen.queryByText(userToHide)).not.toBeInTheDocument();
//   // });
// });