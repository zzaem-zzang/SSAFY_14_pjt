<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username:</label>
        <input v-model="username" id="username" type="text" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input v-model="password" id="password" type="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();
const auth = useAuthStore();

const handleLogin = async () => {
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push({ name: 'PostList' })
  } catch (error) {
    errorMessage.value = 'Invalid username or password'
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.error {
  color: red;
}
</style>