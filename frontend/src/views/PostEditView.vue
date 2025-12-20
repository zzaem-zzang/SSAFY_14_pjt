<template>
  <div v-if="post">
    <h1>Edit Post</h1>
    <input v-model="title" />
    <textarea v-model="content"></textarea>
    <button @click="update">Save</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const title = ref('')
const content = ref('')
const auth = useAuthStore()

async function load() {
  try {
    const res = await api.get(`/posts/${route.params.id}/`)
    post.value = res.data
    title.value = res.data.title
    content.value = res.data.content
    if (!(auth.user.id === res.data.author.id || auth.user.is_staff)) {
      alert('권한이 없습니다.'); router.push({ name: 'PostDetail', params: { id: route.params.id } })
    }
  } catch (err) {
    if (err.response?.status === 404) router.push({ name: 'PostList' })
  }
}

async function update() {
  try {
    await api.put(`/posts/${route.params.id}/`, { title: title.value, content: content.value })
    router.push({ name: 'PostDetail', params: { id: route.params.id } })
  } catch (err) {
    if (err.response?.status === 403) alert('권한이 없습니다.')
    else if (err.response?.status === 401) router.push({ name: 'Login' })
  }
}

onMounted(load)
</script>