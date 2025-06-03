import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { UserProvider, useUser } from './UserContext';

// Test component to interact with the context
const TestComponent = () => {
  const { user, setUser } = useUser();
  
  return (
    <div>
      <div data-testid="user-display">
        {user ? `User: ${user.name}` : 'No user'}
      </div>
      <button 
        data-testid="set-user-btn"
        onClick={() => setUser({ name: 'John Doe', id: 1 })}
      >
        Set User
      </button>
      <button 
        data-testid="clear-user-btn"
        onClick={() => setUser(null)}
      >
        Clear User
      </button>
    </div>
  );
};

describe('UserContext', () => {
  it('provides initial null user state', () => {
    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    expect(screen.getByTestId('user-display')).toHaveTextContent('No user');
  });

  it('allows setting user data', () => {
    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    act(() => {
      screen.getByTestId('set-user-btn').click();
    });

    expect(screen.getByTestId('user-display')).toHaveTextContent('User: John Doe');
  });

  it('allows clearing user data', () => {
    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    // Set user first
    act(() => {
      screen.getByTestId('set-user-btn').click();
    });

    expect(screen.getByTestId('user-display')).toHaveTextContent('User: John Doe');

    // Clear user
    act(() => {
      screen.getByTestId('clear-user-btn').click();
    });

    expect(screen.getByTestId('user-display')).toHaveTextContent('No user');
  });

  it('throws error when useUser is used outside provider', () => {
    // Suppress console.error for this test
    const originalError = console.error;
    console.error = () => {};

    expect(() => {
      render(<TestComponent />);
    }).toThrow();

    console.error = originalError;
  });

  it('shares user state between multiple components', () => {
    const ComponentA = () => {
      const { user, setUser } = useUser();
      return (
        <div>
          <div data-testid="component-a-display">
            A: {user ? user.name : 'No user'}
          </div>
          <button 
            data-testid="component-a-set-btn"
            onClick={() => setUser({ name: 'Alice', id: 2 })}
          >
            Set Alice
          </button>
        </div>
      );
    };

    const ComponentB = () => {
      const { user } = useUser();
      return (
        <div data-testid="component-b-display">
          B: {user ? user.name : 'No user'}
        </div>
      );
    };

    render(
      <UserProvider>
        <ComponentA />
        <ComponentB />
      </UserProvider>
    );

    expect(screen.getByTestId('component-a-display')).toHaveTextContent('A: No user');
    expect(screen.getByTestId('component-b-display')).toHaveTextContent('B: No user');

    act(() => {
      screen.getByTestId('component-a-set-btn').click();
    });

    expect(screen.getByTestId('component-a-display')).toHaveTextContent('A: Alice');
    expect(screen.getByTestId('component-b-display')).toHaveTextContent('B: Alice');
  });
});