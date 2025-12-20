<template>
  <div class="section">
    <h2>의약품 검색</h2>

    <!-- 🔍 검색창 -->
    <div class="search-box">
      <input
        v-model="keyword"
        placeholder="약 이름을 입력하세요"
        @keyup.enter="search"
      />
      <button @click="search">검색</button>
    </div>

    <!-- 🔄 로딩 -->
    <p v-if="loading" class="info">검색 중입니다...</p>

    <!-- 🧾 검색 결과 카드 -->
    <div v-if="drugs.length" class="card-list">
      <div
        class="drug-card"
        v-for="drug in drugs"
        :key="drug.id"
      >
        <h3>{{ drug.name }}</h3>

        <span
          class="badge"
          :class="drug.created ? 'new' : 'exist'"
        >
          {{ drug.created ? '신규 저장' : '기존 데이터' }}
        </span>

        <button @click="goDetail(drug.id)">
          상세보기
        </button>
      </div>
    </div>

    <!-- 📭 결과 없음 -->
    <p v-else-if="searched && !loading && !errorMessage" class="info">
      검색 결과가 없습니다.
    </p>

    <!-- ❗ 오류 메시지 -->
    <p v-if="errorMessage" class="error">오류: {{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const keyword = ref('')
const drugs = ref([])
const loading = ref(false)
const searched = ref(false)
const errorMessage = ref('')

const search = async () => {
  if (!keyword.value) return

  loading.value = true
  searched.value = true

  try {
    const res = await api.get(
      `/drugs/save/?name=${encodeURIComponent(keyword.value)}`
    )
    drugs.value = res.data.saved || []
    errorMessage.value = ''
  } catch (err) {
    console.error('검색 실패', err)
    drugs.value = []
    // 사용자에게 보일 수 있는 에러 메시지 추출
    const serverMessage = err.response?.data?.error || err.response?.data?.detail || err.message
    errorMessage.value = serverMessage
  }

  loading.value = false
}

const goDetail = (id) => {
  router.push(`/drugs/${id}`)
}
</script>

<style scoped>
.section {
  margin-bottom: 40px;
}

/* 검색 영역 */
.search-box {
  display: flex;
  gap: 8px;
  margin: 12px 0;
}

input {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

button {
  padding: 10px 14px;
  border-radius: 8px;
  border: none;
  background: #4f46e5;
  color: white;
  cursor: pointer;
}

button:hover {
  background: #4338ca;
}

/* 카드 리스트 */
.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

/* 카드 */
.drug-card {
  background: #ffffff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drug-card h3 {
  margin: 0;
  font-size: 16px;
}

/* 배지 */
.badge {
  width: fit-content;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge.new {
  background: #dcfce7;
  color: #166534;
}

.badge.exist {
  background: #e5e7eb;
  color: #374151;
}

/* 안내 문구 */
.info {
  margin-top: 16px;
  color: #777;
}

/* 오류 메시지 */
.error {
  margin-top: 12px;
  color: #b91c1c;
  background: #fff5f5;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #fecaca;
}
</style>
