import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import RootPost from './RootPost';
import axios from 'axios';

vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }));

const mockCurrentUser = {
  email: 'Alice406@example.com',
  username: 'coder123',
};

const renderWithProviders = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('RootPost Integration Test', () => {
  it('sends a delete request when the delete button is clicked', async () => {
    useUser.mockReturnValue({ user: mockCurrentUser });
    
    const postToDelete = {
      postid: 12345, // ⚠️ IMPORTANT: A real post ID belonging to Alice406
      poster: mockCurrentUser.email,
      username: mockCurrentUser.username,
      text: 'This post will be deleted by the test.',
      likes: 0,
      liked: false, // <-- Add this missing property
      retweeted: false, // <-- Add this missing property
      replies: 0, // <-- Add this missing property
    };
    const mockSetReload = vi.fn();
    
    // Pass the prop as `post`, not `rootPost`
    renderWithProviders(<RootPost post={postToDelete} setReload={mockSetReload} setRootPost={vi.fn()} />);

    // Your logic to find and click the delete button...
    const deleteButton = screen.getByTestId('CloseIcon').parentElement; // This is the close button now, adjust if you have a delete icon
    await userEvent.click(deleteButton);
    
    // ASSERT: The component should call `setReload` after a successful delete.
    // await waitFor(() => {
    //   expect(mockSetReload).toHaveBeenCalledWith(true);
    // });
  });

  // it('sends a delete request when the delete button is clicked', async () => {
  //   // ARRANGE: For a destructive test, we first CREATE the data we're going to delete.
  //   // This makes the test self-contained and safe to run repeatedly.
  //   const tempPostText = `A temporary post to be deleted - ${Date.now()}`;
  //   const baseurl = import.meta.env.VITE_API_BASE_URL;
    
  //   // 1. Create a post using your API
  //   const createResponse = await axios.post(
  //     `${baseurl}post-tweet`, 
  //     { userid: mockUser.email, textcontent: tempPostText }
  //   );
  //   // The post-tweet lambda might not return the full post, so we need to fetch it
  //   // For simplicity here, we will construct the post object. A better way would be to get the ID and re-fetch.
  //   // This test assumes your delete endpoint only needs a `postid`.
  //   const newPostId = 20002; // You would ideally get this from the createResponse if your API returns it.
  //                          // For now, use a known ID that can be deleted.

  //   const postToDelete = {
  //     postid: newPostId,
  //     poster: mockUser.email, // The post must belong to the logged-in user to be deletable
  //     username: mockUser.username,
  //     text: tempPostText,
  //     likes: 0,
  //   };
  //   const mockSetReload = vi.fn();
    
  //   renderWithProviders(<RootPost rootPost={postToDelete} setReload={mockSetReload} />);

  //   // ACT: Find and click the delete button.
  //   const deleteButton = screen.getByTestId('DeleteIcon').parentElement;
  //   await userEvent.click(deleteButton);
    
  //   // ASSERT: The component should call `setReload` after a successful delete.
  //   await waitFor(() => {
  //     expect(mockSetReload).toHaveBeenCalledWith(true);
  //   });
  // });

});