<template>
  <div class="pharmacy-map-page">
    <div class="spline-background">
      <canvas id="canvas3d"></canvas>
    </div>

    <div class="content-layer">
      <div class="page-header">
        <h1 class="page-title">내 주변 약국 찾기</h1>
        <p class="page-subtitle">현재 위치 기반으로 가까운 약국을 찾아드립니다</p>
      </div>

      <div class="map-wrapper">
        <MapView />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { Application } from '@splinetool/runtime'
import MapView from '@/components/MapView.vue'

let spline = null

onMounted(async () => {
  const canvas = document.getElementById('canvas3d')
  if (!canvas) return

  spline = new Application(canvas)

  try {
    await spline.load('https://prod.spline.design/MSKA16NwDXxn-LI2/scene.splinecode')
    console.log('Spline scene loaded')

    // 씬 로드 후 특정 오브젝트 접근 예시
  } catch (err) {
    console.error('Spline 로드 실패:', err)
  }
})

onUnmounted(() => {
  if (spline) {
    spline.dispose() // 내부 루프 및 리소스 정리
    spline = null
  }
})
</script>

<style scoped>
.pharmacy-map-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
}

/* 3D 배경: 화면 전체에 고정 */
.spline-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0; /* 가장 뒤로 */
}

#canvas3d {
  width: 100%;
  height: 100%;
  display: block;
}

/* 콘텐츠 레이어: 3D 모델 위로 올림 */
.content-layer {
  position: relative;
  z-index: 1;
  padding: 60px 20px;
  pointer-events: none; /* 배경의 3D 모델 조작을 위해 레이어 자체는 통과 */
}

.page-header, .map-wrapper {
  pointer-events: auto; /* 실제 클릭이 필요한 요소들만 다시 활성화 */
}

.page-header {
  max-width: 1000px;
  margin: 0 auto 40px;
  text-align: center;
}

.page-title {
  font-size: 2.8rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 12px;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.5);
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  font-weight: 500;
}

.map-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* 반응형 모바일 */
@media (max-width: 768px) {
  .page-title { font-size: 2rem; }
  .content-layer { padding: 40px 16px; }
}
</style>
