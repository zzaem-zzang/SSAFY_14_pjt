<template>
  <div class="post-detail-container">
    <div v-if="post" class="content-wrapper">
      
      <article class="post-card">
        <div class="post-header">
          <h1 class="title">{{ post.title }}</h1>
          <div class="meta">
            <span class="author">✍️ {{ post.author.username }}</span>
            </div>
        </div>

        <div class="post-body" v-html="post.content"></div>

        <div v-if="canEdit" class="action-buttons">
          <router-link :to="{ name: 'PostEdit', params: { id: post.id } }" class="btn btn-edit">수정</router-link>
          <button @click="deletePost" class="btn btn-delete">삭제</button>
        </div>
      </article>

      <section class="comments-section">
        <h3>댓글 <span class="count">{{ post.comments.length }}</span></h3>
        
        <ul class="comment-list">
          <li v-for="c in post.comments" :key="c.id" class="comment-item">
            <div class="comment-author">{{ c.author.username }}</div>
            <div class="comment-text">{{ c.content }}</div>
          </li>
          <li v-if="post.comments.length === 0" class="empty-comment">
            첫 번째 댓글을 남겨보세요!
          </li>
        </ul>

        <div v-if="auth.isLogin" class="comment-form">
          <textarea
            v-model="newComment"
            placeholder="댓글을 입력하세요..."
            rows="3"
          ></textarea>
          <button @click="createComment" class="btn-submit">등록</button>
        </div>
        <div v-else class="login-plz">
          댓글을 작성하려면 <router-link :to="{ name: 'Login' }">로그인</router-link>이 필요합니다.
        </div>
      </section>

    </div>
    <div v-else class="loading">게시글을 불러오는 중...</div>
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

// 게시글 불러오기
async function load() {
  try {
    const res = await api.get(`/posts/${route.params.id}/`)
    post.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      alert('삭제되었거나 없는 게시글입니다.')
      router.push({ name: 'PostList' })
    }
  }
}

// 권한 확인
const canEdit = computed(() => auth.isLogin && post.value && (auth.user.id === post.value.author.id || auth.user.is_staff))

// 게시글 삭제
async function deletePost() {
  if(!confirm('정말 삭제하시겠습니까?')) return
  try {
    await api.delete(`/posts/${route.params.id}/`)
    router.push({ name: 'PostList' })
  } catch (err) {
    alert('삭제 실패')
  }
}

// 댓글 작성
async function createComment() {
  if (!newComment.value.trim()) return
  try {
    await api.post(`/posts/${route.params.id}/comments/`, { content: newComment.value })
    await load()
    newComment.value = ''
  } catch (err) {
    alert('댓글 작성 실패')
  }
}

onMounted(load)
</script>

<style scoped>
.post-detail-container {
  max-width: 800px;
  margin: 0 auto;
}

/* 게시글 카드 스타일 */
.post-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.post-header {
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 20px;
  margin-bottom: 30px;
}

.title { margin: 0 0 10px; font-size: 2rem; color: #1e293b; }
.meta { color: #64748b; font-size: 0.95rem; }

.post-body {
  line-height: 1.8;
  color: #334155;
  font-size: 1.05rem;
  min-height: 200px;
}

/* 버튼 스타일 */
.action-buttons {
  margin-top: 40px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
}
.btn-edit { background: #f1f5f9; color: #475569; }
.btn-edit:hover { background: #e2e8f0; }
.btn-delete { background: #fee2e2; color: #dc2626; }
.btn-delete:hover { background: #fecaca; }

/* 댓글 스타일 */
.comments-section h3 { margin-bottom: 20px; color: #1e293b; }
.count { color: #4f46e5; margin-left: 4px; }

.comment-list {
  list-style: none;
  padding: 0;
  margin-bottom: 30px;
}

.comment-item {
  background: white;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 10px;
  border: 1px solid #f1f5f9;
}

.comment-author { font-weight: 700; color: #334155; margin-bottom: 4px; font-size: 0.9rem; }
.comment-text { color: #475569; }
.empty-comment { text-align: center; color: #94a3b8; padding: 20px; }

.comment-form { display: flex; flex-direction: column; gap: 10px; }
textarea {
  width: 100%; padding: 16px; border-radius: 12px;
  border: 1px solid #e2e8f0; resize: vertical; outline: none;
}
textarea:focus { border-color: #4f46e5; }

.btn-submit {
  align-self: flex-end;
  background: #4f46e5; color: white; border: none;
  padding: 10px 24px; border-radius: 8px; cursor: pointer;
}
.login-plz { text-align: center; color: #64748b; margin-top: 20px; }
.login-plz a { color: #4f46e5; font-weight: 600; text-decoration: underline; }
</style>