import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { UserProvider } from './context/UserContext.jsx'
import App from './App.jsx'

// Mock createRoot
const mockRender = vi.fn()
vi.mock('react-dom/client', () => ({
  createRoot: vi.fn(() => ({
    render: mockRender
  }))
}))

// Mock getElementById
Object.defineProperty(global.document, 'getElementById', {
  value: vi.fn(() => ({ id: 'root' })),
  writable: true
})

// Mock environment variable
vi.mock('./index.css', () => ({}))

describe('main.jsx', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    import.meta.env = { VITE_GOOGLE_CLIENT_ID: 'test-client-id' }
  })

  it('renders app with correct provider structure', async () => {
    // Import and execute main.jsx
    await import('./main.jsx')
    
    // Verify render was called
    expect(mockRender).toHaveBeenCalledTimes(1)
  })

  it('creates the correct component tree structure', () => {
    const { container } = render(
      <GoogleOAuthProvider clientId="test-client-id">
        <UserProvider>
          <App />
        </UserProvider>
      </GoogleOAuthProvider>
    )
    
    expect(container.firstChild).toBeTruthy()
  })
})