import requests
from bs4 import BeautifulSoup
import re

# 1. 세션 객체 생성 (쿠키 자동 유지)
session = requests.Session()

# 2. 로그인 페이지 GET
login_url = "https://oauth.kepco.co.kr/ksso/front/MB/LG/login.do"
print(f"[*] 접속 중: {login_url}")

try:
    response = session.get(login_url, timeout=10)
    print(f"[+] GET 요청 성공 (Status: {response.status_code})")
except Exception as e:
    print(f"[-] GET 요청 실패: {e}")
    exit(1)

# 로그인 전 쿠키 저장 (비교용)
cookies_before_login = {}
for cookie in session.cookies:
    cookies_before_login[cookie.name] = cookie.value

print(f"\n[*] 로그인 전 쿠키 ({len(cookies_before_login)}개):")
for name, value in cookies_before_login.items():
    print(f"    - {name}: {value[:50]}...")
    if "session" in name.lower() or "jsessionid" in name.lower():
        print(f"      ⚠️  이것은 세션 추적 쿠키입니다 (로그인 전에도 발급됨)")

# 3. CSRF 토큰 파싱 (강화된 검색)
soup = BeautifulSoup(response.text, "html.parser")

print("\n[*] CSRF 토큰 검색 중...")

# 다양한 CSRF 토큰 필드명 시도
csrf_field_names = [
    "csrf_token",
    "_token",
    "csrf",
    "authenticity_token",
    "csrfmiddlewaretoken",
    "token",
    "_csrf",
    "csrfToken",
    "X-CSRF-Token",
    "XSRF-TOKEN",
    "csrf-token",
    "_csrf_token",
    "csrfToken",
    "csrftoken"
]

csrf_value = None
csrf_field_found = None
csrf_source = None

# 방법 1: Input 태그의 name 속성으로 검색
print("[*] 방법 1: Input 태그 name 속성 검색")
for field_name in csrf_field_names:
    # name 속성으로 검색
    csrf_token = soup.find("input", {"name": field_name})
    if csrf_token:
        csrf_value = csrf_token.get("value")
        csrf_field_found = field_name
        csrf_source = "input[name]"
        print(f"    ✅ 발견: {field_name} = {csrf_value[:30]}...")
        break
    
    # id 속성으로도 검색
    csrf_token = soup.find("input", {"id": field_name})
    if csrf_token:
        csrf_value = csrf_token.get("value")
        csrf_field_found = field_name
        csrf_source = "input[id]"
        print(f"    ✅ 발견 (id): {field_name} = {csrf_value[:30]}...")
        break

# 방법 2: Hidden input에서 모든 토큰 후보 찾기
if not csrf_value:
    print("[*] 방법 2: Hidden input 전체 검색")
    hidden_inputs = soup.find_all("input", type="hidden")
    print(f"    - Hidden input 개수: {len(hidden_inputs)}")
    
    for hidden in hidden_inputs:
        name = hidden.get("name", "")
        value = hidden.get("value", "")
        
        # 토큰 후보: 길이가 10자 이상이고, 알파벳/숫자 조합
        if value and len(value) > 10:
            # CSRF 토큰처럼 보이는 패턴 확인
            if re.match(r'^[A-Za-z0-9+/=_-]+$', value):
                print(f"    - 후보 발견: name='{name}', value={value[:30]}...")
                
                # 필드명에 토큰 관련 키워드가 있으면 우선 선택
                if any(keyword in name.lower() for keyword in ["token", "csrf", "auth", "security"]):
                    csrf_value = value
                    csrf_field_found = name
                    csrf_source = "hidden_input_pattern"
                    print(f"    ✅ CSRF 토큰으로 추정: {name}")
                    break

# 방법 3: Meta 태그에서 검색
if not csrf_value:
    print("[*] 방법 3: Meta 태그 검색")
    meta_tags = soup.find_all("meta")
    for meta in meta_tags:
        meta_name = meta.get("name", "").lower()
        meta_content = meta.get("content", "")
        
        if any(keyword in meta_name for keyword in ["csrf", "token"]) and meta_content:
            csrf_value = meta_content
            csrf_field_found = meta_name
            csrf_source = "meta_tag"
            print(f"    ✅ Meta 태그에서 발견: {meta_name} = {meta_content[:30]}...")
            break

# 방법 4: JavaScript 변수에서 검색
if not csrf_value:
    print("[*] 방법 4: JavaScript 변수 검색")
    scripts = soup.find_all("script")
    for script in scripts:
        script_text = script.string or ""
        if script_text:
            # CSRF 토큰 변수 패턴 찾기
            patterns = [
                r'csrf[_-]?token\s*[:=]\s*["\']([^"\']+)["\']',
                r'csrf[_-]?token\s*[:=]\s*["\']([^"\']+)["\']',
                r'token\s*[:=]\s*["\']([A-Za-z0-9+/=_-]{20,})["\']',
                r'X-CSRF-Token["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, script_text, re.I)
                if match:
                    csrf_value = match.group(1)
                    csrf_field_found = "javascript_variable"
                    csrf_source = "javascript"
                    print(f"    ✅ JavaScript에서 발견: {csrf_value[:30]}...")
                    break
            
            if csrf_value:
                break

# 방법 5: Data 속성에서 검색
if not csrf_value:
    print("[*] 방법 5: Data 속성 검색")
    elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
    for elem in elements_with_data:
        for attr_name, attr_value in elem.attrs.items():
            if attr_name.startswith('data-') and any(keyword in attr_name.lower() for keyword in ["csrf", "token"]):
                if isinstance(attr_value, str) and len(attr_value) > 10:
                    csrf_value = attr_value
                    csrf_field_found = attr_name
                    csrf_source = "data_attribute"
                    print(f"    ✅ Data 속성에서 발견: {attr_name} = {csrf_value[:30]}...")
                    break
        if csrf_value:
            break

# 방법 6: 쿠키에서 검색
if not csrf_value:
    print("[*] 방법 6: 쿠키에서 검색")
    for cookie in session.cookies:
        cookie_name = cookie.name.lower()
        if any(keyword in cookie_name for keyword in ["csrf", "token", "xsrf"]):
            csrf_value = cookie.value
            csrf_field_found = cookie.name
            csrf_source = "cookie"
            print(f"    ✅ 쿠키에서 발견: {cookie.name} = {csrf_value[:30]}...")
            break

# 방법 7: 응답 헤더에서 검색
if not csrf_value:
    print("[*] 방법 7: 응답 헤더 검색")
    for header_name, header_value in response.headers.items():
        if any(keyword in header_name.lower() for keyword in ["csrf", "token", "xsrf"]):
            csrf_value = header_value
            csrf_field_found = header_name
            csrf_source = "response_header"
            print(f"    ✅ 헤더에서 발견: {header_name} = {csrf_value[:30]}...")
            break

# 결과 출력
print(f"\n[+] CSRF Token: {csrf_value if csrf_value else 'None'}")
if csrf_value:
    print(f"    - 필드명/소스: {csrf_field_found}")
    print(f"    - 발견 위치: {csrf_source}")
    print(f"    - 값 (전체): {csrf_value}")
else:
    print(f"    - ⚠️  CSRF 토큰을 찾지 못했습니다.")
    print(f"    - 가능한 이유:")
    print(f"      1. 실제로 CSRF 보호가 없을 수 있음")
    print(f"      2. JavaScript로 동적으로 생성되어 초기 HTML에 없음")
    print(f"      3. AJAX 요청으로 별도 엔드포인트에서 가져옴")
    print(f"      4. 필드명이 예상과 다름")

# 4. 로그인 폼 필드 확인
print("\n[*] 로그인 폼 분석:")
form = soup.find("form")
if form:
    print(f"    - Form action: {form.get('action', 'N/A')}")
    print(f"    - Form method: {form.get('method', 'N/A')}")
    form_action = form.get('action', '')
    if form_action and not form_action.startswith('http'):
        # 상대 경로인 경우 절대 경로로 변환
        from urllib.parse import urljoin
        form_action = urljoin(login_url, form_action)
        print(f"    - 절대 경로: {form_action}")
    inputs = form.find_all("input") if form else []
    print(f"    - Input 필드 개수: {len(inputs)}")
    for inp in inputs:
        inp_type = inp.get("type", "text")
        inp_name = inp.get("name", "")
        inp_id = inp.get("id", "")
        print(f"      * type={inp_type}, name={inp_name}, id={inp_id}")
else:
    print("    - Form 태그를 찾을 수 없음")
    print("    - 페이지의 모든 input 필드 검색 중...")
    all_inputs = soup.find_all("input")
    print(f"    - 전체 Input 필드 개수: {len(all_inputs)}")
    for inp in all_inputs:
        inp_type = inp.get("type", "text")
        inp_name = inp.get("name", "")
        inp_id = inp.get("id", "")
        inp_class = inp.get("class", [])
        if inp_name or inp_id:
            print(f"      * type={inp_type}, name={inp_name}, id={inp_id}, class={inp_class}")
    
    # JavaScript로 생성되는 폼 감지
    scripts = soup.find_all("script")
    print(f"\n    - Script 태그 개수: {len(scripts)}")
    for script in scripts:
        script_text = script.string or ""
        if script_text:
            # 로그인 관련 키워드 찾기
            if any(keyword in script_text.lower() for keyword in ["login", "submit", "form", "username", "password", "userid", "userid"]):
                print(f"      * 로그인 관련 JavaScript 발견 (길이: {len(script_text)}자)")
                # 필드명 패턴 찾기
                field_patterns = re.findall(r'(?:name|id|field)\s*[:=]\s*["\']([^"\']+)["\']', script_text, re.I)
                if field_patterns:
                    print(f"        - 발견된 필드명 패턴: {set(field_patterns[:5])}")

# 5. 로그인 데이터 구성 (다양한 필드명 시도)
# 일반적인 로그인 필드명 패턴
username_fields = ["username", "userid", "user_id", "user", "id", "login_id", "email", "account"]
password_fields = ["password", "passwd", "pass", "pwd"]

# 실제 페이지에서 찾은 필드명 사용
actual_username_field = None
actual_password_field = None

if form:
    form_inputs = form.find_all("input")
else:
    form_inputs = soup.find_all("input")

for inp in form_inputs:
    inp_name = inp.get("name", "").lower()
    inp_id = inp.get("id", "").lower()
    inp_type = inp.get("type", "").lower()
    
    # 사용자명 필드 찾기
    if not actual_username_field:
        if inp_type in ["text", "email"]:
            if any(field in inp_name for field in username_fields) or any(field in inp_id for field in username_fields):
                actual_username_field = inp.get("name") or inp.get("id")
                print(f"[*] 사용자명 필드 발견: {actual_username_field}")
    
    # 비밀번호 필드 찾기
    if not actual_password_field:
        if inp_type == "password":
            actual_password_field = inp.get("name") or inp.get("id")
            print(f"[*] 비밀번호 필드 발견: {actual_password_field}")

# 필드명이 없으면 기본값 사용
if not actual_username_field:
    actual_username_field = "username"
if not actual_password_field:
    actual_password_field = "password"

payload = {
    actual_username_field: "testuser",
    actual_password_field: "testpass",
}

if csrf_value:
    payload[csrf_field_found] = csrf_value

print(f"\n[*] 전송할 데이터: {payload}")

# 6. POST 요청 (Form action이 있으면 그것 사용)
post_url = login_url
if form and form.get('action'):
    form_action = form.get('action')
    if not form_action.startswith('http'):
        from urllib.parse import urljoin
        post_url = urljoin(login_url, form_action)
    else:
        post_url = form_action
    print(f"[*] Form action URL 사용: {post_url}")

print(f"\n[*] POST 요청 전송 중... (URL: {post_url})")
try:
    post_response = session.post(post_url, data=payload, allow_redirects=False, timeout=10)
except Exception as e:
    print(f"[-] POST 요청 실패: {e}")
    exit(1)

# 7. 결과 분석
print(f"\n[+] Status Code: {post_response.status_code}")
print(f"[+] Response Headers:")
for key, value in post_response.headers.items():
    print(f"    - {key}: {value}")

# 쿠키 확인 및 비교
print(f"\n[*] 로그인 후 쿠키 분석:")
cookies_after_login = {}
for cookie in session.cookies:
    cookies_after_login[cookie.name] = cookie.value

if cookies_after_login:
    print(f"    - 총 쿠키 개수: {len(cookies_after_login)}개")
    
    # 로그인 전후 쿠키 비교
    new_cookies = {}
    changed_cookies = {}
    same_cookies = {}
    
    for name, value in cookies_after_login.items():
        if name not in cookies_before_login:
            new_cookies[name] = value
        elif cookies_before_login[name] != value:
            changed_cookies[name] = {
                "before": cookies_before_login[name],
                "after": value
            }
        else:
            same_cookies[name] = value
    
    # 새로 생성된 쿠키 (로그인 성공 시 생성될 가능성 높음)
    if new_cookies:
        print(f"\n    ✅ 새로 생성된 쿠키 ({len(new_cookies)}개) - 로그인 성공 가능성 높음:")
        for name, value in new_cookies.items():
            print(f"      * {name}: {value[:50]}...")
            # 인증 관련 쿠키인지 확인
            if any(keyword in name.lower() for keyword in ["auth", "login", "token", "session", "user", "member"]):
                print(f"        🔐 인증 관련 쿠키로 추정됨!")
    
    # 변경된 쿠키 (세션 갱신 등)
    if changed_cookies:
        print(f"\n    🔄 변경된 쿠키 ({len(changed_cookies)}개):")
        for name, values in changed_cookies.items():
            print(f"      * {name}:")
            print(f"        - 이전: {values['before'][:30]}...")
            print(f"        - 현재: {values['after'][:30]}...")
            if "session" in name.lower() or "jsessionid" in name.lower():
                print(f"        ⚠️  JSESSIONID는 로그인 전에도 발급되는 세션 쿠키입니다")
                print(f"        ⚠️  값이 변경되었다면 세션이 갱신되었을 수 있습니다")
    
    # 동일한 쿠키 (로그인 전에도 있던 것)
    if same_cookies:
        print(f"\n    📌 동일한 쿠키 ({len(same_cookies)}개) - 로그인 전에도 존재:")
        for name, value in same_cookies.items():
            print(f"      * {name}: {value[:50]}...")
            if "session" in name.lower() or "jsessionid" in name.lower():
                print(f"        ℹ️  JSESSIONID는 세션 추적용 쿠키 (로그인 성공 여부와 무관)")
    
    # 인증 관련 쿠키만 필터링
    auth_related = {}
    for name, value in cookies_after_login.items():
        if any(keyword in name.lower() for keyword in ["auth", "login", "token", "user", "member", "credential"]):
            if name not in cookies_before_login or cookies_before_login[name] != value:
                auth_related[name] = value
    
    if auth_related:
        print(f"\n    🔐 인증 관련 쿠키 변화 ({len(auth_related)}개):")
        for name, value in auth_related.items():
            print(f"      * {name}: {value[:50]}...")
            if name in new_cookies:
                print(f"        ✅ 새로 생성됨 - 로그인 성공 가능성 높음!")
            elif name in changed_cookies:
                print(f"        🔄 값 변경됨 - 인증 상태 업데이트 가능성")
else:
    print("    - 쿠키 없음")

# 응답 본문 분석
response_text = post_response.text
print(f"\n[*] 응답 본문 길이: {len(response_text)}자")
print(f"[*] 응답 본문 (처음 1000자):")
print("-" * 50)
print(response_text[:1000])
print("-" * 50)

# 응답 본문에서 에러/성공 메시지 찾기
post_soup = BeautifulSoup(response_text, "html.parser")

# 에러 메시지 찾기 (더 다양한 패턴)
error_patterns = [
    r"오류[^<]*",
    r"에러[^<]*",
    r"error[^<]*",
    r"실패[^<]*",
    r"failed[^<]*",
    r"invalid[^<]*",
    r"잘못[^<]*",
    r"확인[^<]*",
    r"입력[^<]*",
    r"일치[^<]*"
]

found_errors = []
for pattern in error_patterns:
    matches = re.findall(pattern, response_text, re.I)
    found_errors.extend(matches[:2])  # 각 패턴당 최대 2개

if found_errors:
    print(f"\n[!] 발견된 에러/경고 메시지:")
    for error in set(found_errors[:5]):  # 중복 제거 후 최대 5개
        error_clean = error.strip()[:100]
        print(f"    - {error_clean}")

# 성공 메시지 찾기
success_patterns = [
    r"환영[^<]*",
    r"welcome[^<]*",
    r"로그인[^<]*성공[^<]*",
    r"login[^<]*success[^<]*",
    r"대시보드[^<]*",
    r"dashboard[^<]*"
]

found_success = []
for pattern in success_patterns:
    matches = re.findall(pattern, response_text, re.I)
    found_success.extend(matches[:2])

if found_success:
    print(f"\n[+] 발견된 성공 메시지:")
    for success in set(found_success[:5]):
        success_clean = success.strip()[:100]
        print(f"    - {success_clean}")

# 페이지 제목 확인
post_title = post_soup.find("title")
if post_title:
    print(f"\n[*] 응답 페이지 제목: {post_title.text.strip()}")

# 8. 로그인 성공 여부 판단
if post_response.status_code == 302:
    location = post_response.headers.get("Location", "")
    print(f"\n[+] Redirect detected!")
    print(f"    - Location: {location}")
    
    # 리다이렉트 후 최종 페이지 확인
    if location:
        print(f"\n[*] 리다이렉트 후 페이지 확인 중...")
        try:
            final_response = session.get(location, allow_redirects=True, timeout=10)
            print(f"    - 최종 URL: {final_response.url}")
            print(f"    - 최종 Status: {final_response.status_code}")
            
            # 로그인 성공 여부 힌트 찾기
            final_soup = BeautifulSoup(final_response.text, "html.parser")
            page_title = final_soup.find("title")
            if page_title:
                print(f"    - 페이지 제목: {page_title.text}")
            
            # 에러 메시지나 성공 메시지 찾기
            error_keywords = ["오류", "에러", "error", "실패", "failed", "invalid", "잘못"]
            success_keywords = ["환영", "welcome", "대시보드", "dashboard", "마이페이지"]
            
            page_text = final_response.text.lower()
            for keyword in error_keywords:
                if keyword.lower() in page_text:
                    print(f"    ⚠️  에러 키워드 발견: '{keyword}'")
                    break
            
            for keyword in success_keywords:
                if keyword.lower() in page_text:
                    print(f"    ✅ 성공 키워드 발견: '{keyword}'")
                    break
                    
        except Exception as e:
            print(f"    [-] 리다이렉트 후 페이지 확인 실패: {e}")
    
    # 쿠키 비교로 로그인 성공 여부 판단
    new_auth_cookies_302 = {}
    for name, value in cookies_after_login.items():
        if name not in cookies_before_login:
            if any(keyword in name.lower() for keyword in ["auth", "login", "token", "user", "member", "credential"]):
                new_auth_cookies_302[name] = value
    
    if new_auth_cookies_302:
        print(f"\n[+] 로그인 성공 가능성: 높음 (302 리다이렉트 + 새 인증 쿠키 생성)")
        print(f"    - 새 인증 쿠키: {list(new_auth_cookies_302.keys())}")
    elif session.cookies:
        # JSESSIONID만 있는 경우
        jsession_only = all("jsessionid" in c.name.lower() for c in session.cookies)
        if jsession_only:
            print(f"\n[?] 로그인 성공 여부 불확실: 302 리다이렉트되었지만 JSESSIONID만 존재")
            print(f"    - JSESSIONID는 로그인 전에도 발급되므로 성공 여부 판단 불가")
        else:
            print(f"\n[+] 로그인 성공 가능성: 중간 (302 리다이렉트 + 쿠키 존재)")
    else:
        print(f"\n[?] 로그인 성공 여부 불확실: 302 리다이렉트되었지만 쿠키 없음")
else:
    print(f"\n[*] Status Code 분석: {post_response.status_code}")
    
    # Status 200인 경우 추가 분석
    if post_response.status_code == 200:
        # 새로 생성된 인증 관련 쿠키 확인
        new_auth_cookies_200 = {}
        for name, value in cookies_after_login.items():
            if name not in cookies_before_login:
                if any(keyword in name.lower() for keyword in ["auth", "login", "token", "user", "member", "credential"]):
                    new_auth_cookies_200[name] = value
        
        if new_auth_cookies_200:
            print(f"\n    ✅ 새로 생성된 인증 쿠키 발견: {len(new_auth_cookies_200)}개")
            print(f"    → 로그인 성공 가능성 높음!")
            for name, value in new_auth_cookies_200.items():
                print(f"      * {name}: {value[:30]}...")
        else:
            # JSESSIONID만 있는지 확인
            jsession_only = all("jsessionid" in c.name.lower() or "wmonid" in c.name.lower() for c in session.cookies)
            if jsession_only and len(session.cookies) <= 2:
                print(f"\n    ⚠️  JSESSIONID/WMONID만 존재 (로그인 전에도 발급되는 세션 쿠키)")
                print(f"    → 로그인 성공 여부 판단 불가")
        
        # 리다이렉트가 JavaScript로 처리되는지 확인
        if "location.href" in response_text or "window.location" in response_text:
            redirect_match = re.search(r'(?:location\.href|window\.location)\s*=\s*["\']([^"\']+)["\']', response_text)
            if redirect_match:
                js_redirect = redirect_match.group(1)
                print(f"\n    - JavaScript 리다이렉트 발견: {js_redirect}")
                if not js_redirect.startswith('http'):
                    from urllib.parse import urljoin
                    js_redirect = urljoin(post_url, js_redirect)
                print(f"    - 절대 경로: {js_redirect}")
        
        # 로그인 실패 vs 성공 판단
        if found_errors:
            print(f"\n[-] Login failed: 에러 메시지 발견")
        elif found_success:
            print(f"\n[+] Login success 가능성: 성공 메시지 발견")
        elif new_auth_cookies_200:
            print(f"\n[+] Login success 가능성: 새 인증 쿠키 생성됨")
        else:
            print(f"\n[?] Login 성공 여부 불확실: 추가 검증 필요")
            print(f"    - JSESSIONID는 로그인 전에도 발급되므로 성공 여부 판단 불가")
            print(f"    - 인증 관련 새 쿠키나 에러/성공 메시지를 확인하세요")
    else:
        print(f"\n[-] Login failed or additional validation required")
        print(f"    - Status Code: {post_response.status_code}")
