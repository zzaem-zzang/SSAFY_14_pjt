<template>
  <div>
    <h1>의약품 검색</h1>

    <!-- 🔍 약 검색 -->
    <DrugSearch />

    <!-- ⭐ 증상 기반 추천 -->
    <SymptomRecommend />
  </div>
</template>

<script setup>
import DrugSearch from '@/components/DrugSearch.vue'
import SymptomRecommend from '@/components/SymptomRecommend.vue'
</script>
