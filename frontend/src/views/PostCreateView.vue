<template>
  <div>
    <h1>Create Post</h1>
    <div>
      <input v-model="title" placeholder="title" />
      <textarea v-model="content" placeholder="content"></textarea>
      <button @click="create">Create</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const title = ref('')
const content = ref('')

async function create() {
  try {
    const res = await api.post('/posts/', { title: title.value, content: content.value })
    router.push({ name: 'PostDetail', params: { id: res.data.id } })
  } catch (err) {
    if (err.response?.status === 401) router.push({ name: 'Login' })
    else alert('Error')
  }
}
</script>