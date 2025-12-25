<template>
  <section class="search-section">
    <!-- 🔍 검색 타입 선택 -->
    <div class="search-type">
      <label class="radio-option">
        <input type="radio" value="drug" v-model="searchType" />
        <span class="radio-label">약 이름</span>
      </label>
      <label class="radio-option">
        <input type="radio" value="symptom" v-model="searchType" />
        <span class="radio-label">증상</span>
      </label>
    </div>

    <div class="search-bar">
      <input v-model="keyword" :placeholder="searchType === 'drug'
        ? '약 이름 (예: 타이레놀)'
        : '어디가 아픈지 자연스럽게 입력해보세요 (예: 머리가 너무 아파요)'" @keyup.enter="search" />
      <button @click="search" class="btn-search">검색</button>
    </div>

    <!-- ⭐ 정렬 선택 바 -->
    <div v-if="drugs.length" class="sort-bar">
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

    <div v-if="loading" class="status-msg">
      <span class="spinner"></span> 검색 중입니다...
    </div>

    <div v-if="errorMessage" class="error-msg">
      ⚠️ {{ errorMessage }}
    </div>

    <div v-if="drugs.length" class="result-grid">
      <div class="drug-card" v-for="drug in drugs" :key="drug.id" @click="goDetail(drug.id)">
        <!-- ⭐ 낱알 이미지 -->
        <div class="image-wrap">
          <img :src="resolveImage(drug.image)" @error="onImgError" />
        </div>
        <div class="card-header">
          <h3>{{ drug.name }}</h3>
          <span class="badge" :class="drug.created ? 'new' : 'exist'">
            {{ drug.created ? '신규' : '정보' }}
          </span>
        </div>
        <p class="click-hint">자세히 보기 &rarr;</p>
      </div>
    </div>

    <div v-else-if="searched && !loading && !errorMessage" class="status-msg empty">
      검색 결과가 없습니다.
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useRouter, useRoute } from 'vue-router'
import placeholder from '@/assets/drug-placeholder.png'

const order = ref('default')
const router = useRouter()
const keyword = ref('')
const drugs = ref([])
const loading = ref(false)
const searched = ref(false)
const errorMessage = ref('')
const searchType = ref('drug') // 'drug' | 'symptom'
const route = useRoute()

onMounted(() => {
  const { keyword: q, type, order: o } = route.query

  if (q) {
    keyword.value = q
    searchType.value = type || 'drug'
    order.value = o || 'default'
    search()
  }
})

const onImgError = (e) => {
  e.target.src = placeholder
}

const setOrder = (value) => {
  order.value = value
  search()
}
const resolveImage = (imagePath) => {
  if (!imagePath) return placeholder
  const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  return `${base}${imagePath}`   // /media/...
}


const search = async () => {
  if (!keyword.value.trim()) return

  // ✅ URL에 검색 상태 저장
  router.push({
    path: route.path,
    query: {
      keyword: keyword.value,
      type: searchType.value,
      order: order.value,
    }
  })

  loading.value = true
  searched.value = true
  errorMessage.value = ''

  try {
    let res

    if (searchType.value === 'drug') {
      res = await api.get('/drugs/', {
        params: {
          search: keyword.value,
          order: order.value !== 'default' ? order.value : undefined
        }
      })
      drugs.value = res.data || []
    }

    if (searchType.value === 'symptom') {
      res = await api.get('/drugs/ai-search/', {
        params: { q: keyword.value }
      })
      drugs.value = res.data.results || []
    }

  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      '검색 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}


const goDetail = (id) => {
  router.push({
    path: `/drugs/${id}`,
    query: {
      keyword: keyword.value,
      type: searchType.value,
      order: order.value
    }
  })
}

</script>

<style scoped>
.search-section {
  width: 100%;
}

/* 검색 타입 선택 */
.search-type {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;

}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.radio-option input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #4f46e5;
  /* 라디오 버튼 테두리 강조 */
  border: 2px solid #4f46e5;
  appearance: auto;
  color: white;
}

.radio-label {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  /* 진한 색상으로 변경 */
  cursor: pointer;
}

/* 검색창 스타일 */
.search-bar {
  display: flex;
  gap: 12px;
  background: white;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  /* 테두리 제거 */
  border: none;
}

input {
  flex: 1;
  border: none;
  font-size: 1rem;
  padding: 12px 16px;
  outline: none;
  border-radius: 12px;
  color: #1e293b;
  background: transparent;
}

input::placeholder {
  color: #94a3b8;
}

input:focus {
  background: #f8fafc;
}

/* 이미지 래퍼: 높이를 고정하고 넘치는 부분 숨김 */
.image-wrap {
  width: 100%;
  height: 160px;
  overflow: hidden;
  border-radius: 12px;
  margin-bottom: 12px;
  background-color: #f8fafc;
}

/* 이미지 본체: 꽉 채우되 비율 유지 */
.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.btn-search {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-search:hover {
  background: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.btn-search:active {
  transform: translateY(0);
}

/* 결과 그리드 */
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 30px;
}

.drug-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.drug-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border-color: #4f46e5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.badge.new {
  background: #dcfce7;
  color: #166534;
}

.badge.exist {
  background: #f1f5f9;
  color: #475569;
}

.click-hint {
  margin-top: 12px;
  font-size: 0.9rem;
  color: #4f46e5;
  font-weight: 500;
}

.status-msg {
  text-align: center;
  margin-top: 40px;
  color: #64748b;
  font-size: 1rem;
}

.status-msg.empty {
  padding: 40px;
  background: #f8fafc;
  border-radius: 12px;
}

.error-msg {
  margin-top: 20px;
  padding: 12px;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 8px;
  text-align: center;
}

.sort-bar {
  display: flex;
  gap: 8px;
  margin-top: 16px;


}

.sort-bar button {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s ease;
}

.sort-bar button:hover {
  border-color: #4f46e5;
  color: #4f46e5;
}

.sort-bar button.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

/* 스피너 애니메이션 */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 반응형 */
@media (max-width: 768px) {
  .search-type {
    gap: 20px;
  }

  .radio-label {
    font-size: 0.95rem;
  }

  .search-bar {
    gap: 10px;
    padding: 6px;
  }

  input {
    padding: 10px 14px;
    font-size: 0.95rem;
  }

  .btn-search {
    padding: 0 20px;
    font-size: 0.95rem;
  }

  .result-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .search-type {
    gap: 16px;
  }

  .radio-option input[type="radio"] {
    width: 16px;
    height: 16px;
  }

  .radio-label {
    font-size: 0.9rem;
  }

  .search-bar {
    flex-direction: column;
    gap: 8px;
  }

  .btn-search {
    width: 100%;
    padding: 12px;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>