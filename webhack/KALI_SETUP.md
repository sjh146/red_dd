# 칼리 리눅스에서 DOM XSS Scanner 실행하기

## ✅ 호환성 확인

칼리 리눅스에서 이 스크립트를 실행할 수 있습니다! Python 스크립트이므로 대부분의 리눅스 배포판에서 동일하게 작동합니다.

---

## 📋 사전 요구사항

### 1. Python 버전 확인

```bash
python3 --version
# 또는
python --version
```

**필요한 버전:** Python 3.6 이상

칼리 리눅스는 기본적으로 Python 3가 설치되어 있습니다.

---

### 2. 필요한 패키지 확인 및 설치

#### 필요한 패키지:
- `requests` - HTTP 요청
- `beautifulsoup4` - HTML 파싱

#### 설치 방법:

```bash
# 방법 1: pip 사용 (권장)
pip3 install requests beautifulsoup4

# 또는
pip install requests beautifulsoup4

# 방법 2: apt를 통한 설치 (칼리 리눅스)
sudo apt update
sudo apt install python3-requests python3-bs4

# 방법 3: requirements.txt 사용
pip3 install -r requirements.txt
```

---

## 🚀 실행 방법

### 1. 스크립트 파일 권한 설정

```bash
# 실행 권한 부여
chmod +x dom_xss_scanner.py

# 또는 Python으로 직접 실행
python3 dom_xss_scanner.py <URL>
```

### 2. 기본 실행

```bash
# 기본 실행
python3 dom_xss_scanner.py https://example.com

# 파라미터가 있는 URL
python3 dom_xss_scanner.py "https://example.com/page?test=123"
```

### 3. 실행 예시

```bash
# 칼리 리눅스 터미널에서
cd /path/to/webhack
python3 dom_xss_scanner.py https://oauth.kepco.co.kr/ksso/front/MB/LG/login.do
```

---

## 🔧 칼리 리눅스 특화 설정

### 1. 칼리 리눅스에 기본 설치된 도구 활용

칼리 리눅스에는 이미 많은 보안 도구가 설치되어 있습니다:

```bash
# 칼리 리눅스 기본 도구들
which python3
which pip3
which curl
which wget

# Python 패키지 확인
pip3 list | grep -i requests
pip3 list | grep -i beautifulsoup
```

### 2. 가상 환경 사용 (권장)

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 패키지 설치
pip install requests beautifulsoup4

# 스크립트 실행
python3 dom_xss_scanner.py https://example.com

# 가상 환경 비활성화
deactivate
```

---

## 🐛 문제 해결

### 문제 1: `pip3: command not found`

```bash
# pip 설치
sudo apt update
sudo apt install python3-pip
```

### 문제 2: `ModuleNotFoundError: No module named 'requests'`

```bash
# 패키지 설치
pip3 install requests beautifulsoup4

# 또는 시스템 패키지로 설치
sudo apt install python3-requests python3-bs4
```

### 문제 3: 권한 오류

```bash
# 사용자 디렉토리에 설치 (권장)
pip3 install --user requests beautifulsoup4

# 또는 sudo 사용 (비권장)
sudo pip3 install requests beautifulsoup4
```

### 문제 4: SSL 인증서 오류

칼리 리눅스에서 일부 사이트에 접속할 때 SSL 인증서 오류가 발생할 수 있습니다:

```bash
# 스크립트 수정 필요 (dom_xss_scanner.py)
# requests.get() 호출 시 verify=False 추가
# 또는 시스템 인증서 업데이트
sudo apt update
sudo apt install ca-certificates
```

---

## 📝 칼리 리눅스에서의 활용 예시

### 1. 칼리 리눅스 기본 도구와 연동

```bash
# 1. Burp Suite와 연동
# Burp Suite에서 타겟 URL 확인 후
python3 dom_xss_scanner.py <Burp에서_확인한_URL>

# 2. 칼리 리눅스의 웹 스캐너와 연동
# OWASP ZAP, Nikto 등과 함께 사용 가능

# 3. 스크립트 결과를 파일로 저장
python3 dom_xss_scanner.py https://example.com > scan_results.txt

# 4. 여러 URL 일괄 스캔
for url in $(cat urls.txt); do
    echo "Scanning: $url"
    python3 dom_xss_scanner.py "$url"
done
```

### 2. 칼리 리눅스 터미널에서 실행

```bash
# 칼리 리눅스 터미널 (bash)
cd ~/red_dd/webhack
python3 dom_xss_scanner.py https://example.com
```

---

## 🔒 보안 주의사항

칼리 리눅스는 보안 테스트용 배포판입니다:

1. **합법적인 테스트만 수행하세요**
   - 본인 소유의 시스템
   - 명시적 허가를 받은 시스템
   - 합법적인 보안 테스트 환경

2. **네트워크 설정 확인**
   - 칼리 리눅스는 기본적으로 많은 네트워크 도구를 실행합니다
   - 방화벽 설정을 확인하세요

3. **프록시 설정**
   - Burp Suite나 OWASP ZAP와 함께 사용 시 프록시 설정 필요

---

## 📊 실행 결과 예시

칼리 리눅스에서 실행하면 동일한 결과를 얻을 수 있습니다:

```
================================================================================
🔍 DOM XSS Scanner 시작
================================================================================
[*] 타겟 URL: https://example.com

[1/5] HTTP 요청/응답 분석 중...
[+] Status Code: 200
[+] Content-Type: text/html

[2/5] JavaScript 파일 추출 중...
[*] 외부 JavaScript 파일: 3개
    - https://example.com/js/app.js
    - https://example.com/js/jquery.min.js
    - https://example.com/js/utils.js

[3/5] 인라인 JavaScript 분석 중...
...

[5/5] 취약점 리포트 생성 중...
```

---

## ✅ 체크리스트

실행 전 확인사항:

- [ ] Python 3 설치 확인 (`python3 --version`)
- [ ] pip3 설치 확인 (`pip3 --version`)
- [ ] 필요한 패키지 설치 (`pip3 install requests beautifulsoup4`)
- [ ] 스크립트 파일 권한 확인 (`chmod +x dom_xss_scanner.py`)
- [ ] 네트워크 연결 확인
- [ ] 타겟 URL 접근 가능 확인

---

## 💡 팁

1. **칼리 리눅스 터미널 색상**
   - 칼리 리눅스는 기본적으로 색상 출력을 지원합니다
   - 스크립트의 출력이 더 보기 좋게 표시됩니다

2. **칼리 리눅스 도구 통합**
   - 이 스크립트는 칼리 리눅스의 다른 보안 도구들과 함께 사용할 수 있습니다
   - Burp Suite, OWASP ZAP, Nikto 등과 연동 가능

3. **자동화 스크립트**
   - 칼리 리눅스의 bash 스크립트와 함께 사용하여 자동화 가능

---

## 🎯 결론

**칼리 리눅스에서 완벽하게 실행 가능합니다!**

Python 스크립트이므로 플랫폼 독립적이며, 필요한 패키지만 설치하면 바로 사용할 수 있습니다.

