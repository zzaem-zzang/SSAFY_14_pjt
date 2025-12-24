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
        <img :src="drug.image || drug.image_url || placeholder" @error="onImgError" alt="약 이미지" />
      </div>

      <!-- ⭐ 평균 별점 -->
      <div v-if="typeof drug.avg_rating === 'number'" class="avg-rating">
        ⭐ 평균 평점 {{ drug.avg_rating.toFixed(1) }} / 5
      </div>

      <!-- 👍👎 사용자 반응 버튼 -->
      <DrugReactionButtons />

      <!-- 🎫 QR 코드 섹션 -->
      <section class="qr-section">
        <div class="qr-header">
          <h3>📱 약국에서 보여주기</h3>
          <p class="qr-desc">약국에서 이 QR 코드를 스캔하면 약 정보가 텍스트로 나타나요!</p>
        </div>

        <button v-if="!showQR" @click="generateQR" class="qr-btn" :disabled="qrLoading">
          {{ qrLoading ? 'QR 코드 생성 중...' : '🎫 QR 코드 생성하기' }}
        </button>

        <div v-if="showQR" class="qr-display">
          <!-- QR 코드 이미지 -->
          <div class="qr-image-container">
            <img :src="qrImage" alt="약 정보 QR 코드" class="qr-image" />
          </div>

          <!-- 약 정보 -->
          <div class="qr-info">
            <p class="qr-drug-name">{{ drug.name }}</p>
            <p class="qr-instruction">📸 약국 직원에게 이 화면을 보여주세요</p>
          </div>

          <!-- 🔥 스캔하면 보이는 정보 미리보기 -->
          <div class="qr-preview" v-if="drugInfo && Object.keys(drugInfo).length > 0">
            <h4>📋 QR 스캔 시 표시되는 정보:</h4>
            <div class="preview-content">
              <div class="preview-item">
                <span class="preview-label">약품명:</span>
                <span class="preview-value">{{ drugInfo['약품명'] }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">효능효과:</span>
                <span class="preview-value">{{ drugInfo['효능효과'] }}</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">용법용량:</span>
                <span class="preview-value">{{ drugInfo['용법용량'] }}</span>
              </div>
              <div class="preview-item warning-item">
                <span class="preview-label">⚠️ 주의사항:</span>
                <span class="preview-value">{{ drugInfo['주의사항'] }}</span>
              </div>
            </div>
          </div>

          <!-- 버튼들 -->
          <div class="qr-actions">
            <button @click="downloadQR" class="download-btn">
              💾 QR 코드 저장
            </button>
            <button @click="printQR" class="print-btn">
              🖨️ 인쇄하기
            </button>
            <button @click="shareQR" class="share-btn">
              📤 공유하기
            </button>
          </div>

          <!-- 사용 팁 -->
          <div class="usage-tip">
            <p>💡 <strong>약국에서 사용법:</strong></p>
            <ol>
              <li>약국 직원에게 QR 코드를 보여주세요</li>
              <li>직원이 스캔하면 약 정보가 <strong>텍스트</strong>로 나타납니다</li>
              <li>약사님이 정보를 확인하고 약을 찾아드립니다</li>
            </ol>

          </div>
        </div>
      </section>

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

      <!-- DrugDetailView.vue (상세페이지 하단쯤) -->
      <!-- ✅ 기존 <section class="chatbot"> 를 아래로 교체 -->
      <section class="info-section chatbot-section">
        <h3>💬 이 약에 대해 물어보세요</h3>

        <div class="chat-panel">
          <div class="chat-log">
            <div v-for="(m, i) in chat" :key="i" :class="['msg', m.role]">
              <div class="bubble">{{ m.text }}</div>
            </div>
            <div v-if="chatLoading" class="msg bot">
              <div class="bubble">답변 생성 중...</div>
            </div>
          </div>

          <div class="quick">
            <button v-for="s in suggestions" :key="s" @click="send(s)">{{ s }}</button>
          </div>

          <div class="chat-input">
            <input v-model="userMsg" @keyup.enter="send()" placeholder="요기에 입력하세요 !!! " />
            <button @click="send()" :disabled="chatLoading || !userMsg.trim()">전송</button>
          </div>
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
      <li v-for="c in drug.comments" :key="`comment-${c.id}`" class="review-item">
        <div class="review-header">
          <span>{{ c.author.nickname || c.author.username }}</span>

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
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const onImgError = (e) => {
  e.target.src = placeholder
}

// 🎫 QR 코드 관련 변수
const showQR = ref(false)
const qrImage = ref('')
const drugInfo = ref({})  // 🔥 약 정보 저장
const qrLoading = ref(false)

// QR 코드 생성
const generateQR = async () => {
  qrLoading.value = true
  try {
    const res = await api.get(`/drugs/${route.params.id}/qr/`)
    qrImage.value = res.data.qr_image
    drugInfo.value = res.data.drug_info  // 🔥 약 정보 저장
    showQR.value = true
    console.log('✅ QR 코드 생성 완료')
    console.log('✅ 약 정보:', drugInfo.value)
  } catch (e) {
    console.error('❌ QR 코드 생성 에러:', e)
    alert(`QR 코드 생성에 실패했습니다: ${e.response?.data?.error || e.message}`)
  } finally {
    qrLoading.value = false
  }
}

// QR 코드 다운로드
const downloadQR = () => {
  const link = document.createElement('a')
  link.href = qrImage.value
  link.download = `${drug.value.name}_QR코드.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// QR 코드 인쇄
const printQR = () => {
  const printWindow = window.open('', '', 'height=600,width=800')
  printWindow.document.write('<html><head><title>약 정보 QR 코드</title>')
  printWindow.document.write('<style>')
  printWindow.document.write(`
    body { 
      display: flex; 
      flex-direction: column; 
      align-items: center; 
      justify-content: center; 
      padding: 20px; 
      font-family: sans-serif;
    }
    h1 { margin: 20px 0; font-size: 28px; }
    img { max-width: 400px; border: 2px solid #000; padding: 10px; }
    p { margin: 10px 0; font-size: 14px; color: #666; }
    .instruction { font-weight: bold; margin-top: 20px; }
  `)
  printWindow.document.write('</style></head><body>')
  printWindow.document.write(`<h1>${drug.value.name}</h1>`)
  printWindow.document.write(`<img src="${qrImage.value}" />`)
  printWindow.document.write('<p class="instruction">약국에서 이 QR 코드를 스캔하면<br>약 정보가 텍스트로 나타납니다</p>')
  printWindow.document.write('</body></html>')
  printWindow.document.close()
  setTimeout(() => {
    printWindow.print()
  }, 250)
}

// QR 코드 공유
const shareQR = async () => {
  try {
    const response = await fetch(qrImage.value)
    const blob = await response.blob()
    const file = new File([blob], `${drug.value.name}_QR.png`, { type: 'image/png' })

    if (navigator.share && navigator.canShare({ files: [file] })) {
      await navigator.share({
        title: `${drug.value.name} - 약 정보`,
        text: `약국에서 보여줄 ${drug.value.name} QR 코드입니다.`,
        files: [file]
      })
      console.log('✅ 공유 완료')
    } else {
      console.log('공유 API 미지원, 다운로드로 대체')
      downloadQR()
      alert('이 브라우저는 공유 기능을 지원하지 않아 다운로드했습니다.')
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      console.error('공유 실패:', e)
      alert('공유에 실패했습니다. 다운로드를 시도해주세요.')
    }
  }
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
  if (Object.keys(route.query).length > 0) {
    router.push({
      path: '/',
      query: route.query   // ⭐ query 통째로 복원
    })
  } else {
    router.push('/')
  }
}


// ✅ 챗봇 상태
const chat = ref([
  { role: 'bot', text: '이 약에 무엇이든 궁금한 걸 물어보세요! ❤️' }
])
const userMsg = ref('')
const chatLoading = ref(false)
const suggestions = ref(['효능', '복용법', '주의사항', '부작용'])

// ✅ 메시지 전송
const send = async (preset) => {
  const msg = (preset ?? userMsg.value).trim()
  if (!msg || chatLoading.value) return

  chat.value.push({ role: 'user', text: msg })
  userMsg.value = ''
  chatLoading.value = true

  try {
    // ⚠️ 백엔드에 /drugs/<id>/chat/ 엔드포인트가 있어야 함
    const res = await api.post(`/drugs/${route.params.id}/chat/`, { message: msg })

    chat.value.push({ role: 'bot', text: res.data.reply })

    // 서버에서 suggestions 내려주면 갱신
    if (Array.isArray(res.data.suggestions)) {
      suggestions.value = res.data.suggestions
    }
  } catch (e) {
    chat.value.push({ role: 'bot', text: '오류가 발생했어요. 잠시 후 다시 시도해 주세요.' })
  } finally {
    chatLoading.value = false
  }
}
</script>

<style scoped>
/* ✅ 챗봇 섹션: info-section 스타일을 베이스로 */
.chatbot-section {
  margin: 30px;
}

/* ✅ 챗봇 내부 패널(본문) */
.chat-panel {
  margin-top: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
}

/* ✅ 로그 영역: info-section 본문 느낌 */
.chat-log {
  max-height: 320px;
  overflow: auto;
  padding: 30px;
  background: #f8fafc;
  /* card-body 톤이랑 맞춤 */
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

/* ✅ 말풍선 */
.msg {
  display: flex;
  margin: 8px 0;
}

.msg.user {
  justify-content: flex-end;
}

.msg.bot {
  justify-content: flex-start;
}

.bubble {
  max-width: 80%;
  white-space: pre-line;
  padding: 10px 12px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #4f46e5;
  line-height: 1.6;
}

/* 사용자 말풍선만 은은하게 강조 (효능 섹션의 보라톤과 톤 맞춤) */
.msg.user .bubble {
  background: #eef2ff;
  border-color: #c7d2fe;
}

/* ✅ 빠른 버튼 */
.quick {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
  margin-left: 30px;
}

.quick button {
  padding: 6px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #ffffff;
  cursor: pointer;
  font-weight: 600;
  color: #4f46e5;
  /* info-section h3 색과 통일 */
}

.quick button:hover {
  background: #f1f5f9;
}

/* ✅ 입력창 */
.chat-input {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.chat-input button {
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  background: #4f46e5;
  /* 메인 컬러 */
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.chat-input button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}


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
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: inherit;
}

.review-form button {
  background: #4f46e5;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.review-form button:hover {
  background: #4338ca;
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
  background: #f8fafc;
}

.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.ai-card {
  margin: 30px;
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



/* ✅ 카드 폭 끝까지(이미 적용한 full-bleed 유지) */
.ai-image.full-bleed {
  margin: 0;
  padding: 30px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

/* ✅ 프레임 크기: 높이를 확 키움 (반응형) */
.ai-image-frame {
  margin-top: 16px;
  width: 100%;
  height: clamp(320px, 55vw, 700px);
  /* ✅ 여기서 커짐 */
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

/* ✅ 프레임을 꽉 채우기 (잘려도 시원하게) */
.ai-image-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 안 잘리게 전체 보이려면 contain */
  display: block;
}

/* 🎫 QR 코드 스타일 */
.qr-section {
  margin: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 16px;
  border: 2px dashed #0ea5e9;
}

.qr-header {
  text-align: center;
  margin-bottom: 20px;
}

.qr-header h3 {
  color: #0369a1;
  font-size: 1.3rem;
  margin-bottom: 8px;
}

.qr-desc {
  color: #0c4a6e;
  font-size: 0.95rem;
  margin: 0;
}

.qr-btn {
  display: block;
  width: 100%;
  padding: 15px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.qr-btn:hover:not(:disabled) {
  background: #0284c7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.qr-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

.qr-display {
  text-align: center;
}

.qr-image-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  display: inline-block;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.qr-image {
  width: 280px;
  height: 280px;
  display: block;
}

.qr-info {
  margin-bottom: 20px;
}

.qr-drug-name {
  font-size: 1.3rem;
  font-weight: 800;
  color: #0369a1;
  margin: 0 0 8px 0;
}

.qr-instruction {
  color: #0c4a6e;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

/* 🔥 QR 미리보기 스타일 */
.qr-preview {
  background: white;
  border: 2px solid #e0f2fe;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  text-align: left;
}

.qr-preview h4 {
  color: #0369a1;
  font-size: 1rem;
  margin: 0 0 15px 0;
  text-align: center;
}

.preview-content {
  background: #f8fafc;
  padding: 15px;
  border-radius: 8px;
}

.preview-item {
  margin: 12px 0;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border-left: 4px solid #0ea5e9;
}

.preview-item.warning-item {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.preview-label {
  display: block;
  font-weight: 700;
  color: #0369a1;
  margin-bottom: 5px;
  font-size: 0.9rem;
}

.preview-item.warning-item .preview-label {
  color: #dc2626;
}

.preview-value {
  display: block;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.preview-item.warning-item .preview-value {
  color: #991b1b;
}

.qr-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 20px 0;
}

.qr-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.download-btn {
  background: #10b981;
  color: white;
}

.download-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.print-btn {
  background: #6366f1;
  color: white;
}

.print-btn:hover {
  background: #4f46e5;
  transform: translateY(-1px);
}

.share-btn {
  background: #f59e0b;
  color: white;
}

.share-btn:hover {
  background: #d97706;
  transform: translateY(-1px);
}

/* 사용 팁 */
.usage-tip {
  background: #fef3c7;
  border: 2px solid #fbbf24;
  border-radius: 12px;
  padding: 15px;
  margin-top: 20px;
  text-align: left;
}

.usage-tip p {
  margin: 0 0 10px 0;
  color: #92400e;
  font-weight: 700;
}

.usage-tip ol {
  margin: 0 0 10px 0;
  padding-left: 20px;
  color: #78350f;
}

.usage-tip li {
  margin: 5px 0;
  line-height: 1.5;
}

.tip-note {
  margin: 10px 0 0 0 !important;
  font-size: 0.9rem;
  color: #059669 !important;
  font-weight: 600 !important;
}

/* 모바일 반응형 */
@media (max-width: 640px) {
  .qr-image {
    width: 220px;
    height: 220px;
  }

  .qr-actions {
    flex-direction: column;
  }

  .qr-actions button {
    width: 100%;
  }

  .preview-content {
    font-size: 0.85rem;
  }
}
</style>