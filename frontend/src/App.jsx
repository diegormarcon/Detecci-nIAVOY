import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Incidents from './pages/Incidents'
import Cameras from './pages/Cameras'
import MapView from './pages/MapView'
import './App.css'

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-600 text-white shadow-lg">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">Sistema de Detección VOI</h1>
              <div className="space-x-4">
                <Link to="/" className="hover:text-blue-200">Dashboard</Link>
                <Link to="/incidents" className="hover:text-blue-200">Incidentes</Link>
                <Link to="/cameras" className="hover:text-blue-200">Cámaras</Link>
                <Link to="/map" className="hover:text-blue-200">Mapa</Link>
              </div>
            </div>
          </div>
        </nav>
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/cameras" element={<Cameras />} />
            <Route path="/map" element={<MapView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

