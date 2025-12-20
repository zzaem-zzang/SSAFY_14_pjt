<template>
  <div v-if="post">
    <h1>{{ post.title }}</h1>
    <p>by {{ post.author.username }}</p>
    <div v-html="post.content"></div>

    <div v-if="canEdit">
      <router-link :to="{ name: 'PostEdit', params: { id: post.id } }">Edit</router-link>
      <button @click="deletePost">Delete</button>
    </div>

    <hr />
    <h3>Comments</h3>
    <ul>
      <li v-for="c in post.comments" :key="c.id">{{ c.author.username }}: {{ c.content }}</li>
    </ul>

    <div v-if="auth.isLogin">
      <textarea v-model="newComment"></textarea>
      <button @click="createComment">Comment</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const newComment = ref('')
const auth = useAuthStore()

async function load() {
  try {
    const res = await api.get(`/posts/${route.params.id}/`)
    post.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      router.push({ name: 'PostList' })
    }
  }
}

const canEdit = computed(() => auth.isLogin && (auth.user.id === post.value?.author.id || auth.user.is_staff))

async function createComment() {
  try {
    await api.post(`/posts/${route.params.id}/comments/`, { content: newComment.value })
    await load()
    newComment.value = ''
  } catch (err) {
    if (err.response?.status === 401) router.push({ name: 'Login' })
  }
}

async function deletePost() {
  if (!confirm('Delete?')) return
  try {
    await api.delete(`/posts/${post.value.id}/`)
    router.push({ name: 'PostList' })
  } catch (err) {
    if (err.response?.status === 403) alert('권한이 없습니다.')
    else if (err.response?.status === 401) router.push({ name: 'Login' })
  }
}

onMounted(load)
</script>