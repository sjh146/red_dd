# coupang-login-page - Work Plan

## TL;DR (For humans)

**What you'll get:** `f_template/coupang/` 폴더 안에 `login.html` 파일 하나와 `login.css` 파일 하나로 구성된, Coupang 스타일의 로그인 페이지. 브라우저에서 그냥 열면 Coupang 로그인 화면처럼 보이는 정적 페이지입니다. 이메일/비밀번호 입력 칸, 로그인 버튼, 자동로그인 체크박스, 회원가입/찾기 링크가 모두 포함됩니다.

**Why this approach:** 원본 clogin.html의 HTML 구조(class/id)와 CSS 선택자가 1:1로 연결되어 있어 DOM 구조는 완전히 보존하는 것이 스타일이 깨지지 않는 유일한 방법. 3개 CSS 파일(총 ~186KB)을 하나로 병합하고, 외부 JS만 제거하면 최소 변경으로 최대 시각적 충실도를 얻습니다.

**What it will NOT do:** 실제로 로그인되지는 않습니다 (제출 버튼을 눌러도 아무 일 없음). OTP/QR 로그인 탭은 구조만 남고 실제 동작하지 않음. Coupang 서버로 데이터를 전송하지 않음.

**Effort:** Medium
**Risk:** Low — CSS는 그대로 병합하고 HTML에서 외부 리소스만 제거하는 단순 작업
**Decisions to sanity-check:** 스프라이트 이미지가 CDN(coupangcdn.com)에서 로드되는 점 (오프라인에서는 깨짐)

Your next move: 이 계획을 승인(approve)한 후 `$start-work` 명령으로 실행을 시작하세요.

---

> TL;DR (machine): Medium effort, Low risk — 정적 Coupang 로그인 페이지 clone. 3개 CSS 병합 + HTML에서 외부 JS/CDN 리소스 제거.

## Scope
### Must have
- `f_template/coupang/login.html` — clogin.html 기반, 외부 JS/CDN 리소스 제거, 폼 구조 보존
- `f_template/coupang/login.css` — login.kr_ko-KR.css + login.clean.kr_ko-KR.css + inline#2.css 병합 (비압축 포맷팅)
- 이메일 로그인 폼 (아이디/비밀번호 입력 + 로그인 버튼 + 자동로그인 체크박스)
- Coupang 로고 (CDN 이미지 유지)
- 탭 헤더 (이메일/휴대폰/QR — 이메일만 active)
- 아이디/비밀번호 찾기 링크, 회원가입 링크
- 푸터 (©Coupang Corp.)

### Must NOT have (guardrails, anti-slop, scope boundaries)
- ❌ 외부 JS 스크립트 일체 (web-log, jslog, qrcode, login.min.js, wdpop, global-ff, web-inspector 등)
- ❌ 추적/분석/에러리포트 스크립트 및 JsLog 코드
- ❌ SEC 보안 위젯 (sec-overlay, VfBDQOWXZY 관련 태그/스타일)
- ❌ iframe 요소 (dpop iframe, pc-otp-login-iframe)
- ❌ modal-container (JS 종속 팝업)
- ❌ 실제 로그인/제출 기능 (form action은 유지하되 동작 없음)
- ❌ Coupang 외부 CDN JS 라이브러리 (CSS CDN 이미지는 유지)
- ❌ document.domain 설정, noscript 리다이렉트, I18n/CoupangSite 전역 설정
- ❌ HTML 구조(class/id) 변경 (CSS와의 매핑 유지)

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: none (정적 HTML+CSS — LSP diagnostics + browser open 확인)
- Evidence: .omo/evidence/task-1-coupang-login-page.txt, .omo/evidence/task-2-coupang-login-page.txt

## Execution strategy
### Parallel execution waves
- Wave 1: Todo 1 (CSS 병합)
- Wave 2: Todo 2 (HTML 정제) — Todo 1 완료 후

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. CSS 병합 | — | 2 | — |
| 2. HTML 정제 | 1 | — | — |
| F1-F4 | 1, 2 | — | F1-F4 모두 병렬 가능 |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] 1. `f_template/coupang/login.css`: 3개 CSS 파일 병합 + 포맷팅
  What to do / Must NOT do:
    1. `login.kr_ko-KR.css` (498줄, 비압축) → 그대로 사용
    2. `login.clean.kr_ko-KR.css` (1줄, ~182KB minified) → Prettier 또는 CSS beautifier로 포맷팅 (가독성 확보). BEM 클래스명, 스프라이트, 레이아웃 등 논리적 순서 유지
    3. `inline#2.css` (14줄, autofill 스타일) → 파일 끝에 추가
    4. 세 파일을 순서대로 결합하여 `f_template/coupang/login.css`로 저장
    Must NOT: CSS 선택자/속성 값 변경 금지, CDN URL 변경 금지, 파일 크기 줄이기 위해 내용 삭제 금지
  Parallelization: Wave 1 | Blocked by: — | Blocks: Todo 2
  References (executor has NO interview context - be exhaustive):
    - f_template/coupang/login.kr_ko-KR.css (498 lines)
    - f_template/coupang/login.clean.kr_ko-KR.css (1 line, ~182KB)
    - f_template/coupang/inline#2.css (14 lines)
  Acceptance criteria (agent-executable):
    1. `wc -c f_template/coupang/login.css` > 100000
    2. `head -5 f_template/coupang/login.css`가 `.rds-modal {`로 시작
    3. `tail -10 f_template/coupang/login.css`에 `@keyframes onautofillcancel` 포함
    4. `grep -c "member-logo" f_template/coupang/login.css` >= 10
    5. 모든 CDN URL(image10.coupangcdn.com, static.coupangcdn.com, coupangcdn.com)이 그대로 존재
  QA scenarios (name the exact tool + invocation): happy — 파일 생성 확인, 키 선택자 존재 확인, CDN URL 보존 확인. Evidence: .omo/evidence/task-1-coupang-login-page.txt
  Commit: Y | feat(coupang): Add merged login.css from 3 source CSS files

- [ ] 2. `f_template/coupang/login.html`: clogin.html 정제 (외부 리소스 제거)
  What to do / Must NOT do:
    1. clogin.html을 읽어서 f_template/coupang/login.html로 저장
    2. 제거할 항목:
       - `<head>` 내 외부 JS: web-log.umd.min.js, jslog, JsLog 코드 전체 (clogin.html:11-40)
       - 외부 CSS 링크 (clogin.html:83,87) → `login.css` 로컬 참조로 변경
       - qrcode.min.js (clogin.html:93)
       - login.min.js preload (clogin.html:97-99)
       - wdpop.js (clogin.html:102 끝부분)
       - Coupang 내부 data-* 속성 (data-log-pack, data-reference, data-web-build-no, data-web-product-global-ff, data-dpop-header-enabled, data-is-international-phone-number 등 — data-tab, data-id는 보존)
       - noscript (clogin.html:53)
       - document.domain 설정 (clogin.html:72)
       - I18n/CoupangSite JS (clogin.html:74-78)
       - 모든 외부 `<script>` 태그 (clogin.html:717-750)
       - sec-overlay 관련 HTML+CSS (clogin.html:750)
       - dpop iframe (clogin.html:754)
       - web-inspector config (clogin.html:754)
       - pc-otp-login-iframe + hidden form (clogin.html:530-531)
       - scoped-modal__container (clogin.html:734-735)
       - ui-autocomplete, qr-tab-under-line (clogin.html:735)
       - temp-content (clogin.html:707)
       - otpLogin-wrapper (clogin.html:597-657)
       - modal-container (clogin.html:709-715)
        - SVG sprite assets (clogin.html:540)는 QR 탭 아이콘에 사용되므로 QR 탭 HTML이 유지되는 한 함께 유지. 제거하려면 QR 탭 HTML도 함께 제거해야 함
    3. CSS 참조 변경:
       - `<link rel="stylesheet" href="login.css" type="text/css">` (login.kr_ko-KR.css 참조 대체)
       - login.clean.kr_ko-KR.css 링크는 제거 (login.css에 통합)
    4. form action은 유지 (동작하지 않음 — JS가 없으므로 submit 해도 이동 없음)
    5. HTML 구조(class/id)는 절대 변경 금지
    Must NOT: class/id 속성 변경 금지, form 구조 변경 금지, 시각적 요소(로고 이미지, 스프라이트 아이콘) 제거 금지
  Parallelization: Wave 2 | Blocked by: Todo 1 | Blocks: —
  References (executor has NO interview context - be exhaustive):
    - f_template/coupang/clogin.html (754 lines)
    - f_template/coupang/login.css (Todo 1 산출물)
  Acceptance criteria (agent-executable):
    1. `grep -c "<script" f_template/coupang/login.html`가 0 (script 태그 완전 제거)
    2. `grep "login.css" f_template/coupang/login.html`가 로컬 CSS 참조 확인 (딱 1개)
    3. `grep -c "coupangcdn" f_template/coupang/login.html` > 0 (CDN 이미지는 유지)
    4. HTML에 class="member-logo", id="login-email-input", id="login-password-input" 존재
    5. 외부 `<script src="http` 참조가 하나도 없음
  QA scenarios (name the exact tool + invocation): happy — HTML 파일 생성, 키 요소 존재 확인, 외부 script 0개 확인. Evidence: .omo/evidence/task-2-coupang-login-page.txt
  Commit: Y | feat(coupang): Create static login page from clogin.html without external JS

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit — 모든 Must have 충족, Must NOT have 위반 없음 확인
- [ ] F2. Code quality review — CSS 포맷팅 상태, HTML 구조 무결성 검토
- [ ] F3. Real manual QA — 브라우저에서 login.html 열어 Coupang 로그인 페이지와 시각적 일치 확인 (스프라이트 아이콘, 로고, 폼 레이아웃)
- [ ] F4. Scope fidelity — 외부 JS 0개, CDN CSS 참조 없음, CDN 이미지만 유지 확인

## Commit strategy
- Todo 1 완료 후: `feat(coupang): Add merged login.css from 3 source CSS files`
- Todo 2 완료 후: `feat(coupang): Create static login page from clogin.html without external JS`
- 최종 검증 후 선택적 squash

## Success criteria
- `f_template/coupang/login.html` — 외부 JS 0개, CDN CSS 참조 0개, CDN 이미지만 유지
- `f_template/coupang/login.css` — 3개 원본 CSS 병합, 모든 선택자 보존
- 브라우저에서 login.html 열었을 때 Coupang 로그인 페이지와 시각적으로 동일
- 폼 입력 가능, 버튼 클릭 가능 (submit 동작 없음)
