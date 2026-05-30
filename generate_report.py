import os
import subprocess
import csv
import urllib.request
import datetime
import re
import ssl

# SSL 검증 건너뛰기 설정 (Mac 등 특정 환경 대응)
ssl_context = ssl._create_unverified_context()

# ==============================================================================
# 1. 설정 (Configuration)
# ==============================================================================
DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d") # 오늘 날짜
WORKSPACE = os.path.expanduser("~/POSCO_카톡")
HTML_PATH = os.path.join(WORKSPACE, f"{DATE_STR}.html")
CSV_URL = "https://docs.google.com/spreadsheets/d/1hTSEWptRpjBf9Q-EJU2tl6HRgtubuVSuwd6iGwEn9Rk/export?format=csv"
GMAIL_USER = "csband8@gmail.com"
RECEIVER = "csband@posco.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "YOUR_APP_PASSWORD")

# ==============================================================================
# 2. 데이터 가져오기 (Google Sheets -> CSV)
# ==============================================================================
print(f"[*] Fetching data from Google Sheets... {DATE_STR}")
raw_data = ""
fetch_success = False

try:
    req = urllib.request.Request(CSV_URL)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        reader = csv.reader(lines)
        rows = list(reader)
        
        # 최신 행에서 B열 데이터 추출 (비어있지 않은 최신 데이터)
        for row in reversed(rows):
            if len(row) > 1 and row[1].strip() and row[1].strip() != "내용":
                raw_data = row[1].strip()
                fetch_success = True
                break
except Exception as e:
    print(f"[!] Error fetching CSV: {e}")

if not fetch_success:
    print("[!] 데이터 fetching 실패. 로컬 백업 또는 샘플 데이터를 사용합니다.")
    # 로컬 백업 탐색 (예: temp_data.csv 또는 최근 HTML에서 추출 - 여기선 샘플 데이터로 대체)
    raw_data = """
■ 포스코이앤씨 : 15명
■ 하도사 : 10명[관3, 작7]
○ 작업시간 : 08:00~17:00
○ 주요 공종 : 철피 지조립
- 작업내용 : 블록 #3 용접 및 검사
- 투입장비 : 200톤 크레인 1대
■ 연장 : 5명 (17:00~20:00) - 용접 잔여 작업
■ 65세 이상 : 2명 (이앤씨 1, 하도사 1)

■ 포스코플랜텍 : 12명
■ 하도사 : 8명[관2, 작6]
○ 작업시간 : 08:00~17:00
○ 주요 공종 : PCI 설비 이설
- 작업내용 : 배관 철거 및 신설
- 투입장비 : 카고크레인 1대
■ 65세 이상 : 1명
    """

# "취약작업자" 단어 사용 금지 (규칙 반영)
raw_data = raw_data.replace("취약작업자", "65세 이상")

# ==============================================================================
# 3. 데이터 파싱 및 통계
# ==============================================================================
def find_number(pattern, text):
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0

total_men = 0
day_men = 0
night_men = 0
midnight_men = 0
senior_men = 0

# 도급사별 파싱 (정규식 확장 필요)
contractors = []
blocks = re.split(r'■\s*포스코([\w]+)', raw_data)
if len(blocks) > 1:
    for i in range(1, len(blocks), 2):
        name = "포스코" + blocks[i]
        content = blocks[i+1]
        
        c_total = find_number(r'[:\s]*(\d+)명', content)
        c_sub = find_number(r'하도사\s*[:\s]*(\d+)명', content)
        c_night = find_number(r'연장\s*[:\s]*(\d+)명', content)
        c_senior = find_number(r'65세\s*이상\s*[:\s]*(\d+)명', content)
        
        contractors.append({
            "name": name,
            "total": c_total + c_night,
            "day": c_total,
            "night": c_night,
            "senior": c_senior,
            "content": content.strip()
        })
        
        total_men += (c_total + c_night)
        day_men += c_total
        night_men += c_night
        senior_men += c_senior

# ==============================================================================
# 4. HTML 템플릿 생성 (GEMINI.md 규칙 준수)
# ==============================================================================
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 광양 2고로 2차개수 일일공사보고서_{DATE_STR}</title>
    <style>
        body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f4f7f9; }}
        .header {{ background: linear-gradient(to right, #0f4c81, #1a73b5); color: white; text-align: center; padding: 30px 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 10px 0 0; font-size: 16px; opacity: 0.9; }}
        
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; padding: 20px; max-width: 1000px; margin: -30px auto 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 15px; text-align: center; border-top: 5px solid #ccc; }}
        .card.blue {{ border-top-color: #0f4c81; }}
        .card.green {{ border-top-color: #28a745; }}
        .card.purple {{ border-top-color: #6f42c1; }}
        .card.orange {{ border-top-color: #fd7e14; }}
        .card.red {{ border-top-color: #dc3545; }}
        .card-title {{ font-size: 14px; color: #666; margin-bottom: 5px; }}
        .card-value {{ font-size: 22px; font-weight: bold; color: #333; }}
        
        .section {{ background: white; margin: 20px auto; max-width: 1000px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .section h2 {{ border-left: 5px solid #0f4c81; padding-left: 10px; font-size: 18px; margin-bottom: 15px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
        th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: center; font-size: 14px; }}
        th {{ background-color: #f8f9fa; color: #495057; }}
        .total-row {{ background-color: #0f4c81; color: white; font-weight: bold; }}
        
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; background: #0f4c81; }}
        
        footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
        
        @media screen and (max-width: 700px) {{
            .dashboard {{ grid-template-columns: 1fr 1fr; }}
            .section {{ margin: 10px; padding: 15px; }}
        }}
        @media print {{
            .header {{ background: #0f4c81 !important; color: white !important; -webkit-print-color-adjust: exact; }}
            .card {{ border: 1px solid #ccc !important; box-shadow: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 광양 2고로 2차개수 일일공사보고서</h1>
        <p>{DATE_STR} {"(데이터 미수신 - 복구 모드)" if not fetch_success else ""}</p>
    </div>

    <div class="dashboard">
        <div class="card blue"><div class="card-title">총원</div><div class="card-value">{total_men}명</div></div>
        <div class="card green"><div class="card-title">주간 작업자</div><div class="card-value">{day_men}명</div></div>
        <div class="card purple"><div class="card-title">야간 작업자</div><div class="card-value">{night_men}명</div></div>
        <div class="card orange"><div class="card-title">철야 작업자</div><div class="card-value">{midnight_men}명</div></div>
        <div class="card red"><div class="card-title">65세 이상</div><div class="card-value">{senior_men}명</div></div>
    </div>

    <div class="section">
        <h2>👷 인원 현황</h2>
"""

for c in contractors:
    html_content += f"""
        <div style="margin-bottom: 20px;">
            <span class="badge">{c['name']}</span>
            <table style="margin-top: 10px;">
                <thead>
                    <tr><th>업체명</th><th>구분</th><th>인원수</th><th>투입장비</th><th>비고</th></tr>
                </thead>
                <tbody>
                    <tr><td>{c['name']}</td><td>도급</td><td>{c['day']}</td><td>-</td><td>{f"65세↑ {c['senior']}명" if c['senior'] > 0 else ""}</td></tr>
                    <tr class="total-row"><td colspan="2">소계</td><td>{c['total']}명</td><td>-</td><td>{f"연장 {c['night']}명" if c['night'] > 0 else ""}</td></tr>
                </tbody>
            </table>
        </div>
    """

html_content += f"""
    </div>

    <div class="section">
        <h2>🔧 주요 공종별 진행현황</h2>
        <div style="white-space: pre-wrap; font-size: 14px;">{raw_data}</div>
    </div>

    <div class="section">
        <h2>⚠️ 안전 특이사항</h2>
        <ul>
            <li>65세 이상 고령 작업자 현황: 총 {senior_men}명 (작업 전 건강상태 확인 필수)</li>
            <li>야간/연장 작업 시 조명 및 안전통로 확보 철저</li>
            {"<li><b>주의: Google Sheets 데이터 연결 실패로 샘플 데이터가 표시되고 있습니다.</b></li>" if not fetch_success else ""}
        </ul>
    </div>

    <footer>
        본 보고서는 시스템에 의해 자동 생성되었습니다. (출력일시: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    </footer>
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[+] Report generated: {HTML_PATH}")

# ==============================================================================
# 5. Git 작업
# ==============================================================================
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-report: {DATE_STR}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("[+] Git push success.")
except Exception as e:
    print(f"[!] Git failed: {e}")

# ==============================================================================
# 6. 이메일 발송 (Gmail SMTP via curl)
# ==============================================================================
if GMAIL_APP_PASSWORD != "YOUR_APP_PASSWORD":
    print("[*] Sending email...")
    link = f"https://goropak.github.io/posco-daily-report/{DATE_STR}.html"
    subject = f"[일일공사보고] 광양 2고로 2차개수 {DATE_STR}"
    body = f"광양 2고로 2차개수 일일공사보고서가 생성되었습니다.\\n\\n링크: {link}"
    
    email_content = f"From: {GMAIL_USER}\\nTo: {RECEIVER}\\nSubject: {subject}\\n\\n{body}"
    with open("mail.txt", "w", encoding="utf-8") as f:
        f.write(email_content)
        
    curl_cmd = [
        "curl", "--url", "smtps://smtp.gmail.com:465", "--ssl-reqd",
        "--mail-from", GMAIL_USER, "--mail-rcpt", RECEIVER,
        "--user", f"{GMAIL_USER}:{GMAIL_APP_PASSWORD}",
        "-T", "mail.txt"
    ]
    try:
        subprocess.run(curl_cmd, check=True)
        print("[+] Email sent successfully.")
    except Exception as e:
        print(f"[!] Email failed: {e}")
    finally:
        if os.path.exists("mail.txt"): os.remove("mail.txt")
else:
    print("[!] GMAIL_APP_PASSWORD가 설정되지 않아 이메일을 발송하지 않습니다.")

print("[*] Done.")
