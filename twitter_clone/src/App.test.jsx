import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import App from './App'

// Mock the page components
vi.mock('./pages/Login', () => ({
  default: () => <div data-testid="login-page">Login Page</div>
}))

vi.mock('./pages/Homepage', () => ({
  default: () => <div data-testid="homepage">Homepage</div>
}))

vi.mock('./pages/Profile', () => ({
  default: () => <div data-testid="profile-page">Profile Page</div>
}))

vi.mock('./pages/Error', () => ({
  default: () => <div data-testid="error-page">Error Page</div>
}))

// Mock the entire react-router-dom to replace BrowserRouter with MemoryRouter
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    BrowserRouter: ({ children }) => children
  }
})

describe('App', () => {
  const renderAppWithRouter = (initialEntries) => {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <App />
      </MemoryRouter>
    )
  }

  it('renders LoginPage on root path', () => {
    renderAppWithRouter(['/'])
    expect(screen.getByTestId('login-page')).toBeInTheDocument()
  })

  it('renders Homepage on /home path', () => {
    renderAppWithRouter(['/home'])
    expect(screen.getByTestId('homepage')).toBeInTheDocument()
  })

  it('renders Profile page on /profile/:profileuserid path', () => {
    renderAppWithRouter(['/profile/123'])
    expect(screen.getByTestId('profile-page')).toBeInTheDocument()
  })

  it('renders ErrorPage for unknown routes', () => {
    renderAppWithRouter(['/unknown-route'])
    expect(screen.getByTestId('error-page')).toBeInTheDocument()
  })

  it('renders ErrorPage for nested unknown routes', () => {
    renderAppWithRouter(['/some/nested/unknown/path'])
    expect(screen.getByTestId('error-page')).toBeInTheDocument()
  })
})