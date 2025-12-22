<template>
  <div class="detail-container">
    <div v-if="loading" class="loading">정보를 불러오고 있습니다...</div>

    <div v-else-if="error" class="error-view">
      <h3>존재하지 않는 의약품입니다.</h3>
      <button @click="goHome">홈으로 돌아가기</button>
    </div>

    <div v-else class="info-card">
      <div class="card-header">
        <span class="category">의약품 상세정보</span>
        <h1 class="drug-title">{{ drug.name }}</h1>
      </div>

      <div class="image-wrap">
        <img :src="drug.image_url || placeholder" @error="onImgError" alt="약 이미지" />
      </div>
      <!-- ⭐ 평균 별점 -->
      <div v-if="typeof drug.avg_rating === 'number'" class="avg-rating">

        ⭐ 평균 평점 {{ drug.avg_rating.toFixed(1) }} / 5
      </div>

      <!-- 👍👎 사용자 반응 버튼 -->
      <DrugReactionButtons />


      <div class="card-body">
        <section class="info-section">
          <h3>📌 효능 및 효과</h3>
          <p>{{ drug.effect || '정보 없음' }}</p>
        </section>

        <section class="info-section">
          <h3>📖 용법 및 용량</h3>
          <p>{{ drug.usage || '정보 없음' }}</p>
        </section>

        <section class="info-section warning">
          <h3>⚠️ 주의사항</h3>
          <p>{{ drug.warning || '정보 없음' }}</p>
        </section>
      </div>
      <!-- 🤖 AI 요약 섹션 -->
      <section class="ai-card">
        <h3>🤖 AI 요약</h3>

        <div v-if="summaryLoading">AI 요약을 불러오는 중...</div>

        <div v-else-if="aiSummary">
          <p class="one-liner">{{ aiSummary.one_liner }}</p>

          <p class="easy">{{ aiSummary.easy_explain }}</p>

          <ul>
            <li v-for="(p, i) in aiSummary.key_points" :key="i">✔ {{ p }}</li>
          </ul>

          <h4>⚠️ 주의사항</h4>
          <ul>
            <li v-for="(c, i) in aiSummary.cautions" :key="i">⚠ {{ c }}</li>
          </ul>

          <h4>🏥 병원에 가야 할 때</h4>
          <ul>
            <li v-for="(w, i) in aiSummary.when_to_see_doctor" :key="i">🏥 {{ w }}</li>
          </ul>
        </div>
      </section>
      <!-- 🖼️ AI 이미지 -->
      <section class="ai-image">
        <button @click="generateAiImage" :disabled="imageLoading">
          {{ imageLoading ? '이미지 생성 중...' : 'AI 이미지 생성' }}
        </button>

        <p v-if="imageError" class="error">{{ imageError }}</p>

        <div v-if="aiImage" class="image-wrap">
          <img :src="aiImage" alt="AI 생성 이미지" />
        </div>
      </section>

      <div class="card-footer">
        <button class="back-btn" @click="goHome">목록으로</button>
      </div>
    </div>
  </div>


  <!-- 💬 리뷰 섹션 -->
  <div class="review-card">
    <h3>💬 사용자 리뷰</h3>

    <!-- 리뷰 목록 -->
    <ul v-if="drug.comments.length">
      <li v-for="c in drug.comments" :key="c.id" class="review-item">
        <div class="review-header">

          <strong>{{ c.author.username }}</strong>
          <span v-if="c.rating" class="review-rating">
            <span v-for="i in 5" :key="i" :class="{ active: i <= c.rating }">★</span>
          </span>
        </div>
        <p>{{ c.content }}</p>
      </li>
    </ul>

    <p v-else class="empty-review">아직 리뷰가 없습니다.</p>

    <!-- 리뷰 작성 -->
    <div v-if="auth.isLogin" class="review-form">

      <!-- ⭐ 별점 입력 -->
      <div class="star-rating">
        <span v-for="i in 5" :key="i" class="star" :class="{ active: i <= (hoverRating || rating) }"
          @mouseenter="setHover(i)" @mouseleave="clearHover" @click="setRating(i)">
          ★
        </span>
      </div>

      <textarea v-model="newComment" placeholder="이 약에 대한 경험을 남겨주세요"></textarea>

      <button @click="createComment">리뷰 등록</button>
    </div>

    <p v-else class="login-hint">
      리뷰를 작성하려면 로그인하세요.
    </p>
  </div>

</template>

<script setup>
import placeholder from '@/assets/drug-placeholder.png'
import { ref, onMounted } from 'vue'
import api from '@/api'
import DrugReactionButtons from '@/components/DrugReactionButtons.vue'
import { useRoute, useRouter } from 'vue-router'

const onImgError = (e) => {
  e.target.src = placeholder
}

// 🤖 AI 요약
const aiSummary = ref(null)
const summaryLoading = ref(false)

// 🖼️ AI 이미지
const aiImage = ref(null)
const imageLoading = ref(false)
const imageError = ref('')

// ai 요약 
const fetchAiSummary = async () => {
  summaryLoading.value = true
  try {
    const res = await api.get(`/drugs/${route.params.id}/ai-summary/`)
    aiSummary.value = res.data
  } catch (e) {
    console.error('AI 요약 로드 실패', e)
  } finally {
    summaryLoading.value = false
  }
}

// ai 이미지
const generateAiImage = async () => {
  imageLoading.value = true
  imageError.value = ''
  aiImage.value = null

  try {
    const res = await api.post(`/drugs/${route.params.id}/ai-image/`)
    aiImage.value = `data:${res.data.mime_type};base64,${res.data.base64}`
  } catch (e) {
    imageError.value = 'AI 이미지 생성에 실패했습니다.'
  } finally {
    imageLoading.value = false
  }
}



const route = useRoute()
const router = useRouter()
const drug = ref({
  name: '',
  effect: '',
  usage: '',
  warning: '',
  image_url: '',
  avg_rating: null,
  comments: []
})

const loading = ref(true)
const error = ref(false)

onMounted(async () => {
  try {
    const res = await api.get(`/drugs/${route.params.id}/`)
    drug.value = res.data
    fetchAiSummary()
  } catch (err) {
    error.value = true
  } finally {
    loading.value = false
  }
})

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const newComment = ref('')
const rating = ref(0)
const hoverRating = ref(0)

function setRating(val) {
  rating.value = val
}
function setHover(val) {
  hoverRating.value = val
}
function clearHover() {
  hoverRating.value = 0
}

// 댓글 작성
async function createComment() {
  if (!newComment.value.trim()) return

  try {
    await api.post(`/drugs/${route.params.id}/comments/`, {
      content: newComment.value,
      rating: rating.value || null
    })
    newComment.value = ''
    rating.value = 0

    // 댓글 다시 불러오기
    const res = await api.get(`/drugs/${route.params.id}/`)
    drug.value = res.data
  } catch (e) {
    alert('리뷰 작성 실패')
  }
}



const goHome = () => {
  const keyword = route.query.keyword

  if (keyword) {
    router.push({
      path: '/',
      query: { keyword }
    })
  } else {
    router.push('/')
  }
}

</script>

<style scoped>
.detail-container {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}

.info-card {
  width: 100%;
  max-width: 700px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  padding: 40px 30px;
}

.category {
  font-size: 0.9rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.drug-title {
  margin: 10px 0 0 0;
  font-size: 2rem;
  font-weight: 800;
}

.card-body {
  padding: 30px;
}

.info-section {
  margin-bottom: 30px;
}

.info-section h3 {
  color: #4f46e5;
  font-size: 1.1rem;
  margin-bottom: 10px;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 8px;
  display: inline-block;
}

.info-section p {
  line-height: 1.7;
  color: #475569;
  white-space: pre-line;
}

.info-section.warning h3 {
  color: #dc2626;
}

.info-section.warning p {
  background: #fef2f2;
  padding: 15px;
  border-radius: 8px;
  color: #991b1b;
}

.card-footer {
  padding: 20px 30px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  text-align: right;
}

.back-btn {
  padding: 10px 20px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  font-weight: 600;
}

.back-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.loading,
.error-view {
  text-align: center;
  margin-top: 50px;
  color: #64748b;
}

.avg-rating {
  margin: 20px auto;
  text-align: center;
  font-weight: 700;
  color: #f59e0b;
}

.review-card {
  max-width: 700px;
  margin: 30px auto;
  background: white;
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}

.review-item {
  border-bottom: 1px solid #f1f5f9;
  padding: 15px 0;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-rating span {
  color: #e5e7eb;
}

.review-rating span.active {
  color: #facc15;
}

.star-rating {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.star {
  font-size: 1.8rem;
  color: #e5e7eb;
  cursor: pointer;
}

.star.active {
  color: #facc15;
}

.review-form textarea {
  width: 100%;
  min-height: 80px;
  margin: 10px 0;
}

.review-form button {
  background: #4f46e5;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.empty-review,
.login-hint {
  text-align: center;
  color: #94a3b8;
  margin-top: 15px;
}

.image-wrap {
  width: 100%;
  height: 260px;
  overflow: hidden;
  /* 넘치는 부분 자르기 */
  background: #f8fafc;
}

.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 좌우 꽉 채움 (핵심) */
  display: block;
}

.ai-card {
  margin-top: 30px;
  padding: 20px;
  border-radius: 16px;
  background: #f8fafc;
}

.one-liner {
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 8px;
}

.easy {
  margin-bottom: 12px;
  color: #475569;
}

.ai-image button {
  margin-top: 16px;
  padding: 10px 20px;
  border-radius: 10px;
  background: #4f46e5;
  color: white;
  border: none;
  cursor: pointer;
}

.ai-image img {
  margin-top: 16px;
  width: 100%;
  max-height: 420px;
  object-fit: contain;
  background: white;
  border-radius: 12px;
}

</style>