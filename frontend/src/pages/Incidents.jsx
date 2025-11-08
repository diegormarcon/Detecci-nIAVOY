import React, { useState, useEffect } from 'react'
import axios from '../services/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    incident_type: '',
    camera_id: '',
    start_date: '',
    end_date: '',
    license_plate: ''
  })

  useEffect(() => {
    fetchIncidents()
  }, [filters])

  const fetchIncidents = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      
      const response = await axios.get(`${API_URL}/api/incidents/?${params}`)
      setIncidents(response.data || [])
    } catch (error) {
      console.error('Error fetching incidents:', error)
      setIncidents([])
    } finally {
      setLoading(false)
    }
  }

  const getIncidentTypeColor = (type) => {
    const colors = {
      speed: 'bg-red-100 text-red-800',
      helmet: 'bg-yellow-100 text-yellow-800',
      zone_invasion: 'bg-orange-100 text-orange-800',
      default: 'bg-gray-100 text-gray-800'
    }
    return colors[type] || colors.default
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Incidentes</h2>
      
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4">Filtros</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Tipo</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={filters.incident_type}
              onChange={(e) => setFilters({...filters, incident_type: e.target.value})}
            >
              <option value="">Todos</option>
              <option value="speed">Velocidad</option>
              <option value="helmet">Casco</option>
              <option value="zone_invasion">Invasión de Zona</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Fecha Inicio</label>
            <input
              type="date"
              className="w-full border rounded px-3 py-2"
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Fecha Fin</label>
            <input
              type="date"
              className="w-full border rounded px-3 py-2"
              value={filters.end_date}
              onChange={(e) => setFilters({...filters, end_date: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Matrícula</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              placeholder="Buscar por matrícula..."
              value={filters.license_plate}
              onChange={(e) => setFilters({...filters, license_plate: e.target.value})}
            />
          </div>
        </div>
      </div>

      {/* Lista de Incidentes */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="text-center py-8">Cargando...</div>
        ) : incidents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No se encontraron incidentes</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Clase</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Velocidad</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matrícula</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {incidents.map((incident) => (
                <tr key={incident.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{incident.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getIncidentTypeColor(incident.incident_type)}`}>
                      {incident.incident_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{incident.detected_class}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {incident.speed_kmh ? `${incident.speed_kmh.toFixed(1)} km/h` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{incident.license_plate || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(incident.timestamp).toLocaleString('es-ES')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      incident.status === 'approved' ? 'bg-green-100 text-green-800' :
                      incident.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {incident.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Incidents

