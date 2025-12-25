import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

// Axios 인스턴스 생성
// - baseURL: 환경변수 우선, 없으면 로컬 서버 사용
// - 기본 헤더: JSON 통신
const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/api`,
  headers: { 'Content-Type': 'application/json' }
})


// =========================
// 요청 인터셉터
// =========================
// - 매 요청마다 auth store를 동적으로 불러옴
// - 토큰이 있으면 Authorization 헤더에 추가
api.interceptors.request.use(config => {
  try {
    const auth = useAuthStore()
    if (auth?.token) {
      config.headers.Authorization = `Token ${auth.token}`
    }
  } catch (e) {
    // store 접근 실패 시 무시
  }
  return config
})


// =========================
// 응답 인터셉터
// =========================
// - 401(인증 실패) 전역 처리
// - 토큰 제거 후 로그인 페이지로 이동
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      try {
        const auth = useAuthStore()
        auth.logout()
      } catch (e) {
        // store 접근 실패 시 무시
      }
      router.push({ name: 'Login' })
    }
    return Promise.reject(error)
  }
)

export default api
