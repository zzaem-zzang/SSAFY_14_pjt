<template>
  <div class="pharmacy-map-page">
    <div class="page-header">
      <h1 class="page-title">내 주변 약국 찾기</h1>
      <p class="page-subtitle">현재 위치 기반으로 가까운 약국을 찾아드립니다</p>
    </div>

    <div class="map-wrapper">
      <MapView />
    </div>
  </div>
</template>

<script setup>
import MapView from '@/components/MapView.vue'
</script>

<style scoped>
.pharmacy-map-page {
  min-height: calc(100vh - 60px);
  padding: 40px 20px;
  background: #f8fafc;
}

.page-header {
  max-width: 1000px;
  margin: 0 auto 32px;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  font-weight: 500;
}

.map-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 반응형 */
@media (max-width: 768px) {
  .pharmacy-map-page {
    padding: 30px 16px;
  }

  .page-header {
    margin-bottom: 24px;
  }

  .page-title {
    font-size: 2rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .map-wrapper {
    padding: 20px;
    border-radius: 12px;
  }
}

@media (max-width: 480px) {
  .pharmacy-map-page {
    padding: 20px 12px;
  }

  .page-title {
    font-size: 1.75rem;
    margin-bottom: 8px;
  }

  .page-subtitle {
    font-size: 0.95rem;
  }

  .map-wrapper {
    padding: 16px;
  }
}
</style>