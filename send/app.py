from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import logging
from typing import List, Optional

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 활성화 (필요시 특정 도메인만 허용하도록 설정 가능)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SMTP 설정 (환경 변수에서 가져오기)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)


def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    body_html: Optional[str] = None,
    attachments: Optional[List[str]] = None
) -> dict:
    """
    여러 수신자에게 이메일을 전송하는 함수
    
    Args:
        recipients: 수신자 이메일 주소 리스트
        subject: 이메일 제목
        body: 이메일 본문 (텍스트)
        body_html: 이메일 본문 (HTML, 선택사항)
        attachments: 첨부 파일 경로 리스트 (선택사항)
    
    Returns:
        dict: 전송 결과
    """
    try:
        # 이메일 메시지 생성
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = ', '.join(recipients)  # 여러 수신자
        msg['Subject'] = subject
        
        # 텍스트 본문 추가
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # HTML 본문 추가 (있는 경우)
        if body_html:
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
        
        # 첨부 파일 추가
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
        
        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS 암호화
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"이메일 전송 성공: {len(recipients)}명에게 전송")
        return {
            'success': True,
            'message': f'{len(recipients)}명에게 이메일이 성공적으로 전송되었습니다.',
            'recipients': recipients
        }
    
    except smtplib.SMTPAuthenticationError:
        error_msg = 'SMTP 인증 실패. 사용자명과 비밀번호를 확인하세요.'
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    
    except smtplib.SMTPRecipientsRefused:
        error_msg = '수신자 이메일 주소가 거부되었습니다.'
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    
    except Exception as e:
        error_msg = f'이메일 전송 중 오류 발생: {str(e)}'
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'smtp_server': SMTP_SERVER,
        'smtp_port': SMTP_PORT,
        'from_email': FROM_EMAIL
    })


@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    """
    이메일 전송 API 엔드포인트
    
    요청 형식:
    {
        "recipients": ["email1@example.com", "email2@example.com"],
        "subject": "이메일 제목",
        "body": "이메일 본문",
        "body_html": "<h1>HTML 본문</h1>",  // 선택사항
        "attachments": ["/path/to/file1.pdf", "/path/to/file2.jpg"]  // 선택사항
    }
    """
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'}), 400
        
        recipients = data.get('recipients', [])
        subject = data.get('subject', '')
        body = data.get('body', '')
        body_html = data.get('body_html', None)
        attachments = data.get('attachments', None)
        
        # 유효성 검사
        if not recipients:
            return jsonify({'success': False, 'error': '수신자 이메일 주소가 필요합니다.'}), 400
        
        if not isinstance(recipients, list):
            return jsonify({'success': False, 'error': '수신자는 리스트 형식이어야 합니다.'}), 400
        
        if not subject:
            return jsonify({'success': False, 'error': '이메일 제목이 필요합니다.'}), 400
        
        if not body and not body_html:
            return jsonify({'success': False, 'error': '이메일 본문이 필요합니다.'}), 400
        
        # 이메일 전송
        result = send_email(
            recipients=recipients,
            subject=subject,
            body=body,
            body_html=body_html,
            attachments=attachments
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'서버 오류: {str(e)}'
        }), 500


@app.route('/send-bulk', methods=['POST'])
def send_bulk_email():
    """
    대량 이메일 전송 API (개별 이메일로 전송)
    
    요청 형식:
    {
        "recipients": ["email1@example.com", "email2@example.com"],
        "subject": "이메일 제목",
        "body": "이메일 본문",
        "body_html": "<h1>HTML 본문</h1>",  // 선택사항
        "attachments": ["/path/to/file1.pdf"]  // 선택사항
    }
    
    각 수신자에게 개별적으로 이메일을 전송합니다.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '요청 데이터가 없습니다.'}), 400
        
        recipients = data.get('recipients', [])
        subject = data.get('subject', '')
        body = data.get('body', '')
        body_html = data.get('body_html', None)
        attachments = data.get('attachments', None)
        
        if not recipients or not isinstance(recipients, list):
            return jsonify({'success': False, 'error': '수신자 이메일 주소가 필요합니다.'}), 400
        
        if not subject:
            return jsonify({'success': False, 'error': '이메일 제목이 필요합니다.'}), 400
        
        if not body and not body_html:
            return jsonify({'success': False, 'error': '이메일 본문이 필요합니다.'}), 400
        
        # 각 수신자에게 개별 전송
        results = []
        success_count = 0
        fail_count = 0
        
        for recipient in recipients:
            result = send_email(
                recipients=[recipient],
                subject=subject,
                body=body,
                body_html=body_html,
                attachments=attachments
            )
            results.append({
                'recipient': recipient,
                'success': result['success'],
                'message': result.get('message', result.get('error', ''))
            })
            
            if result['success']:
                success_count += 1
            else:
                fail_count += 1
        
        return jsonify({
            'success': True,
            'total': len(recipients),
            'success_count': success_count,
            'fail_count': fail_count,
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"대량 전송 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'서버 오류: {str(e)}'
        }), 500


if __name__ == '__main__':
    # 환경 변수 확인
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP_USERNAME 또는 SMTP_PASSWORD가 설정되지 않았습니다.")
        logger.warning(".env 파일을 확인하거나 환경 변수를 설정하세요.")
    
    # 서버 실행
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"이메일 서버 시작: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

