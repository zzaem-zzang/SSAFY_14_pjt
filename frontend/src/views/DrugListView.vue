<template>
  <section>
    <!-- ⭐ 정렬 선택 바 -->
    <div class="sort-bar">
      <button :class="{ active: order === 'default' }" @click="setOrder('default')">
        기본순
      </button>
      <button :class="{ active: order === 'helpful' }" @click="setOrder('helpful')">
        도움순
      </button>
      <button :class="{ active: order === 'rating' }" @click="setOrder('rating')">
        평점순
      </button>
    </div>

    <!-- 약 목록 -->
    <div class="result-grid">
      <div v-for="drug in drugs" :key="drug.id" class="drug-card">
        <!-- 1️⃣ 약 이름 -->
        <h3>{{ drug.name }}</h3>

        <!-- 2️⃣ 도움 비율 + 평점 -->
        <div class="drug-meta">
          <div class="ratio">
            👍 {{ drug.helpful_ratio?.toFixed(0) || 0 }}%
            <span class="sub">
              ({{ drug.helpful_count }}명 중 도움됨)
            </span>
          </div>

          <div class="rating">
            ⭐ {{ drug.avg_rating?.toFixed(1) || '평점 없음' }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>



<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const drugs = ref([])
const order = ref('default')

const fetchDrugs = async () => {
  const params = {}
  if (order.value !== 'default') {
    params.order = order.value
  }

  const res = await api.get('/drugs/', { params })
  drugs.value = res.data
}

const setOrder = (value) => {
  order.value = value
  fetchDrugs()
}

onMounted(fetchDrugs)
</script>


<style scoped>
.sort-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.sort-bar button {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
}

.sort-bar button.active {
  background: #4f46e5;
  color: white;
}

.drug-meta {
  margin-top: 8px;
  font-size: 0.9rem;
}

.ratio {
  color: #16a34a;
  font-weight: 600;
}

.sub {
  font-size: 0.75rem;
  color: #64748b;
}
</style>