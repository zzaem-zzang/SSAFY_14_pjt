<template>
  <div class="write-container">
    <div class="write-card">
      <h1>새 글 작성 ✏️</h1>
      
      <div class="input-group">
        <label>제목</label>
        <input v-model="title" placeholder="제목을 입력하세요" class="title-input" />
      </div>

      <div class="input-group">
        <label>내용</label>
        <textarea v-model="content" placeholder="내용을 자유롭게 작성해주세요" class="content-input"></textarea>
      </div>

      <div class="button-group">
        <button @click="router.back()" class="btn-cancel">취소</button>
        <button @click="create" class="btn-submit">등록하기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const title = ref('')
const content = ref('')

async function create() {
  if(!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 입력해주세요.')
    return
  }

  try {
    const res = await api.post('/posts/', { title: title.value, content: content.value })
    router.push({ name: 'PostDetail', params: { id: res.data.id } })
  } catch (err) {
    if (err.response?.status === 401) {
      alert('로그인이 필요합니다.')
      router.push({ name: 'Login' })
    } else {
      alert('글 작성 중 오류가 발생했습니다.')
    }
  }
}
</script>

<style scoped>
.write-container {
  max-width: 800px;
  margin: 0 auto;
}

.write-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

h1 { margin-top: 0; margin-bottom: 30px; color: #1e293b; font-size: 1.5rem; }

.input-group { margin-bottom: 24px; }
.input-group label {
  display: block; font-weight: 600; margin-bottom: 8px; color: #334155;
}

.title-input {
  width: 100%; padding: 14px; font-size: 1.1rem;
  border: 1px solid #e2e8f0; border-radius: 10px;
}

.content-input {
  width: 100%; min-height: 300px; padding: 14px;
  font-size: 1rem; border: 1px solid #e2e8f0; border-radius: 10px;
  resize: vertical; line-height: 1.6;
}

.title-input:focus, .content-input:focus {
  outline: none; border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.button-group {
  display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px;
}

.btn-cancel {
  padding: 12px 24px; background: #f1f5f9; color: #64748b;
  border: none; border-radius: 10px; font-weight: 600; cursor: pointer;
}
.btn-submit {
  padding: 12px 24px; background: #4f46e5; color: white;
  border: none; border-radius: 10px; font-weight: 600; cursor: pointer;
}
.btn-submit:hover { background: #4338ca; }
</style>