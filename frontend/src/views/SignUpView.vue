<template>
  <div class="signup-wrapper">
    <div class="signup-card">
      <div class="header">
        <h1>회원가입 📝</h1>
        <p>서비스 이용을 위해 계정을 생성해주세요.</p>
      </div>

      <form @submit.prevent="signup" class="signup-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input 
            v-model="username" 
            id="username" 
            placeholder="사용하실 아이디를 입력하세요" 
            required
          />
        </div>

        <div class="form-group">
          <label for="email">이메일 <span class="optional">(선택)</span></label>
          <input 
            v-model="email" 
            id="email" 
            type="email" 
            placeholder="example@email.com" 
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

        <div v-if="error" class="error-msg">
          ⚠️ {{ error }}
        </div>

        <button type="submit" class="btn-signup" :disabled="isLoading">
          {{ isLoading ? '가입 처리 중...' : '회원가입' }}
        </button>
      </form>

      <div class="login-link">
        이미 계정이 있으신가요? 
        <router-link to="/login">로그인하기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const signup = async () => {
  // 유효성 검사 (간단한 예시)
  if (!username.value || !password.value) {
    error.value = '아이디와 비밀번호는 필수입니다.'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // 💡 참고: 실제 배포 환경에서는 도메인을 환경변수로 관리하는 것이 좋습니다.
    await axios.post('http://127.0.0.1:8000/api/auth/register/', {
      username: username.value,
      password: password.value,
      email: email.value,
    })
    
    alert('회원가입이 완료되었습니다! 로그인해주세요.')
    router.push('/login') // 로그인 페이지 경로가 '/login'이라고 가정
  } catch (err) {
    // 서버에서 보내주는 에러 메시지가 있다면 표시, 없다면 기본 메시지
    error.value = err.response?.data?.detail || '회원가입에 실패했습니다. 다시 시도해주세요.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 전체 화면 중앙 정렬 */
.signup-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

/* 카드 스타일 */
.signup-card {
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}

/* 헤더 영역 */
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

/* 폼 스타일 */
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

.optional {
  font-weight: 400;
  color: #94a3b8;
  font-size: 0.8rem;
}

input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
  background: #fff;
}

input:focus {
  border-color: #4f46e5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* 버튼 스타일 */
.btn-signup {
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
  transition: background 0.2s, transform 0.1s;
}

.btn-signup:hover {
  background: #4338ca;
}

.btn-signup:active {
  transform: scale(0.98);
}

.btn-signup:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

/* 에러 메시지 */
.error-msg {
  color: #dc2626;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 16px;
  background: #fef2f2;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #fee2e2;
}

/* 하단 링크 */
.login-link {
  margin-top: 24px;
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}

.login-link a {
  color: #4f46e5;
  font-weight: 600;
  text-decoration: underline;
  margin-left: 5px;
}

.login-link a:hover {
  color: #4338ca;
}
</style>