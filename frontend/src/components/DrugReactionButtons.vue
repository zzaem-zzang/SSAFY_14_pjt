<template>
  <div class="reaction-box">
    <!-- 👍 도움됐어요 -->
    <button
      class="reaction-btn"
      :class="{ active: myReaction === 'helpful' }"
      @click="toggleReaction('helpful')"
    >
      👍 도움됐어요 {{ counts.helpful }}
    </button>

    <!-- 👎 도움 안 됐어요 -->
    <button
      class="reaction-btn"
      :class="{ active: myReaction === 'unhelpful' }"
      @click="toggleReaction('unhelpful')"
    >
      👎 도움 안 됐어요 {{ counts.unhelpful }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const drugId = route.params.id

// 반응 개수
const counts = ref({
  helpful: 0,
  unhelpful: 0,
})

// 내가 누른 반응 (helpful / unhelpful / null)
const myReaction = ref(null)

// ----------------------
// 반응 정보 불러오기
// ----------------------
const fetchReactions = async () => {
  const res = await api.get(`/drugs/${drugId}/reaction/`)
  counts.value.helpful = res.data.helpful
  counts.value.unhelpful = res.data.unhelpful
  myReaction.value = res.data.my_reaction
}

onMounted(fetchReactions)

// ----------------------
// 반응 토글 처리
// ----------------------
const toggleReaction = async (reactionType) => {
  if (!auth.isLogin) {
    alert('로그인 후 반응을 남길 수 있습니다.')
    return
  }

  // 같은 버튼 다시 클릭 → 취소
  const payload =
    myReaction.value === reactionType
      ? { reaction: null }
      : { reaction: reactionType }

  await api.post(`/drugs/${drugId}/reaction/`, payload)

  // 최신 상태 다시 불러오기
  fetchReactions()
}
</script>

<style scoped>
.reaction-box {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.reaction-btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.reaction-btn:hover {
  background: #f8fafc;
}

.reaction-btn.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}
</style>
