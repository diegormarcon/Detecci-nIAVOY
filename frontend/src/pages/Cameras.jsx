import React, { useState, useEffect } from 'react'
import axios from '../services/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

function Cameras() {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState(null)

  useEffect(() => {
    fetchCameras()
  }, [])

  const fetchCameras = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cameras/`)
      setCameras(response.data || [])
    } catch (error) {
      console.error('Error fetching cameras:', error)
      setCameras([])
    } finally {
      setLoading(false)
    }
  }

  const handleCalibrate = (camera) => {
    setSelectedCamera(camera)
    setShowModal(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-800">Cámaras</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Agregar Cámara
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-2">{camera.name}</h3>
              <p className="text-gray-600 mb-4">{camera.location}</p>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Estado:</span>
                  <span className={`text-sm font-medium ${
                    camera.is_active ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {camera.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
                
                {camera.speed_limit && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Límite Velocidad:</span>
                    <span className="text-sm font-medium">{camera.speed_limit} km/h</span>
                  </div>
                )}
                
                {camera.calibration_matrix && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Calibración:</span>
                    <span className="text-sm font-medium text-green-600">✓ Calibrada</span>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => handleCalibrate(camera)}
                  className="flex-1 bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 text-sm"
                >
                  Calibrar
                </button>
                <button className="flex-1 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm">
                  Ver Video
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && selectedCamera && (
        <CalibrationModal
          camera={selectedCamera}
          onClose={() => setShowModal(false)}
          onSave={fetchCameras}
        />
      )}
    </div>
  )
}

function CalibrationModal({ camera, onClose, onSave }) {
  const [pixelPoints, setPixelPoints] = useState([['', ''], ['', ''], ['', ''], ['', '']])
  const [realPoints, setRealPoints] = useState([['', ''], ['', ''], ['', ''], ['', '']])

  const handleSave = async () => {
    try {
      const pixel = pixelPoints.map(p => [parseFloat(p[0]), parseFloat(p[1])]).filter(p => !isNaN(p[0]) && !isNaN(p[1]))
      const real = realPoints.map(p => [parseFloat(p[0]), parseFloat(p[1])]).filter(p => !isNaN(p[0]) && !isNaN(p[1]))
      
      if (pixel.length < 4 || real.length < 4) {
        alert('Por favor completa al menos 4 puntos en ambos conjuntos')
        return
      }
      
      await axios.post(`${API_URL}/api/cameras/${camera.id}/calibrate`, {
        pixel_points: pixel,
        real_points: real
      })
      
      onSave()
      onClose()
    } catch (error) {
      console.error('Error calibrating camera:', error)
      alert('Error al calibrar la cámara: ' + (error.response?.data?.detail || error.message))
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
        <h3 className="text-xl font-semibold mb-4">Calibrar Cámara: {camera.name}</h3>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-2">Puntos en Píxeles</h4>
            {pixelPoints.map((point, i) => (
              <div key={i} className="mb-2">
                <label className="text-sm">Punto {i + 1}:</label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    className="w-full border rounded px-2 py-1"
                    placeholder="X"
                    value={point[0]}
                    onChange={(e) => {
                      const newPoints = [...pixelPoints]
                      newPoints[i][0] = e.target.value
                      setPixelPoints(newPoints)
                    }}
                  />
                  <input
                    type="number"
                    className="w-full border rounded px-2 py-1"
                    placeholder="Y"
                    value={point[1]}
                    onChange={(e) => {
                      const newPoints = [...pixelPoints]
                      newPoints[i][1] = e.target.value
                      setPixelPoints(newPoints)
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Puntos Reales (metros)</h4>
            {realPoints.map((point, i) => (
              <div key={i} className="mb-2">
                <label className="text-sm">Punto {i + 1}:</label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    step="0.1"
                    className="w-full border rounded px-2 py-1"
                    placeholder="X (m)"
                    value={point[0]}
                    onChange={(e) => {
                      const newPoints = [...realPoints]
                      newPoints[i][0] = e.target.value
                      setRealPoints(newPoints)
                    }}
                  />
                  <input
                    type="number"
                    step="0.1"
                    className="w-full border rounded px-2 py-1"
                    placeholder="Y (m)"
                    value={point[1]}
                    onChange={(e) => {
                      const newPoints = [...realPoints]
                      newPoints[i][1] = e.target.value
                      setRealPoints(newPoints)
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="mt-6 flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Guardar Calibración
          </button>
        </div>
      </div>
    </div>
  )
}

export default Cameras

