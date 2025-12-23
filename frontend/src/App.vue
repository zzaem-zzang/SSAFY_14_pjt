<template>
  <div class="app-container">
    <nav class="navbar">
      <div class="nav-content">
        <router-link to="/" class="logo">💊 MediSearch</router-link>
        <div class="nav-links">
          <router-link to="/">홈</router-link>
          <router-link :to="{ name: 'PostList' }">커뮤니티</router-link>
          <!-- 로그인 완료 상태-->
          <div v-if="auth.isLogin" class="user-menu">
            <router-link v-if="auth.isLogin" :to="{ name: 'MyPage' }" class="nickname-link">
              {{ auth.user?.nickname }}님
            </router-link>

            <button @click="handleLogout" class="logout-btn">로그아웃</button>
          </div>
          <!-- 비로그인 상태 -->
          <div v-else class="auth-links">
            <router-link :to="{ name: 'Login' }" class="login-btn">로그인</router-link>
            <router-link :to="{ name: 'SignUp' }" class="signup-btn">회원가입</router-link>
          </div>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await auth.logout()   // ⭐ 서버 로그아웃 완료까지 대기
  router.push({ name: 'Login' })
}

const clearSearch = () => {
  router.push({
    path: '/',      // query 없이 이동
  })
}
</script>

<style>
/* 🌍 전역 스타일 (Global CSS) */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
  background-color: #f8fafc;
  color: #334155;
}

a {
  text-decoration: none;
  color: inherit;
}

button {
  font-family: inherit;
}

/* 레이아웃 */
.navbar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 20px;
}

.nav-content {
  max-width: 1000px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.25rem;
  font-weight: 800;
  color: #4f46e5;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
  font-weight: 500;
  color: #64748b;
}

.nav-links a:hover {
  color: black;
}

.nav-links a.router-link-active {
  color: black;
  font-weight: 700;
}

.login-btn,
.logout-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
}

.login-btn {
  background: #4f46e5;
  color: white;
}

.logout-btn {
  background: #f1f5f9;
  color: #64748b;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 80vh;
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 12px;
  /* ← 이 값으로 간격 조절 */
}

.nickname-link {
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
}

.nickname-link:hover {
  text-decoration: underline;
  color: #4f46e5;
}

</style>