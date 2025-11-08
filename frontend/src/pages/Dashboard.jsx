import React, { useState, useEffect } from 'react'
import axios from '../services/api'
import VideoPlayer from '../components/VideoPlayer'
import IncidentList from '../components/IncidentList'
import StatsCard from '../components/StatsCard'
import CameraSelector from '../components/CameraSelector'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

function Dashboard() {
  const [stats, setStats] = useState({
    totalIncidents: 0,
    todayIncidents: 0,
    activeCameras: 0,
    speedViolations: 0
  })
  const [recentIncidents, setRecentIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [availableCameras, setAvailableCameras] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchRecentIncidents()
    detectCameras()
    
    // Actualizar cada 30 segundos
    const interval = setInterval(() => {
      fetchStats()
      fetchRecentIncidents()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const detectCameras = async () => {
    try {
      setError(null)
      const response = await axios.get(`${API_URL}/api/camera-detection/detect`)
      const cameras = response.data?.cameras || []
      setAvailableCameras(cameras)
      // Seleccionar la primera cámara automáticamente si hay alguna
      if (cameras.length > 0 && !selectedCamera) {
        setSelectedCamera(cameras[0])
      }
    } catch (error) {
      console.error('Error detectando cámaras:', error)
      setError('No se pudieron detectar cámaras. Verifica que el backend esté corriendo en http://localhost:8005')
      setAvailableCameras([])
    }
  }

  const fetchStats = async () => {
    try {
      const [incidentsRes, camerasRes] = await Promise.all([
        axios.get(`${API_URL}/api/incidents/?limit=1000`).catch(err => {
          console.error('Error fetching incidents:', err)
          return { data: [] }
        }),
        axios.get(`${API_URL}/api/cameras/?is_active=true`).catch(err => {
          console.error('Error fetching cameras:', err)
          return { data: [] }
        })
      ])
      
      const incidents = incidentsRes.data || []
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const todayIncidents = incidents.filter(inc => {
        try {
          const incDate = new Date(inc.timestamp)
          return incDate >= today
        } catch {
          return false
        }
      })
      
      const speedViolations = incidents.filter(inc => inc.incident_type === 'speed')
      
      setStats({
        totalIncidents: incidents.length,
        todayIncidents: todayIncidents.length,
        activeCameras: camerasRes.data?.length || 0,
        speedViolations: speedViolations.length
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
      setStats({
        totalIncidents: 0,
        todayIncidents: 0,
        activeCameras: 0,
        speedViolations: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentIncidents = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/incidents/?limit=10`)
      setRecentIncidents(response.data || [])
    } catch (error) {
      console.error('Error fetching recent incidents:', error)
      setRecentIncidents([])
    }
  }

  if (loading) {
    return <div className="text-center py-8">Cargando...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Dashboard</h2>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={detectCameras}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Reintentar
          </button>
        </div>
      )}
      
      {/* Selector de Cámaras */}
      <div className="bg-white rounded-lg shadow p-4">
        <CameraSelector
          cameras={availableCameras}
          selectedCamera={selectedCamera}
          onSelectCamera={setSelectedCamera}
          onRefresh={detectCameras}
        />
      </div>
      
      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Total Incidentes" value={stats.totalIncidents} color="blue" />
        <StatsCard title="Hoy" value={stats.todayIncidents} color="green" />
        <StatsCard title="Cámaras Activas" value={stats.activeCameras} color="purple" />
        <StatsCard title="Infracciones Velocidad" value={stats.speedViolations} color="red" />
      </div>

      {/* Video Player y Lista de Incidentes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-xl font-semibold mb-4">Vista en Vivo</h3>
          <VideoPlayer 
            cameraId={selectedCamera?.id || null} 
            source={selectedCamera?.source || null}
            cameraName={selectedCamera?.name || 'Sin cámara seleccionada'}
          />
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-xl font-semibold mb-4">Incidentes Recientes</h3>
          <IncidentList incidents={recentIncidents} />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
