<template>
  <div class="write-container" v-if="post">
    <div class="write-card">
      <h1>게시글 수정 🛠️</h1>
      
      <div class="input-group">
        <label>제목</label>
        <input v-model="title" class="title-input" />
      </div>

      <div class="input-group">
        <label>내용</label>
        <textarea v-model="content" class="content-input"></textarea>
      </div>

      <div class="button-group">
        <button @click="router.back()" class="btn-cancel">취소</button>
        <button @click="update" class="btn-submit">수정 완료</button>
      </div>
    </div>
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

onMounted(async () => {
  try {
    const res = await api.get(`/posts/${route.params.id}/`)
    post.value = res.data
    title.value = res.data.title
    content.value = res.data.content

    // 권한 체크
    if (!(auth.user.id === res.data.author.id || auth.user.is_staff)) {
      alert('권한이 없습니다.')
      router.push({ name: 'PostDetail', params: { id: route.params.id } })
    }
  } catch (err) {
    if (err.response?.status === 404) router.push({ name: 'PostList' })
  }
})

async function update() {
  try {
    await api.put(`/posts/${route.params.id}/`, { title: title.value, content: content.value })
    router.push({ name: 'PostDetail', params: { id: route.params.id } })
  } catch (err) {
    alert('수정 중 오류가 발생했습니다.')
  }
}
</script>

<style scoped>
/* PostCreateView와 동일한 스타일 사용 */
.write-container { max-width: 800px; margin: 0 auto; }
.write-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
h1 { margin-top: 0; margin-bottom: 30px; color: #1e293b; font-size: 1.5rem; }
.input-group { margin-bottom: 24px; }
.input-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #334155; }
.title-input { width: 100%; padding: 14px; font-size: 1.1rem; border: 1px solid #e2e8f0; border-radius: 10px; }
.content-input { width: 100%; min-height: 300px; padding: 14px; font-size: 1rem; border: 1px solid #e2e8f0; border-radius: 10px; resize: vertical; line-height: 1.6; }
.title-input:focus, .content-input:focus { outline: none; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.button-group { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
.btn-cancel { padding: 12px 24px; background: #f1f5f9; color: #64748b; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit { padding: 12px 24px; background: #4f46e5; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-submit:hover { background: #4338ca; }
</style>