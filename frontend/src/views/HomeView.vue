<template>
  <div class="page-container">
    <!-- 3D 배경 -->
    <div class="spline-background">
      <SplineScene class="spline-canvas" />
    </div>

    <!-- 컨텐츠 레이어 -->
    <div class="content-layer">
      <!-- 히어로 -->
      <section class="hero-section">
        <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
        <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>

        <div class="scroll-indicator">
          <span class="scroll-text">스크롤</span>
          <span class="scroll-arrow">↓</span>
        </div>
      </section>

      <!-- 검색창 -->
      <div class="fixed-search-bar">
        <DrugSearch />
      </div>

      <!-- 🔥 많이 찾아본 약 -->
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
            <span class="drug-name">{{ drug.name }}</span>
            <span class="arrow">→</span>
          </button>
        </div>
      </section>

      <hr class="divider" />

      <!-- 🗺️ 지도 -->
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

import SplineScene from '@/components/SplineScene.vue'
import DrugSearch from '@/components/DrugSearch.vue'
import MapView from '@/components/MapView.vue'

const router = useRouter()
const popularDrugs = ref([])
const popularLoading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/drugs/popular/views/')
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
/* ===== 전체 구조 ===== */
.page-container {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.spline-background {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.spline-canvas {
  width: 100%;
  height: 100%;
}

.content-layer {
  position: relative;
  z-index: 1;
}

/* ===== 히어로 ===== */
.hero-section {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
}

.main-title {
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 800;
  margin-bottom: 16px;
}

.sub-title {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* ===== 검색바 ===== */
.fixed-search-bar {
  position: sticky;
  top: 20px;
  margin: -60px auto 0;
  max-width: 900px;
  padding: 20px;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

/* ===== 인기 약 ===== */
.popular-container {
  max-width: 900px;
  margin: 80px auto;
  padding: 0 20px;
}

.drug-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (min-width: 768px) {
  .drug-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.drug-item {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  cursor: pointer;
}

.drug-item:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
}

.divider {
  margin: 80px auto;
  max-width: 900px;
  height: 1px;
  background: #e2e8f0;
  border: none;
}

/* ===== 지도 ===== */
.map-section {
  max-width: 900px;
  margin: 0 auto 120px;
  padding: 0 20px;
}

.map-card {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

/* ===== 로딩 ===== */
.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #eee;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 40px auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
