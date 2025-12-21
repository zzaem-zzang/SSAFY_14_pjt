<template>
  <div class="board-container">
    <div class="header-row">
      <h1>🗣️ 자유 게시판</h1>
      <router-link v-if="auth.isLogin" :to="{ name: 'PostCreate' }" class="write-btn">
        + 글쓰기
      </router-link>
    </div>

    <div v-if="error" class="error-box">{{ errorMessage }}</div>

    <div class="post-list">
      <div v-for="p in posts" :key="p.id" class="post-item" @click="goDetail(p.id)">
        <div class="post-content">
          <h3 class="post-title">{{ p.title }}</h3>
          <span class="post-meta">
            작성자: <b>{{ p.author.username }}</b> </span>
        </div>
        <div class="post-arrow">›</div>
      </div>
    </div>
    
    <div v-if="posts.length === 0 && !error" class="empty-state">
      등록된 게시글이 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const posts = ref([])
const error = ref(false)
const errorMessage = ref('')
const auth = useAuthStore()
const router = useRouter()

async function load() {
  try {
    const res = await api.get('/posts/')
    posts.value = res.data.results || res.data
  } catch (err) {
    error.value = true
    errorMessage.value = '게시글을 불러오지 못했습니다.'
  }
}

const goDetail = (id) => router.push({ name: 'PostDetail', params: { id } })

onMounted(load)
</script>

<style scoped>
.board-container { max-width: 800px; margin: 0 auto; }

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h1 { font-size: 1.8rem; color: #1e293b; margin: 0; }

.write-btn {
  background: #4f46e5;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  transition: background 0.2s;
}
.write-btn:hover { background: #4338ca; }

.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
  border-color: #e2e8f0;
}

.post-title { margin: 0 0 6px 0; font-size: 1.1rem; color: #334155; }
.post-meta { font-size: 0.85rem; color: #94a3b8; }
.post-arrow { font-size: 1.5rem; color: #cbd5e1; }
.error-box { color: red; margin-bottom: 10px; }
.empty-state { text-align: center; color: #94a3b8; margin-top: 40px; }
</style>