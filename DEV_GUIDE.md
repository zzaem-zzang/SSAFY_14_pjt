# 통합 가이드: Django REST + Vue 3 (Pinia, axios)

## 1) Vue ↔ Django 게시글 CRUD (실전 요약)

- 공통: `api` 인스턴스를 사용하세요 (src/api/index.js). Authorization은 `Authorization: Token <token>`.
1. 게시글 목록 조회 (GET)

```js
// src/views/PostListView.vue (요약)
import api from '@/api'
const res = await api.get('/posts/')
const posts = res.data.results // 또는 res.data
```

2. 게시글 상세 조회 (GET)

```js
const res = await api.get(`/posts/${id}/`)
const post = res.data
```

3. 게시글 생성 (POST, 인증 필요)

```js
await api.post('/posts/', { title, content })
// 201 응답 후 상세로 라우팅
router.push({ name: 'PostDetail', params: { id: res.data.id } })
```

4. 게시글 수정 (PUT, 작성자만 가능)

```js
await api.put(`/posts/${id}/`, { title, content })
// 403: 권한 없음, 401: 로그인 필요
```

5. 게시글 삭제 (DELETE, 작성자만 가능)

```js
await api.delete(`/posts/${id}/`)
```

에러 처리 팁:

- 401: 인증 필요 → 로그인 페이지로 리디렉션, 토큰 초기화
- 403: 권한 없음 → 사용자에게 적절한 메시지 표시

---

## 2) Pinia Auth Store (전체 코드 예시)

위치: `frontend/src/stores/auth.js`

```js
import { defineStore } from 'pinia'
import api from '@/api'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: null, user: null }),
  getters: { isLogin: state => !!state.token && !!state.user },
  actions: {
    init() { ... },
    async login(credentials) { ... },
    logout() { ... },
    setUser(user) { ... }
  }
})
```

- 토큰/최소 사용자 정보를 `localStorage`에 저장하여 새로고침 후에도 유지
- `isLogin` 판단 기준: `token 존재 && user 존재`

보안 팁: localStorage는 XSS에 취약합니다. CSP 적용, 입력 검증, 필요 시 HttpOnly 쿠키 + CSRF 방식을 고려하세요.

---

## 3) axios interceptor 예시 (src/api/index.js)

- 요청 인터셉터: Pinia에서 토큰을 읽어 `Authorization` 헤더 추가
- 응답 인터셉터: 401을 전역으로 잡아 `auth.logout()` 및 라우팅

```js
api.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Token ${auth.token}`
  return config
})

api.interceptors.response.use(null, error => {
  if (error.response?.status === 401) {
    const auth = useAuthStore()
    auth.logout()
    router.push({ name: 'Login' })
  }
  return Promise.reject(error)
})
```

---

## 4) 권한 처리 (작성자 / 관리자)

- 서버: 커스텀 permission `IsAuthorOrAdmin` 적용 (posts/permissions.py)
- View: `permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]`

401 vs 403:

- 401 Unauthorized: 인증(로그인) 필요
- 403 Forbidden: 인증은 되었지만 권한 없음

Vue에서 버튼 노출 제어:

```vue
<button v-if="auth.isLogin && (auth.user.id === post.author.id || auth.user.is_staff)">수정</button>
```

---

## 5) 실행 및 검증

- 백엔드: `.venv` 활성화 후 `python backend/manage.py migrate`, `python backend/manage.py runserver`
- 프론트엔드: `cd frontend && npm install && npm run dev`

---

## 6) 추가 권장 사항

- 토큰 만료/refresh 정책 추가 (access/refresh 패턴)
- XSS 방지(CSP, sanitize user input)
- API 응답 규격 통일(에러 형식 통일)

---

## 7) 환경 변수 설정 및 보안 권고 🔐

- 개발환경에서는 프로젝트 내 `backend/.env` 파일에 민감 정보를 저장하고, `.gitignore`에 포함하여 절대 커밋하지 마세요. 예시(`backend/.env.example`) 파일을 참고하세요.

- 필수 환경 변수 예시:
  - `SECRET_KEY` (Django)
  - `E_DRUG_API_KEY` (공공데이터 API 키)

- **중요:** 공개 채널(예: 이 채팅)에 API 키를 올리셨다면 즉시 해당 키를 폐기/재발급하세요. 보안 사고로 이어질 수 있습니다.

- 권장: 운영 환경에서는 Azure Key Vault, AWS Secrets Manager, Google Secret Manager 같은 비밀관리 서비스를 사용하세요.

---

## 8) 트러블슈팅: 의약품 검색이 500/502를 반환할 때 🔎

- 증상: `GET /api/drugs/save/?name=...` 호출 시 프론트에서 500 또는 502 에러 발생
- 원인: 외부 공공데이터 API (E-Drug) 호출 중 인증(401) 또는 다른 오류가 발생한 경우입니다. 보통 `E_DRUG_API_KEY`가 누락되었거나 잘못된 값일 때 발생합니다.
- 해결 방법:
  1. `backend/.env` 파일을 만들고 `E_DRUG_API_KEY=<your_key>` 를 추가하세요.
  2. 서버를 재시작하세요: `python backend/manage.py runserver`
  3. 문제가 계속되면 `backend/ingredients/utils.py`에서 외부 API 로그를 확인하거나, 직접 `manage.py shell`에서 `fetch_drug_from_api('타이')`를 호출해 반환값을 점검하세요.
- 참고: 서버는 인증 관련 실패를 502로 매핑하여 명확한 메시지를 반환합니다. 프론트엔드에서는 이를 표시하도록 되어 있습니다.

필요하시면 제가 `.env` 설정을 도와드리거나, 키 검증용 간단 엔드포인트를 추가해 드리겠습니다.

필요하시면 제가 이 가이드를 기반으로 프로젝트에 바로 적용되는 PR(또는 파일 변경)을 계속 진행하겠습니다.