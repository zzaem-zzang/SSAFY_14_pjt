<template>
  <div class="home-wrapper">
    <div class="hero-section">
      <h1 class="main-title">어떤 약을 찾고 계신가요?</h1>
      <p class="sub-title">증상을 검색하거나 의약품 이름을 입력해보세요.</p>
    </div>

    <DrugSearch />
  </div>
</template>

<script setup>
import DrugSearch from '@/components/DrugSearch.vue'
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