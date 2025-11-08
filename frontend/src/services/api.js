// Configuración global de axios para manejo de errores
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

// Configurar axios con manejo de errores global
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para manejar errores
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // El servidor respondió con un código de error
      console.error('Error de respuesta:', error.response.status, error.response.data)
    } else if (error.request) {
      // La solicitud se hizo pero no se recibió respuesta
      console.error('Error de red: No se pudo conectar al backend en', API_URL)
      console.error('Verifica que el backend esté corriendo en http://localhost:8005')
    } else {
      // Algo más causó el error
      console.error('Error:', error.message)
    }
    // Retornar error para que pueda ser manejado por el componente
    return Promise.reject(error)
  }
)

export default api

