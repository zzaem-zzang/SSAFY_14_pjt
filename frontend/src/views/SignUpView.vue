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
            @blur="validateUsername"
            id="username"
            type="text"
            placeholder="4~20자, 영문으로 시작"
            required
          />
          <div v-if="errors.username" class="field-error">
            {{ errors.username }}
          </div>
          <div v-else-if="validations.username" class="field-success">
            ✓ 사용 가능한 아이디입니다
          </div>
        </div>

        <!-- 닉네임 -->
        <div class="form-group">
          <label for="nickname">닉네임</label>
          <input
            v-model="nickname"
            @blur="validateNickname"
            id="nickname"
            type="text"
            placeholder="2~15자, 한글/영문/숫자"
            required
          />
          <div v-if="errors.nickname" class="field-error">
            {{ errors.nickname }}
          </div>
          <div v-else-if="validations.nickname" class="field-success">
            ✓ 사용 가능한 닉네임입니다
          </div>
        </div>

        <!-- 비밀번호 -->
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            v-model="password"
            @input="validatePassword"
            id="password"
            type="password"
            placeholder="8자 이상, 영문/숫자/특수문자"
            required
          />
          <!-- 비밀번호 강도 바 -->
          <div class="password-strength">
            <div 
              class="strength-bar" 
              :class="passwordStrengthClass"
              :style="{ width: passwordStrength + '%' }"
            ></div>
          </div>
          <div v-if="errors.password" class="field-error">
            {{ errors.password }}
          </div>
        </div>

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input
            v-model="passwordConfirm"
            @input="validatePasswordConfirm"
            id="passwordConfirm"
            type="password"
            placeholder="비밀번호를 다시 입력하세요"
            required
          />
          <div v-if="errors.passwordConfirm" class="field-error">
            {{ errors.passwordConfirm }}
          </div>
          <div v-else-if="passwordConfirm && password === passwordConfirm" class="field-success">
            ✓ 비밀번호가 일치합니다
          </div>
        </div>

        <!-- 서버 에러 -->
        <div v-if="errorMessage" class="error-msg">
          ⚠️ {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="btn-login"
          :disabled="isLoading || !isFormValid"
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const username = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const errors = ref({
  username: '',
  nickname: '',
  password: '',
  passwordConfirm: ''
})

const validations = ref({
  username: false,
  nickname: false,
  password: false,
  passwordConfirm: false
})

// 아이디 검증
const validateUsername = () => {
  const value = username.value.trim()
  
  if (!value) {
    errors.value.username = '아이디를 입력하세요'
    validations.value.username = false
    return false
  }
  
  if (value.length < 4) {
    errors.value.username = '아이디는 최소 4자 이상이어야 합니다'
    validations.value.username = false
    return false
  }
  
  if (value.length > 20) {
    errors.value.username = '아이디는 최대 20자까지 가능합니다'
    validations.value.username = false
    return false
  }
  
  if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(value)) {
    errors.value.username = '아이디는 영문으로 시작하고 영문, 숫자만 사용 가능합니다'
    validations.value.username = false
    return false
  }
  
  errors.value.username = ''
  validations.value.username = true
  return true
}

// 닉네임 검증
const validateNickname = () => {
  const value = nickname.value.trim()
  
  if (!value) {
    errors.value.nickname = '닉네임을 입력하세요'
    validations.value.nickname = false
    return false
  }
  
  if (value.length < 2) {
    errors.value.nickname = '닉네임은 최소 2자 이상이어야 합니다'
    validations.value.nickname = false
    return false
  }
  
  if (value.length > 15) {
    errors.value.nickname = '닉네임은 최대 15자까지 가능합니다'
    validations.value.nickname = false
    return false
  }
  
  if (!/^[가-힣a-zA-Z0-9]+$/.test(value)) {
    errors.value.nickname = '닉네임은 한글, 영문, 숫자만 사용 가능합니다'
    validations.value.nickname = false
    return false
  }
  
  errors.value.nickname = ''
  validations.value.nickname = true
  return true
}

// 비밀번호 강도 계산
const passwordStrength = computed(() => {
  const pass = password.value
  if (!pass) return 0
  
  let strength = 0
  if (pass.length >= 8) strength += 25
  if (/[a-zA-Z]/.test(pass)) strength += 25
  if (/\d/.test(pass)) strength += 25
  if (/[!@#$%^&*(),.?":{}|<>]/.test(pass)) strength += 25
  
  return strength
})

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength < 50) return 'weak'
  if (strength < 75) return 'medium'
  return 'strong'
})

// 비밀번호 검증
const validatePassword = () => {
  const value = password.value
  
  if (!value) {
    errors.value.password = '비밀번호를 입력하세요'
    validations.value.password = false
    return false
  }
  
  if (value.length < 8) {
    errors.value.password = '비밀번호는 최소 8자 이상이어야 합니다'
    validations.value.password = false
    return false
  }
  
  if (!/[a-zA-Z]/.test(value)) {
    errors.value.password = '비밀번호에 영문자가 포함되어야 합니다'
    validations.value.password = false
    return false
  }
  
  if (!/\d/.test(value)) {
    errors.value.password = '비밀번호에 숫자가 포함되어야 합니다'
    validations.value.password = false
    return false
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
    errors.value.password = '비밀번호에 특수문자가 포함되어야 합니다'
    validations.value.password = false
    return false
  }
  
  errors.value.password = ''
  validations.value.password = true
  return true
}

// 비밀번호 확인 검증
const validatePasswordConfirm = () => {
  if (!passwordConfirm.value) {
    errors.value.passwordConfirm = '비밀번호 확인을 입력하세요'
    validations.value.passwordConfirm = false
    return false
  }
  
  if (password.value !== passwordConfirm.value) {
    errors.value.passwordConfirm = '비밀번호가 일치하지 않습니다'
    validations.value.passwordConfirm = false
    return false
  }
  
  errors.value.passwordConfirm = ''
  validations.value.passwordConfirm = true
  return true
}

// 폼 전체 유효성
const isFormValid = computed(() => {
  return (
    username.value &&
    nickname.value &&
    password.value &&
    passwordConfirm.value &&
    validations.value.username &&
    validations.value.nickname &&
    validations.value.password &&
    validations.value.passwordConfirm
  )
})

const handleSignUp = async () => {
  errorMessage.value = ''

  // 모든 필드 검증
  const usernameValid = validateUsername()
  const nicknameValid = validateNickname()
  const passwordValid = validatePassword()
  const passwordConfirmValid = validatePasswordConfirm()

  if (!usernameValid || !nicknameValid || !passwordValid || !passwordConfirmValid) {
    return
  }

  isLoading.value = true

  try {
    await api.post('/auth/register/', {
      username: username.value.trim(),
      nickname: nickname.value.trim(),
      password: password.value,
      password_confirm: passwordConfirm.value,
    })

    alert('회원가입이 완료되었습니다! 로그인해주세요.')
    router.push('/login')

  } catch (err) {
    console.error('회원가입 에러:', err)
    const data = err.response?.data

    // 서버에서 온 에러 메시지 처리
    if (data?.username) {
      errors.value.username = Array.isArray(data.username) ? data.username[0] : data.username
    }
    if (data?.nickname) {
      errors.value.nickname = Array.isArray(data.nickname) ? data.nickname[0] : data.nickname
    }
    if (data?.password) {
      errors.value.password = Array.isArray(data.password) ? data.password[0] : data.password
    }
    if (data?.password_confirm) {
      errors.value.passwordConfirm = Array.isArray(data.password_confirm) 
        ? data.password_confirm[0] 
        : data.password_confirm
    }
    
    // 일반 에러 메시지
    if (data?.detail) {
      errorMessage.value = data.detail
    } else if (!data?.username && !data?.nickname && !data?.password && !data?.password_confirm) {
      errorMessage.value = '회원가입에 실패했습니다. 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
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

/* 필드별 에러 메시지 */
.field-error {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 6px;
}

.field-success {
  color: #10b981;
  font-size: 0.85rem;
  margin-top: 6px;
}

/* 비밀번호 강도 표시 */
.password-strength {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: all 0.3s;
}

.strength-bar.weak {
  background: #dc2626;
}

.strength-bar.medium {
  background: #f59e0b;
}

.strength-bar.strong {
  background: #10b981;
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
  transition: all 0.2s;
}

.btn-login:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-1px);
}

.btn-login:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

.error-msg {
  color: #dc2626;
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 16px;
  background: #fef2f2;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #fecaca;
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
  text-decoration: none;
}

.footer-text a:hover {
  text-decoration: underline;
}
</style>