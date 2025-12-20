# API 명세 (Django REST Framework)

다음 API 표는 실전 서비스 기준으로 작성되었습니다. 인증은 DRF TokenAuth(`Authorization: Token <token>`)을 사용합니다.

| Method | URL                              | 설명                               | Request                                                                            | Response (예시)                                                                                           | 인증 여부                        |
| ------ | --------------------------------:| -------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------- |
| POST   | `/api/auth/register/`            | 회원가입 — 계정 생성 후 토큰 반환             | `{ "username": "jane", "email":"j@x.com", "password":"pass" }`                     | `201 { "id":1, "username":"jane","email":"j@x.com", "token":"abc..." }`                                 | ×                            |
| POST   | `/api/auth/login/`               | 로그인 — 토큰 반환                      | `{ "username":"jane","password":"pass" }`                                          | `200 { "token":"abc...", "user":{ "id":1,"username":"jane" } }`                                         | ×                            |
| POST   | `/api/auth/logout/`              | 로그아웃 — 서버에서 토큰 폐기                | Header `Authorization: Token <token>`                                              | `200 { "detail":"Logged out" }`                                                                         | **Token 인증 필요**              |
| GET    | `/api/auth/user/`                | 로그인 사용자 정보 조회                    | Header `Authorization: Token <token>`                                              | `200 { "id":1,"username":"jane","email":"j@x.com" }`                                                    | **Token 인증 필요**              |
| GET    | `/api/posts/`                    | 게시글 목록 조회 (페이지네이션)               | `?page=1&page_size=10`                                                             | `200 { "count":100, "results":[ { "id":1,"title":"...", "author":{...}, "excerpt":"..." } ] }`          | ×                            |
| GET    | `/api/posts/{id}/`               | 게시글 상세 조회 (댓글 포함)                | -                                                                                  | `200 { "id":1,"title":"...", "content":"...", "author":{ "id":2,"username":"kim" }, "comments":[...] }` | ×                            |
| POST   | `/api/posts/`                    | 게시글 생성 — 로그인 필요                  | Header `Authorization: Token <token>` <br>Body `{ "title":"...","content":"..." }` | `201 { "id":10,"title":"...", "author":{...} }`                                                         | **Token 인증 필요**              |
| PUT    | `/api/posts/{id}/`               | 게시글 수정 — **작성자만 가능** (관리자 허용 가능) | Header `Authorization: Token <token>` <br>Body `{ "title":"...","content":"..." }` | `200 { "id":1,"title":"...","content":"..." }`                                                          | **Token 인증 필요 — 작성자만 수정 가능** |
| DELETE | `/api/posts/{id}/`               | 게시글 삭제 — **작성자만 가능** (관리자 허용 가능) | Header `Authorization: Token <token>`                                              | `204 No Content`                                                                                        | **Token 인증 필요 — 작성자만 삭제 가능** |
| POST   | `/api/posts/{post_id}/comments/` | 댓글 생성                            | Header `Authorization: Token <token>` <br>Body `{ "content":"..." }`               | `201 { "id":5, "content":"...", "author":{...}, "post":10 }`                                            | **Token 인증 필요**              |
| DELETE | `/api/comments/{id}/`            | 댓글 삭제 — **작성자만 가능** (관리자 허용 가능)  | Header `Authorization: Token <token>`                                              | `204 No Content`                                                                                        | **Token 인증 필요 — 작성자만 삭제 가능** |


**추가: 외부 의약품 API 관련**
- GET `/api/drugs/save/?name={name}`
  - 설명: 공공데이터(E-Drug)에서 의약품을 검색하고 DB에 저장
  - 응답 예외: 외부 API 인증 문제(잘못된 `E_DRUG_API_KEY`) 등 외부 오류 발생 시 `502` + `{ "error": "외부 API 인증 실패: E_DRUG_API_KEY를 확인하세요." }` 와 같은 에러 메시지를 반환합니다. 프론트엔드에서 해당 메시지를 사용자에게 노출하도록 되어 있습니다.

> **주의:** 인증 헤더 예시: `Authorization: Token <token>`
