import { defineStore } from 'pinia'
import api from '@/api'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null
  }),

  getters: {
    isLogin: state => !!state.token && !!state.user
  },

  actions: {
    init() {
      const token = localStorage.getItem(TOKEN_KEY)
      const userJson = localStorage.getItem(USER_KEY)

      if (token) this.token = token
      if (userJson) this.user = JSON.parse(userJson)
    },

    async login(credentials) {
      const res = await api.post('/auth/login/', credentials)

      this.token = res.data.token
      this.user = res.data.user

      localStorage.setItem(TOKEN_KEY, this.token)
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },

    // ✅ 정상 logout
    async logout() {
      // 🔥 토큰 있을 때만 서버에 알림
      if (this.token) {
        try {
          await api.post('/auth/logout/')
        } catch (e) {
          // 토큰 만료 등은 무시
        }
      }

      // 🔥 항상 로컬 상태 정리
      this.forceLogout()
    },

    // ✅ 강제 로그아웃 (401 등)
    forceLogout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },

    setUser(user) {
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    }
  }
})
