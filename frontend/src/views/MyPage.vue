<template>
  <div class="mypage-container">
    <h2 class="title">마이페이지</h2>

    <!-- 내 정보 -->
    <div class="card">
      <h3>내 정보</h3>
      <p><strong>아이디:</strong> {{ auth.user.username }}</p>
      <p><strong>닉네임:</strong> {{ auth.user.nickname }}</p>
    </div>

    <!-- 로그아웃 -->
    <div class="card">
      <button @click="logout" class="btn">
        로그아웃
      </button>
    </div>

    <!-- 회원탈퇴 -->
    <div class="card danger">
      <button @click="withdraw" class="btn danger">
        회원탈퇴
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/api'

const auth = useAuthStore()
const router = useRouter()

const logout = async () => {
  await auth.logout()
  auth.forceLogout()
  router.push('/')
}

const withdraw = async () => {
  if (!confirm('정말 탈퇴하시겠습니까?\n모든 데이터가 삭제됩니다.')) return

  await api.post('/auth/withdraw/')
  auth.forceLogout()
  router.push('/')
}
</script>

<style scoped>
.mypage-container {
  max-width: 500px;
  margin: 0 auto;
}

.title {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 30px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 14px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.card h3 {
  margin-bottom: 12px;
}

.btn {
  padding: 10px;
  width: 100%;
  border-radius: 10px;
  border: none;
  cursor: pointer;
}

.btn.danger {
  background: #dc2626;
  color: white;
}

.card.danger {
  border-color: #fee2e2;
}
</style>
