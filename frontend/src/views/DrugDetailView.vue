<template>
  <div class="detail-wrapper">
    <div v-if="loading" class="info">불러오는 중...</div>

    <div v-else-if="error" class="info error">
      존재하지 않는 의약품입니다.
      <button @click="goHome">홈으로</button>
    </div>

    <!-- 💊 상세 카드 -->
    <div v-else class="drug-card">
      <h1 class="title">💊 {{ drug.name }}</h1>

      <section>
        <h3>📌 효능</h3>
        <p>{{ drug.effect || '정보 없음' }}</p>
      </section>

      <section>
        <h3>📖 복용 방법</h3>
        <p>{{ drug.usage || '정보 없음' }}</p>
      </section>

      <section>
        <h3>⚠️ 주의사항</h3>
        <p>{{ drug.warning || '정보 없음' }}</p>
      </section>

      <button class="back-btn" @click="goHome">
        ← 검색으로 돌아가기
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const drug = ref(null)
const loading = ref(true)
const error = ref(false)

onMounted(async () => {
  try {
    const res = await api.get(`/drugs/${route.params.id}/`)
    drug.value = res.data
  } catch (err) {
    console.error('상세 조회 실패', err)
    error.value = true
  } finally {
    loading.value = false
  }
})

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.detail-wrapper {
  display: flex;
  justify-content: center;
  padding: 40px 16px;
}

/* 카드 */
.drug-card {
  max-width: 600px;
  width: 100%;
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

/* 제목 */
.title {
  margin-bottom: 20px;
  font-size: 24px;
}

/* 섹션 */
section {
  margin-bottom: 20px;
}

section h3 {
  margin-bottom: 8px;
  font-size: 16px;
  color: #4f46e5;
}

section p {
  line-height: 1.6;
  white-space: pre-line; /* 줄바꿈 유지 */
}

/* 버튼 */
.back-btn {
  margin-top: 24px;
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: none;
  background: #4f46e5;
  color: white;
  font-size: 15px;
  cursor: pointer;
}

.back-btn:hover {
  background: #4338ca;
}

/* 안내 */
.info {
  font-size: 16px;
  color: #666;
}

.info.error {
  color: #dc2626;
}

.info button {
  margin-top: 12px;
  padding: 8px 12px;
}
</style>
