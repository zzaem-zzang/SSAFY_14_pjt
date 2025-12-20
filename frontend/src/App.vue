<template>
  <div class="container">
    <header class="header">
      <div class="header-inner">
        <h1>💊 의약품 서비스</h1>
        <nav class="nav">
          <router-link to="/">홈</router-link>
          <router-link to="/posts">게시글</router-link>
          <router-link to="/posts/create" v-if="auth.isLogin">글쓰기</router-link>
          <span class="spacer"></span>
          <template v-if="auth.isLogin">
            <span class="user">{{ auth.user.username }}</span>
            <button class="link-btn" @click="logout">로그아웃</button>
          </template>
          <router-link v-else to="/login">로그인</router-link>
        </nav>
      </div>
    </header>

    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
const auth = useAuthStore()
const { isLogin, user } = storeToRefs(auth)

function logout() {
  auth.logout()
}
</script>

<style>
body {
  margin: 0;
  background-color: #f5f6f8;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

.container {
  max-width: 1024px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  margin-bottom: 24px;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

h1 {
  margin: 0;
}

.nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav a {
  color: #333;
  text-decoration: none;
}

.spacer {
  width: 16px;
}

.user {
  font-weight: 600;
  margin-right: 8px;
}

.link-btn {
  border: none;
  background: transparent;
  color: #4f46e5;
  cursor: pointer;
}
</style>
