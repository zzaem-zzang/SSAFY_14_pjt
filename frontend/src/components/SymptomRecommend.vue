<template>
  <div class="section">
    <h2>증상으로 약 추천</h2>
    <p class="desc">증상을 선택하면 관련 의약품을 추천해드립니다.</p>

    <select v-model="selectedSymptom" @change="fetchRecommend">
      <option disabled value="">증상 선택</option>
      <option
        v-for="symptom in symptoms"
        :key="symptom.id"
        :value="symptom.id"
      >
        {{ symptom.name }}
      </option>
    </select>

    <ul v-if="drugs.length">
      <li
        v-for="drug in drugs"
        :key="drug.id"
        @click="goDetail(drug.id)"
      >
        {{ drug.name }}
      </li>
    </ul>

    <p v-else-if="selectedSymptom" class="empty">
      추천 가능한 약이 없습니다.
    </p>
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

// 🔹 증상 목록 불러오기
onMounted(async () => {
  try {
    const res = await api.get('/symptoms/')
    symptoms.value = res.data
  } catch (err) {
    console.error('증상 목록 불러오기 실패', err)
  }
})

// 🔹 증상 선택 → 추천 요청
const fetchRecommend = async () => {
  if (!selectedSymptom.value) return

  try {
    const res = await api.get(
      `/recommend/symptom/?symptom=${selectedSymptom.value}`
    )
    drugs.value = res.data.recommendations
  } catch (err) {
    console.error('증상 추천 실패', err)
    drugs.value = []
  }
}

// 🔹 상세 페이지 이동
const goDetail = (id) => {
  router.push(`/drugs/${id}`)
}
</script>

<style scoped>
.section {
  margin-top: 40px;
}

select {
  padding: 10px;
  margin: 12px 0;
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ddd;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 10px;
  background: #fff;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
}

li:hover {
  background: #f1f5f9;
}

.desc {
  color: #666;
  font-size: 14px;
}

.empty {
  color: #999;
  margin-top: 10px;
}
</style>
