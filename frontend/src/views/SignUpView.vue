<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="header">
        <h1>회원가입 📝</h1>
        <p>간단한 정보 입력으로 계정을 생성하세요.</p>
      </div>

      <form @submit.prevent="handleSignUp" class="login-form">
        <!-- 아이디 -->
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

        <!-- 닉네임 -->
        <div class="form-group">
          <label for="nickname">닉네임</label>
          <input
            v-model="nickname"
            id="nickname"
            type="text"
            placeholder="서비스에서 사용할 닉네임"
            required
          />
        </div>

        <!-- 비밀번호 -->
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

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input
            v-model="passwordConfirm"
            id="passwordConfirm"
            type="password"
            placeholder="비밀번호를 다시 입력하세요"
            required
          />
        </div>

        <!-- 비밀번호 불일치 안내 -->
        <div
          v-if="password && passwordConfirm && password !== passwordConfirm"
          class="error-msg"
        >
          ⚠️ 비밀번호가 일치하지 않습니다.
        </div>

        <!-- 서버 에러 -->
        <div v-if="errorMessage" class="error-msg">
          ⚠️ {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="btn-login"
          :disabled="isLoading"
        >
          {{ isLoading ? '가입 중...' : '회원가입' }}
        </button>
      </form>

      <div class="footer-text">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const username = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleSignUp = async () => {
  errorMessage.value = ''

  if (password.value !== passwordConfirm.value) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  isLoading.value = true

  try {
    await api.post('/auth/register/', {
      username: username.value,
      nickname: nickname.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })

    alert('회원가입이 완료되었습니다. 로그인해주세요.')
    router.push('/login')

  } catch (err) {
    const data = err.response?.data

    if (data?.username) {
      errorMessage.value = data.username[0]
    } else if (data?.nickname) {
      errorMessage.value = data.nickname[0]
    } else if (data?.password_confirm) {
      errorMessage.value = data.password_confirm[0]
    } else {
      errorMessage.value = '회원가입에 실패했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 🔥 로그인 화면과 완전히 동일한 스타일 */
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
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

.header h1 {
  margin: 0 0 8px;
  font-size: 1.8rem;
  color: #1e293b;
}

.header p {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 20px;
}

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
}

.btn-login:hover {
  background: #4338ca;
}

.btn-login:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.error-msg {
  color: #dc2626;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 16px;
  background: #fef2f2;
  padding: 10px;
  border-radius: 8px;
}

.footer-text {
  margin-top: 20px;
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}

.footer-text a {
  color: #4f46e5;
  font-weight: 600;
  margin-left: 5px;
}
</style>
