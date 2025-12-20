import { defineStore } from 'pinia'
import api from '@/api'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: null, user: null }),
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
    logout() {
      try {
        api.post('/auth/logout/')
      } catch (e) {}
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