// Manejo global de errores no capturados
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled promise rejection:', event.reason)
  // No prevenir el error para que se muestre en consola, pero manejarlo
  if (event.reason?.message) {
    console.error('Detalles del error:', event.reason.message)
  }
  // Solo prevenir si es un error de conexión conocido
  if (event.reason?.code === 'ERR_NETWORK' || event.reason?.message?.includes('ERR_CONNECTION_RESET')) {
    event.preventDefault()
  }
})

// Manejo global de errores de JavaScript
window.addEventListener('error', event => {
  console.error('JavaScript error:', event.error)
  // No prevenir para ver errores reales
})

export {}

