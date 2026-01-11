"""
DOM XSS Scanner
Burp Suite 워크플로우: HTTP → JavaScript → DOM XSS 탐지

기능:
1. HTTP 요청/응답 분석
2. JavaScript 파일 추출 및 분석
3. DOM 조작 코드 탐지 (document.write, innerHTML, eval 등)
4. 사용자 입력 소스 탐지 (location.hash, location.search 등)
5. XSS 페이로드 테스트
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, parse_qs
import json

class DOMXSSScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vulnerabilities = []
        self.js_files = []
        # 실습용: 모든 파일 분석 (라이브러리도 포함)
        self.library_patterns = []  # 빈 리스트로 설정하여 필터링 비활성화
        # 실습용: 모든 위험한 Sink 함수 포함
        self.dangerous_sinks = [
            'document.write',
            'document.writeln',
            'innerHTML',
            'outerHTML',
            'insertAdjacentHTML',
            'eval',
            'Function',  # 실습용: 포함
            'setTimeout',  # 실습용: 포함
            'setInterval',  # 실습용: 포함
            'location.href',  # 실습용: 포함
            'location.replace',  # 실습용: 포함
            'location.assign',  # 실습용: 포함
            'window.location',  # 실습용: 포함
            'document.location',  # 실습용: 포함
            'document.cookie',  # 실습용: 포함
            'document.domain',  # 실습용: 포함
            'document.open',  # 실습용: 포함
            'document.close',  # 실습용: 포함
            'document.execCommand',  # 실습용: 포함
            'document.createElement',  # 실습용: 포함
            'jQuery.html',
            'jQuery.append',
            'jQuery.prepend',
            'jQuery.after',
            'jQuery.before',
            'jQuery.insertAfter',
            'jQuery.insertBefore',
            'jQuery.wrap',
            'jQuery.wrapAll',
            'jQuery.wrapInner',
            '$.html',
            '$.append',
            '$.prepend',
            '$.after',
            '$.before',
            '$.insertAfter',
            '$.insertBefore',
            '$.wrap',
            '$.wrapAll',
            '$.wrapInner',
            'ReactDOM.render',
            'React.createElement',
            'ReactDOMServer.renderToString',
            'dangerouslySetInnerHTML',
            'v-html',
            'ng-bind-html',
            'angular.element',
            'Vue.compile',
            'DOMParser.parseFromString'
        ]
        self.user_input_sources = [
            'location.hash',
            'location.search',
            'location.href',
            'location.pathname',
            'document.URL',
            'document.documentURI',
            'document.baseURI',
            'window.location',
            'window.location.href',
            'window.location.search',
            'window.location.hash',
            'document.referrer',
            'document.cookie',
            'window.name',
            'history.pushState',
            'history.replaceState',
            'localStorage',
            'sessionStorage',
            'postMessage',
            'window.name',
            'location',
            'document.location',
            'document.URLUnencoded',
            'document.baseURI',
            'document.forms',
            'document.anchors',
            'document.links',
            'document.images',
            'document.embeds',
            'document.plugins',
            'document.scripts',
            'document.getElementById',
            'document.getElementsByName',
            'document.getElementsByTagName',
            'document.getElementsByClassName',
            'document.querySelector',
            'document.querySelectorAll',
            'jQuery',
            '$',
            'angular.element',
            'React',
            'Vue'
        ]
        self.xss_payloads = [
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '<script>alert(1)</script>',
            'javascript:alert(1)',
            '\'"><script>alert(1)</script>',
            '<iframe src=javascript:alert(1)>',
            '<body onload=alert(1)>',
            '<input onfocus=alert(1) autofocus>',
            '<select onfocus=alert(1) autofocus>',
            '<textarea onfocus=alert(1) autofocus>',
            '<keygen onfocus=alert(1) autofocus>',
            '<video><source onerror=alert(1)>',
            '<audio src=x onerror=alert(1)>',
            '<details open ontoggle=alert(1)>',
            '<marquee onstart=alert(1)>',
            '<math><mi//xlink:href="data:x,<script>alert(1)</script>">',
            '"><img src=x onerror=alert(1)>',
            '\'"><svg/onload=alert(1)>',
            '<svg/onload=alert(String.fromCharCode(88,83,83))>',
            '<img src=x id=dmFyIGE9YWxlcnQoZG9jdW1lbnQuZG9tYWluKTs= onerror=eval(atob(this.id))>'
        ]

    def scan(self):
        """메인 스캔 함수"""
        print("=" * 80)
        print("🔍 DOM XSS Scanner 시작")
        print("=" * 80)
        print(f"[*] 타겟 URL: {self.target_url}\n")
        
        # 1. HTTP 요청/응답 분석
        print("[1/5] HTTP 요청/응답 분석 중...")
        html_content = self.analyze_http_response()
        
        if not html_content:
            print("[-] HTTP 응답을 가져올 수 없습니다.")
            return
        
        # 2. JavaScript 파일 추출
        print("\n[2/5] JavaScript 파일 추출 중...")
        self.extract_js_files(html_content)
        
        # 3. 인라인 JavaScript 분석
        print("\n[3/5] 인라인 JavaScript 분석 중...")
        self.analyze_inline_js(html_content)
        
        # 4. DOM 조작 코드 탐지
        print("\n[4/5] DOM 조작 코드 탐지 중...")
        self.detect_dom_manipulation()
        
        # 5. 취약점 리포트
        print("\n[5/5] 취약점 리포트 생성 중...")
        self.generate_report()

    def analyze_http_response(self):
        """HTTP 요청/응답 분석"""
        try:
            response = self.session.get(self.target_url, timeout=10)
            print(f"[+] Status Code: {response.status_code}")
            print(f"[+] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"[+] Content-Length: {len(response.content)} bytes")
            
            # 응답 헤더 분석
            print(f"\n[*] 응답 헤더:")
            security_headers = ['X-XSS-Protection', 'Content-Security-Policy', 'X-Content-Type-Options']
            for header in security_headers:
                value = response.headers.get(header, 'Not Set')
                if value == 'Not Set':
                    print(f"    ⚠️  {header}: {value}")
                else:
                    print(f"    ✅ {header}: {value}")
            
            return response.text
        except Exception as e:
            print(f"[-] HTTP 요청 실패: {e}")
            return None

    def is_library_file(self, url):
        """라이브러리 파일인지 확인 (실습용: 항상 False 반환)"""
        # 실습용: 모든 파일 분석
        return False

    def extract_js_files(self, html_content):
        """HTML에서 JavaScript 파일 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 외부 JavaScript 파일
        script_tags = soup.find_all('script', src=True)
        print(f"[*] 외부 JavaScript 파일: {len(script_tags)}개")
        
        for script in script_tags:
            js_url = script.get('src')
            if js_url:
                absolute_url = urljoin(self.target_url, js_url)
                
                # 실습용: 모든 파일 분석
                self.js_files.append({
                    'type': 'external',
                    'url': absolute_url,
                    'tag': script
                })
                print(f"    - {absolute_url}")
        
        # 인라인 JavaScript
        inline_scripts = soup.find_all('script', src=False)
        print(f"[*] 인라인 JavaScript 블록: {len(inline_scripts)}개")
        
        for idx, script in enumerate(inline_scripts):
            js_code = script.string or ""
            if js_code.strip():
                self.js_files.append({
                    'type': 'inline',
                    'url': self.target_url,
                    'code': js_code,
                    'index': idx
                })
                print(f"    - 인라인 스크립트 #{idx + 1} ({len(js_code)} bytes)")

    def analyze_inline_js(self, html_content):
        """인라인 JavaScript 분석"""
        soup = BeautifulSoup(html_content, 'html.parser')
        inline_scripts = soup.find_all('script', src=False)
        
        for idx, script in enumerate(inline_scripts):
            js_code = script.string or ""
            if not js_code.strip():
                continue
            
            print(f"\n[*] 인라인 스크립트 #{idx + 1} 분석:")
            self.analyze_js_code(js_code, f"inline_script_{idx}")

    def detect_dom_manipulation(self):
        """DOM 조작 코드 탐지"""
        print("\n[*] DOM 조작 코드 탐지:")
        
        # 외부 JS 파일 분석
        for js_file in self.js_files:
            if js_file['type'] == 'external':
                try:
                    print(f"\n[*] 분석 중: {js_file['url']}")
                    response = self.session.get(js_file['url'], timeout=10)
                    if response.status_code == 200:
                        self.analyze_js_code(response.text, js_file['url'])
                except Exception as e:
                    print(f"    [-] 파일 다운로드 실패: {e}")
            elif js_file['type'] == 'inline':
                self.analyze_js_code(js_file['code'], f"inline_{js_file['index']}")

    def analyze_js_code(self, js_code, source):
        """JavaScript 코드 분석 (실습용: 모든 파일 분석)"""
        # 실습용: 라이브러리 파일도 분석
        
        # 위험한 Sink 함수 찾기
        for sink in self.dangerous_sinks:
            # 더 정확한 패턴 매칭
            if sink in ['innerHTML', 'outerHTML', 'insertAdjacentHTML']:
                # 할당 패턴만 찾기 (=, += 등)
                pattern = re.compile(r'\.' + re.escape(sink) + r'\s*[=+]', re.IGNORECASE)
            elif sink == 'eval':
                # eval( 패턴
                pattern = re.compile(r'\beval\s*\(', re.IGNORECASE)
            elif sink in ['document.write', 'document.writeln']:
                # document.write( 패턴
                pattern = re.compile(r'\b' + re.escape(sink) + r'\s*\(', re.IGNORECASE)
            elif sink.startswith('jQuery.') or sink.startswith('$.'):
                # jQuery 메서드 패턴
                pattern = re.compile(r'\b' + re.escape(sink) + r'\s*\(', re.IGNORECASE)
            else:
                pattern = re.compile(r'\b' + re.escape(sink) + r'\s*\(', re.IGNORECASE)
            
            matches = pattern.finditer(js_code)
            
            for match in matches:
                # 컨텍스트 추출 (앞뒤 300자로 확장)
                start = max(0, match.start() - 300)
                end = min(len(js_code), match.end() + 300)
                context = js_code[start:end]
                
                # 사용자 입력 소스 확인 (더 정확한 패턴)
                user_input_found = False
                input_source = None
                
                # Source와 Sink가 실제로 연결되어 있는지 확인
                for input_source_pattern in self.user_input_sources:
                    # Source 패턴 찾기
                    source_pattern = re.compile(
                        r'\b' + re.escape(input_source_pattern) + r'\b',
                        re.IGNORECASE
                    )
                    
                    if source_pattern.search(context):
                        # 실제 데이터 흐름 확인
                        # 예: location.hash가 innerHTML에 직접 할당되는지 확인
                        source_match = source_pattern.search(context)
                        sink_match_pos = match.start() - start
                        
                        # Source와 Sink 사이의 코드 확인
                        between_code = context[source_match.end():sink_match_pos]
                        
                        # 간단한 변수 할당 패턴 확인
                        # 예: var x = location.hash; ... innerHTML = x;
                        if re.search(r'=\s*[^;]*' + re.escape(input_source_pattern), between_code, re.IGNORECASE):
                            user_input_found = True
                            input_source = input_source_pattern
                            break
                        
                        # 직접 사용 패턴 확인
                        # 예: innerHTML = location.hash 또는 insertAdjacentHTML("afterend", location.pathname)
                        direct_patterns = [
                            # innerHTML = location.hash
                            r'\.' + re.escape(sink) + r'\s*=\s*[^=]*' + re.escape(input_source_pattern),
                            # insertAdjacentHTML("position", location.pathname)
                            r'\.' + re.escape(sink) + r'\s*\([^)]*' + re.escape(input_source_pattern),
                            # document.write(location.hash)
                            r'\b' + re.escape(sink) + r'\s*\([^)]*' + re.escape(input_source_pattern),
                            # eval(location.hash)
                            r'\beval\s*\([^)]*' + re.escape(input_source_pattern),
                        ]
                        
                        for direct_pattern in direct_patterns:
                            if re.search(direct_pattern, context, re.IGNORECASE):
                                user_input_found = True
                                input_source = input_source_pattern
                                break
                        
                        if user_input_found:
                            break
                
                # 취약점 발견
                if user_input_found:
                    line_num = js_code[:match.start()].count('\n') + 1
                    
                    # 중복 제거 (같은 위치의 같은 취약점)
                    is_duplicate = False
                    for existing_vuln in self.vulnerabilities:
                        if (existing_vuln['sink'] == sink and 
                            existing_vuln['source'] == input_source and
                            existing_vuln['location'] == source and
                            abs(existing_vuln['line'] - line_num) < 5):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        vulnerability = {
                            'type': 'DOM XSS',
                            'severity': 'High',
                            'sink': sink,
                            'source': input_source,
                            'location': source,
                            'line': line_num,
                            'context': context.strip(),
                            'payload': self.generate_payload(sink, input_source)
                        }
                        self.vulnerabilities.append(vulnerability)
                        
                        print(f"\n    ⚠️  취약점 발견!")
                        print(f"        - Sink: {sink}")
                        print(f"        - Source: {input_source}")
                        print(f"        - 위치: {source} (라인 {line_num})")
                        print(f"        - 컨텍스트: {context[:150]}...")
        
        # 실습용: 추가 패턴 검색 (모든 패턴 포함)
        # location.hash가 innerHTML에 직접 할당되는 경우
        if re.search(r'\.innerHTML\s*=\s*[^=]*location\.hash', js_code, re.IGNORECASE):
            line_num = js_code.find('location.hash')
            if line_num > 0:
                line_num = js_code[:line_num].count('\n') + 1
                print(f"    ⚠️  location.hash → innerHTML 직접 할당 발견: {source} (라인 {line_num})")
        
        # eval()에 사용자 입력이 직접 전달되는 경우
        if re.search(r'eval\s*\(\s*[^)]*location\.(hash|search)', js_code, re.IGNORECASE):
            line_num = js_code.find('eval')
            if line_num > 0:
                line_num = js_code[:line_num].count('\n') + 1
                print(f"    ⚠️  eval()에 사용자 입력 직접 전달 발견: {source} (라인 {line_num})")
        
        # 실습용: 추가 위험 패턴 검색
        # location.search/hash 직접 사용
        if re.search(r'location\.(hash|search)\s*[=:]', js_code, re.IGNORECASE):
            matches = list(re.finditer(r'location\.(hash|search)\s*[=:]', js_code, re.IGNORECASE))
            for match in matches[:3]:  # 최대 3개만 표시
                line_num = js_code[:match.start()].count('\n') + 1
                print(f"    ℹ️  location.{match.group(1)} 직접 사용 발견: {source} (라인 {line_num})")
        
        # document.cookie 직접 할당
        if re.search(r'document\.cookie\s*=', js_code, re.IGNORECASE):
            matches = list(re.finditer(r'document\.cookie\s*=', js_code, re.IGNORECASE))
            for match in matches[:3]:
                line_num = js_code[:match.start()].count('\n') + 1
                print(f"    ⚠️  document.cookie 직접 할당 발견: {source} (라인 {line_num})")
        
        # setTimeout/setInterval에 문자열 전달
        if re.search(r'(setTimeout|setInterval)\s*\(\s*["\']', js_code, re.IGNORECASE):
            matches = list(re.finditer(r'(setTimeout|setInterval)\s*\(\s*["\']', js_code, re.IGNORECASE))
            for match in matches[:3]:
                line_num = js_code[:match.start()].count('\n') + 1
                print(f"    ⚠️  {match.group(1)}에 문자열 전달 발견: {source} (라인 {line_num})")

    def generate_payload(self, sink, source):
        """XSS 페이로드 생성"""
        # source에 따라 다른 페이로드 생성
        if 'hash' in source.lower():
            return '#<img src=x onerror=alert(1)>'
        elif 'search' in source.lower() or 'query' in source.lower():
            return '?test=<img src=x onerror=alert(1)>'
        elif 'href' in source.lower():
            return 'javascript:alert(1)'
        else:
            return '<img src=x onerror=alert(1)>'

    def generate_report(self):
        """취약점 리포트 생성"""
        print("\n" + "=" * 80)
        print("📊 취약점 리포트")
        print("=" * 80)
        
        if not self.vulnerabilities:
            print("\n✅ 발견된 DOM XSS 취약점이 없습니다.")
            print("\n⚠️  주의: 이 스캐너는 정적 분석만 수행합니다.")
            print("   실제 취약점 확인을 위해서는 동적 테스트가 필요합니다.")
            return
        
        print(f"\n[!] 총 {len(self.vulnerabilities)}개의 잠재적 DOM XSS 취약점 발견:\n")
        
        for idx, vuln in enumerate(self.vulnerabilities, 1):
            print(f"{'=' * 80}")
            print(f"취약점 #{idx}")
            print(f"{'=' * 80}")
            print(f"타입: {vuln['type']}")
            print(f"심각도: {vuln['severity']}")
            print(f"위험한 Sink: {vuln['sink']}")
            print(f"사용자 입력 Source: {vuln['source']}")
            print(f"위치: {vuln['location']}")
            print(f"라인: {vuln['line']}")
            print(f"\n컨텍스트:")
            print(f"{vuln['context']}")
            print(f"\n테스트 페이로드:")
            print(f"{vuln['payload']}")
            print()
        
        # 요약
        print("\n" + "=" * 80)
        print("📋 요약")
        print("=" * 80)
        print(f"총 취약점: {len(self.vulnerabilities)}개")
        
        # Sink별 통계
        sink_count = {}
        for vuln in self.vulnerabilities:
            sink = vuln['sink']
            sink_count[sink] = sink_count.get(sink, 0) + 1
        
        print(f"\n위험한 Sink 함수별 통계:")
        for sink, count in sorted(sink_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {sink}: {count}개")
        
        # Source별 통계
        source_count = {}
        for vuln in self.vulnerabilities:
            source = vuln['source']
            source_count[source] = source_count.get(source, 0) + 1
        
        print(f"\n사용자 입력 Source별 통계:")
        for source, count in sorted(source_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {source}: {count}개")

    def test_xss(self, test_url=None):
        """XSS 페이로드 테스트 (동적 테스트)"""
        if not test_url:
            test_url = self.target_url
        
        print("\n" + "=" * 80)
        print("🧪 XSS 페이로드 테스트 (동적 테스트)")
        print("=" * 80)
        
        # URL 파라미터 추출
        parsed = urlparse(test_url)
        params = parse_qs(parsed.query)
        
        if not params:
            print("[*] URL 파라미터가 없습니다. 수동으로 테스트하세요.")
            print("\n테스트할 페이로드:")
            for payload in self.xss_payloads[:5]:
                print(f"  - {payload}")
            return
        
        print(f"[*] 발견된 파라미터: {list(params.keys())}")
        
        for param_name in params.keys():
            print(f"\n[*] 파라미터 '{param_name}' 테스트 중...")
            for payload in self.xss_payloads[:3]:  # 처음 3개만 테스트
                test_params = params.copy()
                test_params[param_name] = [payload]
                
                # URL 재구성
                test_url_parsed = list(parsed)
                test_url_parsed[4] = '&'.join([f"{k}={v[0]}" for k, v in test_params.items()])
                test_url_full = urlparse('')._replace(*test_url_parsed).geturl()
                
                try:
                    response = self.session.get(test_url_full, timeout=10)
                    if payload in response.text:
                        print(f"  ⚠️  페이로드가 응답에 포함됨: {payload}")
                        print(f"     → 수동으로 브라우저에서 테스트 필요")
                except Exception as e:
                    print(f"  [-] 테스트 실패: {e}")


def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python dom_xss_scanner.py <URL>")
        print("\n예시:")
        print("  python dom_xss_scanner.py https://example.com")
        print("  python dom_xss_scanner.py https://example.com/page?test=123")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # URL 검증
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    scanner = DOMXSSScanner(target_url)
    scanner.scan()
    
    # 동적 테스트 옵션
    print("\n" + "=" * 80)
    response = input("동적 XSS 테스트를 수행하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        scanner.test_xss()


if __name__ == "__main__":
    main()

