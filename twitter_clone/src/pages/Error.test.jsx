import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ErrorPage from './Error';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper function to render component with router
const renderWithRouter = (component) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('ErrorPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders 404 error message', () => {
    renderWithRouter(<ErrorPage />);
    
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  });

  it('renders go back home button', () => {
    renderWithRouter(<ErrorPage />);
    
    const button = screen.getByRole('button', { name: /go back home/i });
    expect(button).toBeInTheDocument();
  });

  it('navigates to /home when button is clicked', () => {
    renderWithRouter(<ErrorPage />);
    
    const button = screen.getByRole('button', { name: /go back home/i });
    fireEvent.click(button);
    
    expect(mockNavigate).toHaveBeenCalledWith('/home');
    expect(mockNavigate).toHaveBeenCalledTimes(1);
  });

  it('has accessible button', () => {
    renderWithRouter(<ErrorPage />);
    
    const button = screen.getByRole('button', { name: /go back home/i });
    expect(button).toBeEnabled();
    expect(button).toHaveAttribute('type', 'button');
  });
});