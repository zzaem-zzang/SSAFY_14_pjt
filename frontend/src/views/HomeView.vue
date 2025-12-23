<template>
  <div class="container">
    <div class="home-wrapper">
      <header class="hero-section">
        <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
        <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>
      </header>

      <DrugSearch />

      <section class="popular-container">
        <div class="popular-header">
          <span class="fire-icon">🔥</span>
          <h2 class="section-label">많이 찾아본 약</h2>
        </div>

        <div v-if="popularLoading" class="loading-state">
          <div class="spinner"></div>
        </div>

        <div v-else class="drug-grid">
          <button 
            v-for="drug in popularDrugs" 
            :key="drug.id" 
            class="drug-item" 
            @click="goDetail(drug.id)"
          >
            <div class="drug-info">
              <span class="drug-name">{{ drug.name }}</span>
            </div>
            <span class="arrow">→</span>
          </button>
        </div>
      </section>

      <hr class="divider" />

      <section class="map-section">
        <h2 class="section-title">내 주변 약국 지도</h2>
        <div class="map-card">
          <MapView />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import DrugSearch from '@/components/DrugSearch.vue'
import MapView from '@/components/MapView.vue'

const router = useRouter()
const popularDrugs = ref([])
const popularLoading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/drugs/popular/views/')
    // 8개로 제한하여 2행 4열(PC) 또는 4행 2열(모바일)로 칸을 딱 맞춤
    popularDrugs.value = res.data.slice(0, 8) 
  } catch (e) {
    console.error('인기 약 로딩 실패:', e)
  } finally {
    popularLoading.value = false
  }
})

const goDetail = (id) => {
  router.push(`/drugs/${id}`)
}
</script>

<style scoped>
/* 전체 레이아웃 정렬 */
.container {
  width: 100%;
  background-color: #f8fafc; /* 연한 배경색으로 요소 구분감 강화 */
  min-height: 100vh;
}

.home-wrapper {
  max-width: 900px; /* 칸 맞춤을 위해 폭을 소폭 조정 */
  margin: 0 auto;
  padding: 60px 20px 100px;
}

.hero-section {
  text-align: center;
  margin-bottom: 48px;
}

.main-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

/* 🔥 그리드 시스템: 칸을 일정하게 유지 */
.drug-grid {
  display: grid;
  /* 가로 너비를 동일하게 1:1 비율로 나눔 */
  grid-template-columns: repeat(2, 1fr); 
  gap: 16px;
}

/* 태블릿/PC 환경에서는 4열로 정렬 */
@media (min-width: 768px) {
  .drug-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.drug-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  
  /* 핵심: 고정 높이를 주어 이름 길이에 상관없이 칸 높이를 통일 */
  min-height: 72px; 
  height: 100%;
}

.drug-info {
  flex: 1;
  display: flex;
  align-items: center;
  margin-right: 8px;
  overflow: hidden;
}

.drug-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  line-height: 1.4;
  text-align: left;

  /* 핵심: 2줄까지만 보여주고 그 이상은 ... 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}

.arrow {
  flex-shrink: 0;
  font-size: 0.9rem;
  color: #cbd5e1;
}

.drug-item:hover {
  border-color: #3b82f6;
  background-color: #ffffff;
  transform: translateY(-3px);
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
}

.drug-item:hover .drug-name { color: #3b82f6; }
.drug-item:hover .arrow { color: #3b82f6; }

/* 나머지 요소 정렬 */
.popular-container { margin-top: 48px; }
.popular-header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.section-label { font-size: 1.15rem; font-weight: 700; color: #1e293b; }

.divider {
  border: none;
  height: 1px;
  background-color: #e2e8f0;
  margin: 64px 0;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: #1e293b;
}

.map-card {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 40px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>