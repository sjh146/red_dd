# naver-login-page - Work Plan

## TL;DR (For humans)

**What you'll get:** `f_template/naver/` 폴더 안에 `login.html` 파일 하나와 `login.css` 파일 하나로 구성된, Naver 스타일의 로그인 페이지. 브라우저에서 그냥 열면 Naver 로그인 화면처럼 보이는 정적 페이지입니다. ID/비밀번호 입력 칸, 로그인 버튼, 로그인 유지/IP 보안 옵션, 회원가입/찾기 링크, Apple/Google/Line 소셜 로그인 버튼이 모두 포함됩니다.

**Why this approach:** coupang과 동일한 패턴. nlog.html의 HTML 구조(class/id)와 CSS 선택자가 1:1로 연결되어 있어 DOM 구조는 완전히 보존. 4개 CSS 파일(nlogin.css 2836줄 + global_login_dark.css 391줄 + nloginline#1.css 16줄 + nloginline#2.css 19줄)을 하나로 병합하고, 외부 JS만 제거.

**What it will NOT do:** 실제로 로그인되지는 않습니다 (form submit 동작 없음). Apple/Google/Line 소셜 버튼은 눌러도 반응 없음. Naver 서버로 데이터를 전송하지 않음.

**Effort:** Medium
**Risk:** Low — coupang과 동일한 방식. CSS는 그대로 병합, HTML에서 외부 리소스만 제거.
**Decisions to sanity-check:** 스프라이트 이미지가 CDN(ssl.pstatic.net)에서 로드됨. 다크모드 CSS(global_login_dark.css)도 포함되어 media query prefers-color-scheme 대응 가능.

Your next move: approve or `$start-work`.

---

> TL;DR (machine): Medium effort, Low risk — 정적 Naver 로그인 페이지 clone. 4개 CSS 병합 + HTML에서 외부 JS/CDN 리소스 제거.

## Scope
### Must have
- `f_template/naver/login.html` — nlog.html 기반, 외부 JS 제거, 폼 구조 보존
- `f_template/naver/login.css` — nlogin.css + global_login_dark.css + nloginline#1.css + nloginline#2.css 병합
- Naver 로고 (스프라이트 CDN 이미지 유지)
- ID/비밀번호 입력 폼 (floating label + input_text)
- 로그인 유지 체크박스 + IP 보안 토글 스위치
- "로그인" 버튼 (초록색 #03c75a)
- ID 검색 / 비밀번호 검색 / 회원 가입 링크
- Apple/Google/Line 소셜 로그인 버튼
- 푸터 (스마트 고객 서비스 / 온라인 도움말 / 언어 선택 / © NAVER Corp.)
- 다크모드 테마 지원 (data-theme 속성 + dark.css 통합)

### Must NOT have (guardrails, anti-slop, scope boundaries)
- ❌ 외부 JS 스크립트 일체 (nlog.js, gfp-display-sdk.js, wtm.pstatic.net, ntm_scripts, synchronizer.js, gfp-core.js, passkeyApi.js, login.js, ncaptcha-api.js 등)
- ❌ 추적/분석/광고 스크립트 및 nclicks
- ❌ iframe 요소 (ncaptcha-iframe, banner iframe)
- ❌ 광고 배너 (banner_wrap, banner_inner, data-ad-unit)
- ❌ ncaptcha 관련 모든 요소 (ncaptcha-split hidden input, ncaptcha-iframe, ncaptcha-api script)
- ❌ 실제 로그인/제출 기능 (form action 유지하되 동작 없음)
- ❌ passkey 관련 (passkeyBtn, passkeyApi.js, passkey login section)
- ❌ Naver CDN JS 라이브러리 (CSS 폰트/CDN 이미지는 유지)
- ❌ HTML 구조(class/id) 변경 (CSS와의 매핑 유지)
- ❌ data-i18n 속성 제거 (다국어 관련 — 있어도 무해하나 JS 없으면 무의미하므로 제거해도 됨. 구조 유지 차원에서 유지 가능)
- ❌ `<html>`의 data-i18n-json 속성 제거

## Verification strategy
- Test decision: none (정적 HTML+CSS)
- Evidence: .omo/evidence/task-1-naver-login-page.txt, task-2-naver-login-page.txt

## Todos
- [ ] 1. `f_template/naver/login.css`: 4개 CSS 파일 병합
  What to do / Must NOT do:
    1. `nlogin.css` (2836 lines) → 그대로 사용
    2. `global_login_dark.css` (391 lines) → 그대로 사용 (두 번째에 배치 — 다크모드 스프라이트 오버라이드)
    3. `nloginline#1.css` (16 lines, 광고 스타일) → 세 번째에 배치
    4. `nloginline#2.css` (19 lines, 배너 이미지 스타일) → 마지막에 배치
    5. 네 파일을 순서대로 결합하여 `f_template/naver/login.css`로 저장
    Must NOT: CSS 선택자/속성 값 변경 금지, CDN URL 변경 금지
  References:
    - f_template/naver/nlogin.css (2836 lines)
    - f_template/naver/global_login_dark.css (391 lines)
    - f_template/naver/nloginline#1.css (16 lines)
    - f_template/naver/nloginline#2.css (19 lines)
  Acceptance criteria:
    1. `wc -l f_template/naver/login.css` >= 3200 (4개 파일 합계)
    2. `head -20 f_template/naver/login.css`에 `@charset "UTF-8"`과 `@font-face` 포함
    3. `tail -20 f_template/naver/login.css`에 `image_container_p462t1w` 포함
    4. `grep -c "naver_logo" f_template/naver/login.css` >= 5
    5. 모든 CDN URL(ssl.pstatic.net)이 그대로 존재
  QA scenarios: happy — 파일 생성 확인, 키 선택자 존재 확인, CDN URL 보존 확인. Evidence: .omo/evidence/task-1-naver-login-page.txt
  Commit: Y | feat(naver): Add merged login.css from 4 source CSS files

- [ ] 2. `f_template/naver/login.html`: nlog.html 정제
  What to do / Must NOT do:
    1. nlog.html을 읽어서 f_template/naver/login.html로 저장
    2. 제거할 항목:
       - `<head>` 내 `<script>` 태그 4개 (nlog.js, gfp-display-sdk, wtm.pstatic.net, synchronizer.js) — nlog.html:8
       - `<html>`의 `data-i18n-json` 속성
       - `<body>` 바로 다음 `<script>` 2개 (ntm_scripts, prefers-color-scheme dark 스크립트) — nlog.html:11
       - `<form>` 내 passkey 관련: `passkeyBtn_column`, `passkeyBtn_row` li 태그와 그 내용 (nlog.html:118-122, 132-136)
       - QR/OTP 관련: `qronetime_link` 섹션들 (nlog.html:145-161) — 버튼은 유지해도 무방하나 JS 없으므로 제거
       - 광고 배너: `banner_wrap` 전체 (nlog.html:201-203)
       - 하단 hidden input들: nclicks_nsc, removeLink, hide_util, ncaptchaSplit, onload_pk, locale, adult_surl_v2, ispopup, isPc — JS 종속 (nlog.html:232-241)
       - nv_stat div (nlog.html:241)
       - 모든 외부 `<script>` 태그: gfp-core.js, passkeyApi.js, login.js, ncaptcha-api.js (nlog.html:242-245)
       - ncaptcha-iframe (nlog.html:249)
    3. CSS 참조 변경:
       - `<link rel="stylesheet" type="text/css" href="/login/css/v3/global_login.css">` (nlog.html:6)
         → `<link rel="stylesheet" type="text/css" href="login.css">`
       - `<link rel="stylesheet" type="text/css" href="/login/css/v3/global_login_dark.css">` (nlog.html:7)
         → 제거 (login.css에 통합됨)
    4. `data-i18n` 속성은 유지해도 무방 (시각적 영향 없음)
    5. form action 유지 (동작하지 않음)
    6. HTML 구조(class/id)는 절대 변경 금지
    Must NOT: class/id 속성 변경 금지, form 구조 변경 금지, 시각적 요소(로고, 소셜 로그인 아이콘, 스프라이트) 제거 금지
  References:
    - f_template/naver/nlog.html (249 lines)
    - f_template/naver/login.css (Todo 1 산출물)
  Acceptance criteria:
    1. `grep -c "<script" f_template/naver/login.html`가 0
    2. `grep "login.css" f_template/naver/login.html`가 로컬 CSS 참조 확인 (딱 1개)
    3. `grep -c "ssl.pstatic.net" f_template/naver/login.html` > 0 (CDN 이미지 유지)
    4. HTML에 class="naver_logo", id="id", id="pw" 존재
    5. 외부 `<script src=` 참조가 하나도 없음
    6. "로그인" 텍스트를 가진 버튼 존재
  QA scenarios: happy — HTML 파일 생성, 키 요소 존재 확인, 외부 script 0개 확인. Evidence: .omo/evidence/task-2-naver-login-page.txt
  Commit: Y | feat(naver): Create static login page from nlog.html without external JS

## Final verification wave
- [ ] F1. Plan compliance audit — Must have 전부 충족, Must NOT have 위반 없음
- [ ] F2. Code quality review — CSS 파일 병합 상태, HTML 구조 무결성
- [ ] F3. Real manual QA — Naver 로그인 페이지 시각적 일치 확인 (로고, 폼, 버튼, 소셜 로그인, 푸터)
- [ ] F4. Scope fidelity — 외부 JS 0개, CDN CSS 참조 없음, CDN 이미지만 유지

## Commit strategy
- Todo 1 완료: feat(naver): Add merged login.css from 4 source CSS files
- Todo 2 완료: feat(naver): Create static login page from nlog.html without external JS
