import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const getAnalysis = () => api.get('/analyze')
export const getLivePrices = () => api.get('/live-prices')
export const getPriceTrends = () => api.get('/price-trends')
export const postOptimization = (data) => api.post('/optimize', data)
export const savePreferences = (data) => api.post('/preferences', data)
export const getPreferences = () => api.get('/preferences')
export const calculateComfort = (avoidHours) => api.post('/calculate-comfort', { avoid_hours: avoidHours })
export const saveAppliances = (data) => api.post('/appliances', data)
export const getAppliances = () => api.get('/appliances')

export default api