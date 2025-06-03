import { useEffect, useState } from 'react'
import LoginPage from './pages/Login'
import Homepage from './pages/Homepage';
import Profile from './pages/Profile';
import ErrorPage from './pages/Error' 

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';


function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/home" element={<Homepage />} />
        <Route path="/profile/:profileuserid" element={<Profile />} />
        <Route path="/profile/undefined" element={<ErrorPage />} /> {/* Catch-all route */}
        <Route path="*" element={<ErrorPage />} /> {/* Catch-all route */}
      </Routes>
    </Router>
  )
}

export default App
