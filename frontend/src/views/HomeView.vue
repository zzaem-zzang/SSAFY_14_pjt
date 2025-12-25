<template>
  <div class="page-container">
    <!-- 3D 배경 -->
    <div class="spline-background">
      <SplineScene class="spline-canvas" />
    </div>

    <!-- 컨텐츠 레이어 -->
    <div class="content-layer">
      <!-- 히어로 + 검색창 통합 섹션 -->
      <section class="hero-section">
        <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
        <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>

        <!-- 검색창 -->
        <div class="search-container">
          <DrugSearch />
        </div>

       
    
        <!-- 스크롤 인디케이터 -->
        <div class="scroll-indicator" @click="smoothScrollToContent">
          <span class="scroll-text">인기 약품 보기</span>
          <span class="scroll-arrow">↓</span>
        </div>
      </section>

      <!-- 컨텐츠 영역 -->
      <div ref="contentRef" class="content-sections">
        <!-- 🔥 많이 찾아본 약 -->
        <section class="popular-container">
          <div class="popular-header">
            <span class="fire-icon">🔥 최근</span>
            <h2 class="section-label">많이 찾아본 약</h2>
            <span class="info-tooltip" title="사람들이 가장 많이 검색된 의약품입니다">ⓘ</span>
          </div>

          <div v-if="popularLoading" class="loading-state">
            <div class="spinner"></div>
            <p class="loading-text">인기 약품을 불러오는 중...</p>
          </div>

          <div v-else-if="popularDrugs.length === 0" class="empty-state">
            <p>아직 데이터가 없습니다</p>
          </div>

          <div v-else class="drug-grid">
            <button
              v-for="(drug, index) in popularDrugs"
              :key="drug.id"
              class="drug-item"
              @click="goDetail(drug.id)"
              :style="{ animationDelay: `${index * 0.05}s` }"
            >
              <div class="drug-content">
                <span class="drug-rank">{{ index + 1 }}</span>
                <span class="drug-name">{{ drug.name }}</span>
              </div>
              <span class="arrow">→</span>
            </button>
          </div>
 <div class="hero-disclaimer">
          <p>
            ⓘ 본 서비스는 사용자의 증상 입력을 기반으로 관련 의약품 정보와 요약 콘텐츠를 추천하는 서비스입니다.<br>
          &ensp; &ensp;의료적 판단이나 처방이 아닌, <strong>의사결정을 돕기 위한 정보 추천</strong>에 목적이 있습니다.
          </p>
        </div>
          
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

import SplineScene from '@/components/SplineScene.vue'
import DrugSearch from '@/components/DrugSearch.vue'

const router = useRouter()
const popularDrugs = ref([])
const popularLoading = ref(true)
const contentRef = ref(null)


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

const smoothScrollToContent = () => {
  contentRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const searchByCategory = (keyword) => {
  router.push(`/drugs?search=${keyword}`)
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

/* ===== 히어로 섹션 (검색창 포함) ===== */
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
  padding: 60px 20px;
}
/* ✅ 서비스 고지 문구 스타일 (중앙 정렬 버전) */
.hero-disclaimer {
  width: 100%;             /* 전체 너비 확보 */
  max-width: 800px;        /* 너무 퍼지지 않게 제한 */
  margin: 40px auto 20px;  /* 위아래 여유 및 가로 중앙 정렬(auto) */
  padding: 0 20px;
  text-align: center;      /* 텍스트 내부 중앙 정렬 */
  color: #6b7280;          /* 밝은 배경에서 잘 보이도록 회색계열로 변경 */
  font-size: 0.9rem;
  line-height: 1.6;
  font-weight: 400;
  clear: both;             /* 주변 요소 간섭 방지 */
}

.hero-disclaimer strong {
  font-weight: 700;
  color: #1f2937;          /* 강조 문구는 진하게 */
}

/* 모바일 대응 */
@media (max-width: 640px) {
  .hero-disclaimer {
    font-size: 0.8rem;
    margin-top: 30px;
  }
  .hero-disclaimer br {
    display: none;         /* 모바일은 공간 협소로 줄바꿈 제거 */
  }
}
.main-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  margin-bottom: 20px;
  text-shadow: 0 4px 12px rgba(0,0,0,0.3);
  letter-spacing: -0.02em;
}

.sub-title {
  font-size: clamp(1rem, 2vw, 1.3rem);
  opacity: 0.95;
  margin-bottom: 48px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
  font-weight: 400;
}

/* ===== 검색창 (히어로 내부) ===== */
.search-container {
  width: 100%;
  max-width: 800px;
  padding: 0 20px;
  margin-bottom: 60px;
  animation: fadeInUp 0.8s ease-out 0.3s backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 검색창 스타일 오버라이드 */
.search-container :deep(.search-wrapper) {
  background: rgba(255,255,255,0.98);
  border-radius: 24px;
  padding: 24px 28px;
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  border: 1px solid rgba(255,255,255,0.9);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-container :deep(.search-wrapper):hover,
.search-container :deep(.search-wrapper):focus-within {
  box-shadow: 0 24px 80px rgba(0,0,0,0.3);
  transform: translateY(-4px);
  border-color: #3b82f6;
}

/* 스크롤 인디케이터 */
.scroll-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.8;
  margin-top: auto;
  padding-bottom: 40px;
}

.scroll-indicator:hover {
  transform: translateY(5px);
  opacity: 1;
}

.scroll-text {
  font-size: 0.95rem;
  font-weight: 500;
}

.scroll-arrow {
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(10px); }
}

/* ===== 컨텐츠 영역 ===== */
.content-sections {
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 10%, white 20%);
  padding-top: 60px;
  padding-bottom: 0.2rem;
}

/* ===== 인기 약 ===== */
.popular-container {
  max-width: 1100px;
  margin: 0 auto 80px;
  padding: 0 20px;
}

.popular-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.fire-icon {
  color: red;
  font-size: 1.8rem;
  animation: fire 1.5s ease-in-out infinite;
}

@keyframes fire {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.section-label {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
}

.info-tooltip {
  font-size: 1rem;
  color: #6b7280;
  cursor: help;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.info-tooltip:hover {
  opacity: 1;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
}

.loading-text {
  margin-top: 20px;
  color: #6b7280;
  font-size: 1rem;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #9ca3af;
  font-size: 1.1rem;
}

.drug-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (min-width: 768px) {
  .drug-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }
}

/* 약 카드 디자인 */
.drug-item {
  background: white;
  border-radius: 18px;
  padding: 20px;
  border: 2px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideIn 0.5s ease-out backwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drug-item:hover {
  border-color: #3b82f6;
  background: #f8faff;
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.15);
}

.drug-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drug-rank {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.drug-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
}

.arrow {
  color: #94a3b8;
  font-size: 1.3rem;
  transition: transform 0.3s ease;
}

.drug-item:hover .arrow {
  transform: translateX(4px);
  color: #3b82f6;
}

/* 더보기 버튼 */
.show-more-btn {
  width: 100%;
  margin-top: 28px;
  padding: 18px;
  background: linear-gradient(135deg, #f8faff 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 18px;
  color: #475569;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.show-more-btn:hover {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: #3b82f6;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

/* 빠른 카테고리 */
.quick-categories {
  max-width: 1100px;
  margin: 0 auto 120px;
  padding: 0 20px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 32px;
}

@media (min-width: 768px) {
  .category-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
}

.category-card {
  background: white;
  border-radius: 24px;
  padding: 32px 24px;
  border: 2px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.category-card:hover {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
  transform: translateY(-8px);
  box-shadow: 0 16px 40px rgba(59, 130, 246, 0.15);
}

.category-icon {
  font-size: 3rem;
  transition: transform 0.3s ease;
}

.category-card:hover .category-icon {
  transform: scale(1.2);
}

.category-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.05rem;
}

/* 로딩 스피너 */
.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 반응형 */
@media (max-width: 640px) {
  .hero-section {
    padding: 40px 20px;
  }

  .main-title {
    margin-bottom: 16px;
  }

  .sub-title {
    margin-bottom: 36px;
  }

  .search-container {
    margin-bottom: 40px;
  }

  .drug-name {
    font-size: 0.9rem;
  }
  
  .section-label {
    font-size: 1.4rem;
  }
  
  .category-card {
    padding: 24px 20px;
  }
  
  .category-icon {
    font-size: 2.5rem;
  }
}



</style>