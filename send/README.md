# 이메일 자동 전송 서버

여러 사람에게 자동으로 이메일을 보낼 수 있는 Flask 기반 REST API 서버입니다.

## 기능

- 여러 수신자에게 동시에 이메일 전송
- 텍스트 및 HTML 형식 이메일 지원
- 첨부 파일 지원
- 대량 이메일 개별 전송 (BCC 방식)
- REST API 엔드포인트 제공

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env.example` 파일을 `.env`로 복사하고 실제 값으로 수정하세요.

```bash
cp .env.example .env
```

`.env` 파일을 열어서 다음 정보를 입력하세요:
- `SMTP_SERVER`: SMTP 서버 주소 (예: smtp.gmail.com)
- `SMTP_PORT`: SMTP 포트 (예: 587)
- `SMTP_USERNAME`: 이메일 주소
- `SMTP_PASSWORD`: 이메일 비밀번호 또는 앱 비밀번호
- `FROM_EMAIL`: 발신자 이메일 주소

### Gmail 사용 시 주의사항

Gmail을 사용하는 경우:
1. Google 계정에서 2단계 인증을 활성화하세요
2. 앱 비밀번호를 생성하세요: [Google 계정 설정](https://myaccount.google.com/apppasswords)
3. 생성된 앱 비밀번호를 `SMTP_PASSWORD`에 입력하세요

## 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## API 사용법

### 1. 서버 상태 확인

```bash
GET /health
```

### 2. 여러 수신자에게 이메일 전송

```bash
POST /send-email
Content-Type: application/json

{
  "recipients": ["user1@example.com", "user2@example.com"],
  "subject": "이메일 제목",
  "body": "이메일 본문 텍스트",
  "body_html": "<h1>HTML 형식 본문</h1>",
  "attachments": ["/path/to/file.pdf"]
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "2명에게 이메일이 성공적으로 전송되었습니다.",
  "recipients": ["user1@example.com", "user2@example.com"]
}
```

### 3. 대량 이메일 개별 전송

각 수신자에게 개별적으로 이메일을 전송합니다 (BCC가 아닌 개별 전송).

```bash
POST /send-bulk
Content-Type: application/json

{
  "recipients": ["user1@example.com", "user2@example.com"],
  "subject": "이메일 제목",
  "body": "이메일 본문",
  "body_html": "<h1>HTML 본문</h1>",
  "attachments": ["/path/to/file.pdf"]
}
```

**응답 예시:**
```json
{
  "success": true,
  "total": 2,
  "success_count": 2,
  "fail_count": 0,
  "results": [
    {
      "recipient": "user1@example.com",
      "success": true,
      "message": "1명에게 이메일이 성공적으로 전송되었습니다."
    },
    {
      "recipient": "user2@example.com",
      "success": true,
      "message": "1명에게 이메일이 성공적으로 전송되었습니다."
    }
  ]
}
```

## cURL 예시

### 기본 이메일 전송
```bash
curl -X POST http://localhost:5000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user1@example.com", "user2@example.com"],
    "subject": "테스트 이메일",
    "body": "이것은 테스트 이메일입니다."
  }'
```

### HTML 이메일 전송
```bash
curl -X POST http://localhost:5000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user@example.com"],
    "subject": "HTML 이메일",
    "body": "텍스트 버전",
    "body_html": "<h1>HTML 버전</h1><p>이것은 HTML 형식의 이메일입니다.</p>"
  }'
```

### 첨부 파일 포함 이메일 전송
```bash
curl -X POST http://localhost:5000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user@example.com"],
    "subject": "첨부 파일 포함",
    "body": "첨부 파일을 확인하세요.",
    "attachments": ["/path/to/document.pdf"]
  }'
```

## Python 클라이언트 예시

```python
import requests

url = "http://localhost:5000/send-email"
data = {
    "recipients": ["user1@example.com", "user2@example.com"],
    "subject": "테스트 이메일",
    "body": "이것은 테스트 이메일입니다.",
    "body_html": "<h1>HTML 버전</h1><p>이것은 HTML 형식의 이메일입니다.</p>"
}

response = requests.post(url, json=data)
print(response.json())
```

## JavaScript 클라이언트 예시

```javascript
fetch('http://localhost:5000/send-email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    recipients: ['user1@example.com', 'user2@example.com'],
    subject: '테스트 이메일',
    body: '이것은 테스트 이메일입니다.',
    body_html: '<h1>HTML 버전</h1><p>이것은 HTML 형식의 이메일입니다.</p>'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## 주의사항

1. **보안**: 프로덕션 환경에서는 인증 토큰이나 API 키를 추가하세요.
2. **비율 제한**: 이메일 서비스 제공업체의 전송 제한을 확인하세요.
3. **스팸 필터**: 대량 이메일 전송 시 스팸 필터에 걸릴 수 있습니다.
4. **환경 변수**: `.env` 파일은 절대 Git에 커밋하지 마세요.

## 라이선스

MIT

