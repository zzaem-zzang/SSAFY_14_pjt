<template>
  <div class="detail-container">
    <div v-if="loading" class="loading">정보를 불러오고 있습니다...</div>

    <div v-else-if="error" class="error-view">
      <h3>존재하지 않는 의약품입니다.</h3>
      <button @click="goHome">홈으로 돌아가기</button>
    </div>

    <div v-else class="info-card">
      <div class="card-header">
        <span class="category">의약품 상세정보</span>
        <h1 class="drug-title">{{ drug.name }}</h1>
      </div>

      <div class="card-body">
        <section class="info-section">
          <h3>📌 효능 및 효과</h3>
          <p>{{ drug.effect || '정보 없음' }}</p>
        </section>

        <section class="info-section">
          <h3>📖 용법 및 용량</h3>
          <p>{{ drug.usage || '정보 없음' }}</p>
        </section>

        <section class="info-section warning">
          <h3>⚠️ 주의사항</h3>
          <p>{{ drug.warning || '정보 없음' }}</p>
        </section>
      </div>

      <div class="card-footer">
        <button class="back-btn" @click="goHome">목록으로</button>
      </div>
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
    error.value = true
  } finally {
    loading.value = false
  }
})

const goHome = () => router.push('/')
</script>

<style scoped>
.detail-container {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}

.info-card {
  width: 100%;
  max-width: 700px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  padding: 40px 30px;
}

.category {
  font-size: 0.9rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.drug-title {
  margin: 10px 0 0 0;
  font-size: 2rem;
  font-weight: 800;
}

.card-body { padding: 30px; }

.info-section { margin-bottom: 30px; }
.info-section h3 {
  color: #4f46e5;
  font-size: 1.1rem;
  margin-bottom: 10px;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 8px;
  display: inline-block;
}

.info-section p {
  line-height: 1.7;
  color: #475569;
  white-space: pre-line;
}

.info-section.warning h3 { color: #dc2626; }
.info-section.warning p { background: #fef2f2; padding: 15px; border-radius: 8px; color: #991b1b; }

.card-footer {
  padding: 20px 30px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  text-align: right;
}

.back-btn {
  padding: 10px 20px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  font-weight: 600;
}
.back-btn:hover { background: #f1f5f9; color: #334155; }

.loading, .error-view { text-align: center; margin-top: 50px; color: #64748b; }
</style>