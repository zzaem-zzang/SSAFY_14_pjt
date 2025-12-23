<template>
  <div class="container">
    <div class="home-wrapper">
      <div class="hero-section">
        <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
        <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>
      </div>

      <DrugSearch />
      <hr class="divider" />
      <SymptomRecommend />
    </div>

    <section style="max-width: 800px; margin: 24px auto; padding: 0 20px;">
      <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">
        내 주변 약국 지도
      </h3>
      <MapView />
    </section>
  </div>
</template>

<script setup>
import DrugSearch from '@/components/DrugSearch.vue'
import SymptomRecommend from '@/components/SymptomRecommend.vue'
import MapView from '@/components/MapView.vue'  // 경로 확인!
</script>

<style scoped>
.home-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  margin-bottom: 40px;
}

.main-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 10px;
}

.sub-title {
  color: #64748b;
  font-size: 1.1rem;
}

.divider {
  border: none;
  height: 1px;
  background: #e2e8f0;
  margin: 60px 0;
}
</style>