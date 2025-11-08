import React from 'react'

function IncidentList({ incidents }) {
  if (incidents.length === 0) {
    return <div className="text-gray-500 text-center py-4">No hay incidentes recientes</div>
  }

  return (
    <div className="space-y-2">
      {incidents.map((incident) => (
        <div
          key={incident.id}
          className="border rounded p-3 hover:bg-gray-50"
        >
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium">
                {incident.incident_type} - {incident.detected_class}
              </div>
              <div className="text-sm text-gray-600">
                Track ID: {incident.track_id}
                {incident.speed_kmh && ` - ${incident.speed_kmh.toFixed(1)} km/h`}
              </div>
            </div>
            <div className="text-xs text-gray-500">
              {new Date(incident.timestamp).toLocaleTimeString('es-ES')}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default IncidentList

