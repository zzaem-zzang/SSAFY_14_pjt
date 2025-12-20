<template>
  <div>
    <h1>Posts</h1>
    <div v-if="error">Error: {{ errorMessage }}</div>
    <ul>
      <li v-for="p in posts" :key="p.id">
        <router-link :to="{ name: 'PostDetail', params: { id: p.id } }">{{ p.title }}</router-link>
        — by {{ p.author.username }}
      </li>
    </ul>
    <router-link v-if="auth.isLogin" :to="{ name: 'PostCreate' }">Create Post</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const posts = ref([])
const error = ref(false)
const errorMessage = ref('')
const auth = useAuthStore()

async function load() {
  try {
    const res = await api.get('/posts/')
    posts.value = res.data.results || res.data
  } catch (err) {
    error.value = true
    errorMessage.value = err.response?.data?.detail || err.message
  }
}

onMounted(load)
</script>