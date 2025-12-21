<template>
  <div class="recommend-section">
    <h2>🩺 증상으로 약 찾기</h2>
    <p class="desc">현재 겪고 계신 증상을 선택해주세요.</p>

    <div class="symptom-chips">
      <button
        v-for="symptom in symptoms"
        :key="symptom.id"
        class="chip"
        :class="{ active: selectedSymptom === symptom.id }"
        @click="selectAndFetch(symptom.id)"
      >
        {{ symptom.name }}
      </button>
    </div>

    <div v-if="drugs.length" class="recommend-results">
      <h3>추천 의약품 ({{ drugs.length }})</h3>
      <ul class="drug-list">
        <li v-for="drug in drugs" :key="drug.id" @click="goDetail(drug.id)">
          <div class="drug-info">
            <span class="drug-name">{{ drug.name }}</span>
          </div>
          <span class="arrow">👉</span>
        </li>
      </ul>
    </div>
    
    <div v-else-if="selectedSymptom && drugs.length === 0" class="empty-msg">
      해당 증상에 대한 추천 약이 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const symptoms = ref([])
const selectedSymptom = ref('')
const drugs = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/symptoms/')
    symptoms.value = res.data
  } catch (err) {
    console.error('증상 로드 실패', err)
  }
})

const selectAndFetch = async (id) => {
  if (selectedSymptom.value === id) return // 이미 선택됨
  selectedSymptom.value = id
  
  try {
    const res = await api.get(`/recommend/symptom/?symptom=${id}`)
    drugs.value = res.data.recommendations
  } catch (err) {
    drugs.value = []
  }
}

const goDetail = (id) => router.push(`/drugs/${id}`)
</script>

<style scoped>
.recommend-section { margin-top: 20px; }

h2 { font-size: 1.5rem; margin-bottom: 8px; color: #1e293b; }
.desc { color: #64748b; margin-bottom: 24px; }

/* 칩 스타일 */
.symptom-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
}

.chip {
  padding: 10px 20px;
  border-radius: 50px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chip:hover { border-color: #4f46e5; color: #4f46e5; }
.chip.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* 추천 리스트 스타일 */
.drug-list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 12px;
}

.drug-list li {
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.03);
  transition: transform 0.2s;
}

.drug-list li:hover {
  transform: translateX(4px);
  background: #f8fafc;
}

.drug-name { font-weight: 600; color: #334155; }
.arrow { color: #cbd5e1; }
.empty-msg { margin-top: 20px; color: #94a3b8; font-style: italic; }
</style>