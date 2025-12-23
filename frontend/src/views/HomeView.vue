<template>
  <div class="page-container">
    <!-- 3D 배경 (고정) -->
    <div class="spline-background">
      <SplineScene class="spline-canvas" />
    </div>

    <!-- 모든 컨텐츠 (3D 위에 표시) -->
    <div class="content-layer">
      <!-- 히어로 섹션 -->
      <section class="hero-section">
        <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
        <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>
        
        <div class="scroll-indicator">
          <span class="scroll-text">스크롤</span>
          <span class="scroll-arrow">↓</span>
        </div>
      </section>

      <!-- 검색창 고정 영역 -->
      <div class="fixed-search-bar">
        <div class="search-wrapper">
          <DrugSearch @search-start="handleSearch" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SplineScene from '@/components/SplineScene.vue'
import DrugSearch from '@/components/DrugSearch.vue'

const handleSearch = () => {
  // 검색 로직만 유지
  console.log('검색 시작')
}
</script>

<style scoped>
.page-container {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 3D 배경 (전체 화면 고정) */
.spline-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  /* 마우스 이벤트 활성화 */
  pointer-events: auto;
}

.spline-canvas {
  width: 100%;
  height: 100%;
  /* 마우스 이벤트 활성화 - 3D 씬이 마우스에 반응 */
  pointer-events: auto;
}

/* 모든 컨텐츠 레이어 (3D 위) */
.content-layer {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  /* 배경은 투명하게 하되, 자식 요소들은 클릭 가능하게 */
  pointer-events: none;
}

.content-layer > * {
  /* 자식 요소들은 다시 클릭 가능하게 */
  pointer-events: auto;
}

/* 히어로 섹션 */
.hero-section {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 24px;
  position: relative;
  /* 텍스트 영역은 마우스 이벤트 무시 (3D가 반응하도록) */
  pointer-events: none;
}

.hero-section > * {
  /* 텍스트 자체는 선택 가능하게 */
  pointer-events: auto;
}

.main-title {
  color: white;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  margin-bottom: 16px;
  text-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.6),
    0 2px 10px rgba(0, 0, 0, 0.4);
  letter-spacing: -0.02em;
  backdrop-filter: blur(2px);
}

.sub-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: clamp(1rem, 2vw, 1.25rem);
  margin-bottom: 2rem;
  text-shadow: 
    0 2px 15px rgba(0, 0, 0, 0.5),
    0 1px 5px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: white;
  opacity: 0.9;
  animation: bounce 2s infinite;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.scroll-text {
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.scroll-arrow {
  font-size: 1.5rem;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 검색창 고정 영역 */
.fixed-search-bar {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 1200px;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  padding: 20px 24px;
  border: none;
  /* 검색창은 반드시 클릭 가능하게 */
  pointer-events: auto;
}

.search-wrapper {
  width: 100%;
}

/* 반응형 */
@media (max-width: 768px) {
  .main-title {
    font-size: 2rem;
  }
  
  .sub-title {
    font-size: 1rem;
  }
  
  .fixed-search-bar {
    top: 60px;
    max-width: calc(100% - 32px);
    padding: 16px 20px;
    border-radius: 12px;
  }
  
  .scroll-indicator {
    bottom: 30px;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 1.75rem;
  }
  
  .sub-title {
    font-size: 0.95rem;
  }
  
  .fixed-search-bar {
    top: 50px;
    max-width: calc(100% - 24px);
    padding: 12px 16px;
  }
}

/* 접근성 */
@media (prefers-reduced-motion: reduce) {
  .scroll-indicator {
    animation: none;
  }
  
  * {
    transition: none !important;
    animation: none !important;
  }
}

/* 글라스모피즘 효과 강화 (선택사항) */
@supports (backdrop-filter: blur(20px)) {
  .fixed-search-bar {
    background: rgba(255, 255, 255, 0.90);
  }
}

/* Firefox 전용 */
@-moz-document url-prefix() {
  .fixed-search-bar {
    background: rgba(255, 255, 255, 0.98);
  }
}
</style>