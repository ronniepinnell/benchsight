/**
 * Toast Notification Utilities
 * 
 * Simple toast notification system for tracker
 */

export type ToastType = 'success' | 'error' | 'warning' | 'info'

let toastContainer: HTMLDivElement | null = null

function ensureToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div')
    toastContainer.id = 'toast-container'
    toastContainer.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 z-50 space-y-2 pointer-events-none'
    document.body.appendChild(toastContainer)
  }
  return toastContainer
}

export function toast(message: string, type: ToastType = 'info', duration: number = 3000) {
  const container = ensureToastContainer()
  
  const toast = document.createElement('div')
  toast.className = `px-4 py-2 rounded-md shadow-lg pointer-events-auto transition-all transform translate-y-0 opacity-0 ${
    type === 'success' ? 'bg-green-600 text-white' :
    type === 'error' ? 'bg-red-600 text-white' :
    type === 'warning' ? 'bg-yellow-600 text-white' :
    'bg-blue-600 text-white'
  }`
  toast.textContent = message
  
  container.appendChild(toast)
  
  // Animate in
  requestAnimationFrame(() => {
    toast.classList.remove('opacity-0')
    toast.classList.add('opacity-100')
  })
  
  // Remove after duration
  setTimeout(() => {
    toast.classList.add('opacity-0', '-translate-y-2')
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast)
      }
    }, 300)
  }, duration)
  
  return toast
}
