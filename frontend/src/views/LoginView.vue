<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="header">
        <h1>환영합니다! 👋</h1>
        <p>서비스 이용을 위해 로그인해주세요.</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input
            v-model="username"
            id="username"
            type="text"
            placeholder="아이디를 입력하세요"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            v-model="password"
            id="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
          />
        </div>

        <div v-if="errorMessage" class="error-msg">
          ⚠️ {{ errorMessage }}
        </div>

        <button type="submit" class="btn-login" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const router = useRouter();
const auth = useAuthStore();

const handleLogin = async () => {
  if (!username.value || !password.value) return;
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    await auth.login({ username: username.value, password: password.value })
    router.push({ name: 'home' })
  } catch (error) {
    errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; /* 화면 중앙 정렬 */
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 { margin: 0 0 8px; font-size: 1.8rem; color: #1e293b; }
.header p { margin: 0; color: #64748b; font-size: 0.95rem; }

.form-group { margin-bottom: 20px; }
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #334155;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
}

input:focus {
  border-color: #4f46e5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.btn-login {
  width: 100%;
  padding: 14px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.2s;
}

.btn-login:hover { background: #4338ca; }
.btn-login:disabled { background: #94a3b8; cursor: not-allowed; }

.error-msg {
  color: #dc2626;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 16px;
  background: #fef2f2;
  padding: 10px;
  border-radius: 8px;
}
</style>