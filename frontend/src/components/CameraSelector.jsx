import React from 'react'

function CameraSelector({ cameras, selectedCamera, onSelectCamera, onRefresh }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Cámaras Disponibles</h3>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          🔄 Detectar Cámaras
        </button>
      </div>
      
      {cameras.length === 0 ? (
        <div className="text-center py-4 text-gray-500">
          <p>No se detectaron cámaras disponibles</p>
          <p className="text-sm mt-2">Asegúrate de que tu cámara esté conectada</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cameras.map((camera) => (
            <div
              key={camera.id}
              onClick={() => onSelectCamera(camera)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedCamera?.id === camera.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{camera.name}</h4>
                {selectedCamera?.id === camera.id && (
                  <span className="text-blue-600 text-sm">✓ Seleccionada</span>
                )}
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>Tipo:</strong> {camera.type === 'usb' ? 'USB' : 'Dispositivo'}</p>
                {camera.resolution && (
                  <p><strong>Resolución:</strong> {camera.resolution}</p>
                )}
                {camera.fps && (
                  <p><strong>FPS:</strong> {camera.fps}</p>
                )}
                <p><strong>Fuente:</strong> {camera.source}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onSelectCamera(camera)
                }}
                className={`mt-3 w-full px-3 py-2 rounded text-sm ${
                  selectedCamera?.id === camera.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {selectedCamera?.id === camera.id ? 'Seleccionada' : 'Seleccionar'}
              </button>
            </div>
          ))}
        </div>
      )}
      
      {selectedCamera && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">
            <strong>Cámara activa:</strong> {selectedCamera.name} ({selectedCamera.source})
          </p>
          <p className="text-xs text-green-600 mt-1">
            La detección comenzará automáticamente cuando inicies el procesamiento
          </p>
        </div>
      )}
    </div>
  )
}

export default CameraSelector

