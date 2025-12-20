import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' }
})

// 요청 interceptor: 동적으로 auth store를 가져와 토큰 추가
api.interceptors.request.use(config => {
  try {
    const auth = useAuthStore()
    if (auth?.token) config.headers.Authorization = `Token ${auth.token}`
  } catch (e) {}
  return config
})

// 응답 interceptor: 401 전역 처리
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      try {
        const auth = useAuthStore()
        auth.logout()
      } catch (e) {}
      router.push({ name: 'Login' })
    }
    return Promise.reject(error)
  }
)

export default api
