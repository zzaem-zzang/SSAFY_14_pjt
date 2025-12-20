import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import api from '@/api'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// init auth store
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore(pinia)
auth.init()

app.mount('#app')

export { api }
