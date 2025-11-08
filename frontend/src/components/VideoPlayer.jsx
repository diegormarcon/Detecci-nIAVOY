import React, { useState, useEffect, useRef } from 'react'
import axios from '../services/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

function VideoPlayer({ cameraId, source, cameraName }) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [status, setStatus] = useState('idle')
  const [detectionStatus, setDetectionStatus] = useState(null)
  const [error, setError] = useState(null)
  const [videoStarted, setVideoStarted] = useState(false)
  const [detectionFrame, setDetectionFrame] = useState(null)
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const frameIntervalRef = useRef(null)

  useEffect(() => {
    if (source && cameraId !== null) {
      setStatus('ready')
      checkDetectionStatus()
    } else {
      setStatus('idle')
      stopLocalVideo()
      stopFramePolling()
    }
    
    // Verificar estado cada 2 segundos si está corriendo
    const interval = setInterval(() => {
      if (status === 'running') {
        checkDetectionStatus()
      }
    }, 2000)
    
    return () => {
      clearInterval(interval)
      stopLocalVideo()
      stopFramePolling()
    }
  }, [source, cameraId, status])

  const startFramePolling = () => {
    // Polling para obtener frames del detector cada 100ms
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current)
    }
    
    frameIntervalRef.current = setInterval(async () => {
      if (cameraId !== null && status === 'running') {
        try {
          const response = await axios.get(`${API_URL}/api/camera-detection/frame/${cameraId}`)
          if (response.data?.frame) {
            setDetectionFrame(response.data.frame)
          }
        } catch (error) {
          // Silenciar errores si no hay frame disponible aún
          if (error.response?.status !== 404) {
            console.error('Error obteniendo frame:', error)
          }
        }
      }
    }, 100) // Actualizar cada 100ms (~10 FPS)
  }

  const stopFramePolling = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current)
      frameIntervalRef.current = null
    }
    setDetectionFrame(null)
  }

  const startLocalVideo = async () => {
    try {
      setError(null)
      // Obtener lista de dispositivos disponibles
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')
      
      // Intentar acceder a la cámara local usando getUserMedia
      let constraints = {
        video: { facingMode: 'user' }, // Por defecto cámara frontal
        audio: false
      }
      
      // Si source es un número y hay dispositivos disponibles, intentar usar ese índice
      if (source && !isNaN(source) && videoDevices.length > parseInt(source)) {
        constraints.video = { deviceId: { exact: videoDevices[parseInt(source)].deviceId } }
      }
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setVideoStarted(true)
        setStatus('ready')
      }
    } catch (err) {
      console.error('Error accediendo a la cámara:', err)
      setError('No se pudo acceder a la cámara: ' + err.message)
      setVideoStarted(false)
    }
  }

  const stopLocalVideo = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setVideoStarted(false)
  }

  const checkDetectionStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/detection/status`)
      const process = response.data.processes?.find(p => p.camera_id === cameraId)
      if (process && process.running) {
        setStatus('running')
        setDetectionStatus(process)
        startFramePolling() // Iniciar polling de frames
      } else if (status === 'running') {
        setStatus('ready')
        stopFramePolling()
      }
    } catch (error) {
      console.error('Error verificando estado:', error)
    }
  }

  const startDetection = async () => {
    if (!source || cameraId === null) {
      setError('Por favor selecciona una cámara primero')
      return
    }
    
    setIsProcessing(true)
    setStatus('processing')
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/api/detection/start`, {
        camera_id: cameraId,
        source: source,
        display: true  // Mostrar ventana de video
      })
      
      setStatus('running')
      setDetectionStatus(response.data)
      setIsProcessing(false)
      
      // Iniciar polling de frames después de un breve delay
      setTimeout(() => {
        startFramePolling()
      }, 1000)
      
      // Mostrar mensaje informativo
      if (response.data.message) {
        alert(response.data.message)
      } else {
        alert('Detección iniciada. El video con detecciones se mostrará aquí.')
      }
    } catch (error) {
      console.error('Error iniciando detección:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido'
      setError('Error al iniciar detección: ' + errorMsg)
      setStatus('ready')
      setIsProcessing(false)
    }
  }

  const stopDetection = async () => {
    try {
      await axios.post(`${API_URL}/api/detection/stop/${cameraId}`)
      setStatus('ready')
      setDetectionStatus(null)
      setError(null)
      stopFramePolling()
    } catch (error) {
      console.error('Error deteniendo detección:', error)
      setError('Error al detener detección')
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-black rounded-lg aspect-video flex items-center justify-center relative overflow-hidden">
        {status === 'idle' ? (
          <div className="text-white text-center">
            <p className="text-lg mb-2">Selecciona una cámara</p>
            <p className="text-sm text-gray-400">Usa el selector de cámaras arriba</p>
          </div>
        ) : status === 'ready' ? (
          <div className="w-full h-full relative">
            {/* Mostrar frame del detector si está disponible, sino mostrar video local o overlay */}
            {detectionFrame ? (
              <img
                src={detectionFrame}
                alt="Detección en vivo"
                className="w-full h-full object-contain"
                style={{ display: 'block' }}
              />
            ) : videoStarted ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-white bg-black bg-opacity-75">
                <div className="text-center">
                  <p className="text-lg mb-2">Cámara: {cameraName}</p>
                  <p className="text-sm text-gray-400 mb-4">Fuente: {source}</p>
                  <button
                    onClick={startLocalVideo}
                    className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 mb-3"
                  >
                    📹 Iniciar Cámara
                  </button>
                  <p className="text-xs text-gray-500 mb-4">o</p>
                  <button
                    onClick={startDetection}
                    disabled={isProcessing}
                    className="px-6 py-3 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    ▶ Iniciar Detección
                  </button>
                  <p className="text-xs text-gray-400 mt-2">
                    La detección mostrará el video con detecciones aquí
                  </p>
                </div>
              </div>
            )}
            {/* Controles cuando el video está activo */}
            {videoStarted && !detectionFrame && (
              <div className="absolute bottom-4 left-4 right-4 flex justify-center space-x-2">
                <button
                  onClick={stopLocalVideo}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                >
                  ⏹ Detener Cámara
                </button>
                <button
                  onClick={startDetection}
                  disabled={isProcessing}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm"
                >
                  ▶ Iniciar Detección
                </button>
              </div>
            )}
          </div>
        ) : status === 'processing' ? (
          <div className="text-white text-center">
            <p className="text-lg mb-2">Iniciando detección...</p>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          </div>
        ) : (
          <div className="w-full h-full relative">
            {/* Mostrar frame del detector con detecciones */}
            {detectionFrame ? (
              <img
                src={detectionFrame}
                alt="Detección en vivo"
                className="w-full h-full object-contain"
                style={{ display: 'block' }}
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-white bg-black bg-opacity-50">
                <div className="text-center">
                  <p className="text-lg mb-2">Esperando frames del detector...</p>
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
                </div>
              </div>
            )}
            {/* Overlay cuando está corriendo */}
            <div className="absolute top-4 right-4">
              <div className="flex items-center space-x-2 bg-red-600 px-3 py-1 rounded">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span className="text-xs">EN VIVO</span>
              </div>
            </div>
            {detectionStatus && (
              <div className="absolute top-4 left-4 bg-black bg-opacity-75 px-3 py-1 rounded">
                <p className="text-xs text-white">PID: {detectionStatus.process_id}</p>
              </div>
            )}
            <div className="absolute bottom-4 left-4 right-4 flex justify-center">
              <button
                onClick={stopDetection}
                className="px-6 py-3 bg-red-600 text-white rounded hover:bg-red-700"
              >
                ⏹ Detener Detección
              </button>
            </div>
          </div>
        )}
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
      
      {status === 'running' && !error && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3">
          <p className="text-sm text-blue-800">
            <strong>Estado:</strong> Procesando video de {cameraName}
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Los incidentes detectados aparecerán automáticamente en la lista de incidentes.
            {detectionFrame ? ' Video con detecciones visible arriba.' : ' Esperando frames del detector...'}
          </p>
        </div>
      )}
    </div>
  )
}

export default VideoPlayer
