import React, { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix para iconos de Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

function MapView() {
  const [cameras, setCameras] = React.useState([])
  const [incidents, setIncidents] = React.useState([])

  useEffect(() => {
    // Cargar cámaras e incidentes
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'
    
    fetch(`${API_URL}/api/cameras/`)
      .then(res => {
        if (!res.ok) throw new Error('Error al cargar cámaras')
        return res.json()
      })
      .then(data => setCameras(data || []))
      .catch(err => {
        console.error('Error loading cameras:', err)
        setCameras([])
      })
    
    fetch(`${API_URL}/api/incidents/?limit=100`)
      .then(res => {
        if (!res.ok) throw new Error('Error al cargar incidentes')
        return res.json()
      })
      .then(data => setIncidents(data || []))
      .catch(err => {
        console.error('Error loading incidents:', err)
        setIncidents([])
      })
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Mapa de Incidentes</h2>
      
      <div className="bg-white rounded-lg shadow" style={{ height: '600px' }}>
        <MapContainer
          center={[-34.6037, -58.3816]} // Buenos Aires por defecto
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          
          {cameras.map((camera) => {
            if (camera.latitude && camera.longitude) {
              return (
                <Marker
                  key={camera.id}
                  position={[camera.latitude, camera.longitude]}
                >
                  <Popup>
                    <div>
                      <h3 className="font-semibold">{camera.name}</h3>
                      <p>{camera.location}</p>
                      <p className="text-sm text-gray-600">
                        {camera.is_active ? 'Activa' : 'Inactiva'}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )
            }
            return null
          })}
        </MapContainer>
      </div>
      
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-2">Leyenda</h3>
        <div className="flex space-x-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded-full mr-2"></div>
            <span>Cámaras</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapView

