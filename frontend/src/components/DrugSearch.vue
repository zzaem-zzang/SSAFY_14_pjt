<template>
  <section class="search-section">
    <div class="search-bar">
      <input
        v-model="keyword"
        placeholder="약 이름(예: 타이레놀)을 입력하세요"
        @keyup.enter="search"
      />
      <button @click="search" class="btn-search">검색</button>
    </div>

    <div v-if="loading" class="status-msg">
      <span class="spinner"></span> 검색 중입니다...
    </div>

    <div v-if="errorMessage" class="error-msg">
      ⚠️ {{ errorMessage }}
    </div>

    <div v-if="drugs.length" class="result-grid">
      <div
        class="drug-card"
        v-for="drug in drugs"
        :key="drug.id"
        @click="goDetail(drug.id)"
      >
        <div class="card-header">
          <h3>{{ drug.name }}</h3>
          <span class="badge" :class="drug.created ? 'new' : 'exist'">
            {{ drug.created ? '신규' : '정보' }}
          </span>
        </div>
        <p class="click-hint">자세히 보기 &rarr;</p>
      </div>
    </div>

    <div v-else-if="searched && !loading && !errorMessage" class="status-msg empty">
      검색 결과가 없습니다.
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')
const drugs = ref([])
const loading = ref(false)
const searched = ref(false)
const errorMessage = ref('')

const search = async () => {
  if (!keyword.value.trim()) return
  loading.value = true
  searched.value = true
  errorMessage.value = ''
  
  try {
    const res = await api.get(`/drugs/save/?name=${encodeURIComponent(keyword.value)}`)
    drugs.value = res.data.saved || []
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '검색 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => router.push(`/drugs/${id}`)
</script>

<style scoped>
.search-section { width: 100%; }

/* 검색창 스타일 */
.search-bar {
  display: flex;
  gap: 12px;
  background: white;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

input {
  flex: 1;
  border: none;
  font-size: 1rem;
  padding: 12px 16px;
  outline: none;
  border-radius: 12px;
}

.btn-search {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-search:hover { background: #4338ca; }

/* 결과 그리드 */
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 30px;
}

.drug-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.drug-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border-color: #4f46e5;
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
}
.badge.new { background: #dcfce7; color: #166534; }
.badge.exist { background: #f1f5f9; color: #475569; }

.click-hint {
  margin-top: 12px;
  font-size: 0.9rem;
  color: #4f46e5;
  font-weight: 500;
}

.status-msg {
  text-align: center;
  margin-top: 40px;
  color: #64748b;
}
.error-msg {
  margin-top: 20px;
  padding: 12px;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 8px;
  text-align: center;
}
</style>