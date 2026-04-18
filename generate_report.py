import os
import subprocess
import csv
import urllib.request
import datetime
import re

# ==============================================================================
# 1. 설정 (Configuration)
# ==============================================================================
DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d") # 오늘 날짜
WORKSPACE = os.path.expanduser("~/POSCO_카톡")
HTML_PATH = os.path.join(WORKSPACE, f"{DATE_STR}.html")
CSV_URL = "https://docs.google.com/spreadsheets/d/1hTSEWptRpjBf9Q-EJU2tl6HRgtubuVSuwd6iGwEn9Rk/export?format=csv"
GMAIL_USER = "csband8@gmail.com"
RECEIVER = "csband@posco.com"
# GMAIL_APP_PASSWORD는 환경변수로 설정하거나 아래에 직접 입력하세요.
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "YOUR_APP_PASSWORD")

# ==============================================================================
# 2. 데이터 가져오기 (Google Sheets -> CSV)
# ==============================================================================
print(f"[*] Fetching data from Google Sheets... {DATE_STR}")
try:
    req = urllib.request.Request(CSV_URL)
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        reader = csv.reader(lines)
        rows = list(reader)
except Exception as e:
    print(f"[!] Error fetching CSV: {e}")
    exit(1)

# 최신 행에서 B열 데이터 추출 (비어있지 않은 최신 데이터)
raw_data = ""
for row in reversed(rows):
    if len(row) > 1 and row[1].strip():
        raw_data = row[1].strip()
        break

if not raw_data:
    print("[!] Column B에 데이터가 없습니다.")
    exit(1)

# "취약작업자" 단어 사용 금지
raw_data = raw_data.replace("취약작업자", "65세 이상")

# ==============================================================================
# 3. 데이터 파싱 및 통계 (간단한 정규식 기반)
# ==============================================================================
def find_number(pattern, text):
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0

total_men = find_number(r"총원\s*(\d+)", raw_data) or find_number(r"계\s*(\d+)", raw_data)
# 실제 파이프라인에서는 더 정밀한 파싱이 필요할 수 있습니다.
# 여기서는 예시 숫자를 사용하거나 데이터에서 추출합니다.
day_men = total_men
night_men = find_number(r"연장\s*(\d+)", raw_data)
midnight_men = find_number(r"철야\s*(\d+)", raw_data)
senior_men = find_number(r"65세\s*(\d+)", raw_data)

# ==============================================================================
# 4. HTML 보고서 생성 (GEMINI.md 규칙 준수)
# ==============================================================================
html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 광양 2고로 일일공사보고서 - {DATE_STR}</title>
    <style>
        :root {{
            --primary: #0f4c81;
            --primary-light: #1a73b5;
            --bg: #f8f9fa;
            --white: #ffffff;
            --blue: #0f4c81;
            --green: #28a745;
            --purple: #6f42c1;
            --orange: #fd7e14;
            --red: #dc3545;
        }}
        body {{
            font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
            background-color: var(--bg);
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--white);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(to right, var(--primary), var(--primary-light));
            color: var(--white);
            text-align: center;
            padding: 30px 20px;
        }}
        header h1 {{ margin: 0; font-size: 24px; }}
        header .date {{ margin-top: 10px; font-size: 16px; opacity: 0.9; }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            padding: 20px;
            background: #fff;
        }}
        .card {{
            text-align: center;
            padding: 15px 5px;
            border-radius: 8px;
            background: #fff;
            border: 1px solid #eee;
            position: relative;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 5px;
            border-radius: 8px 8px 0 0;
        }}
        .card-1::before {{ background: var(--blue); }}
        .card-2::before {{ background: var(--green); }}
        .card-3::before {{ background: var(--purple); }}
        .card-4::before {{ background: var(--orange); }}
        .card-5::before {{ background: var(--red); }}
        
        .card-label {{ font-size: 12px; color: #666; display: block; margin-bottom: 5px; }}
        .card-value {{ font-size: 20px; font-weight: bold; }}
        .card-unit {{ font-size: 14px; font-weight: normal; margin-left: 2px; }}

        section {{ padding: 20px; border-bottom: 1px solid #eee; }}
        h2 {{ font-size: 18px; color: var(--primary); border-left: 4px solid var(--primary); padding-left: 10px; margin-bottom: 15px; }}
        
        .data-block {{
            background: #f1f3f5;
            padding: 15px;
            border-radius: 5px;
            font-size: 14px;
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        
        footer {{
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #888;
            background: #f8f9fa;
        }}

        @media screen and (max-width: 700px) {{
            .dashboard {{ grid-template-columns: repeat(3, 1fr); }}
            .card-4, .card-5 {{ grid-column: span 1.5; }}
        }}
        @media print {{
            body {{ padding: 0; background: #fff; }}
            .container {{ box-shadow: none; border: 1px solid #ccc; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>📋 광양 2고로 2차개수 일일공사보고서</h1>
        <div class="date">{DATE_STR}</div>
    </header>

    <div class="dashboard">
        <div class="card card-1">
            <span class="card-label">총원</span>
            <span class="card-value">{total_men}<span class="card-unit">명</span></span>
        </div>
        <div class="card card-2">
            <span class="card-label">주간</span>
            <span class="card-value">{day_men}<span class="card-unit">명</span></span>
        </div>
        <div class="card card-3">
            <span class="card-label">야간</span>
            <span class="card-value">{night_men}<span class="card-unit">명</span></span>
        </div>
        <div class="card card-4">
            <span class="card-label">철야</span>
            <span class="card-value">{midnight_men}<span class="card-unit">명</span></span>
        </div>
        <div class="card card-5">
            <span class="card-label">65세 이상</span>
            <span class="card-value">{senior_men}<span class="card-unit">명</span></span>
        </div>
    </div>

    <section>
        <h2>👷 주요 공정 및 인원 상세</h2>
        <div class="data-block">{raw_data}</div>
    </section>

    <footer>
        본 보고서는 시스템에 의해 자동 생성되었습니다. (출력일시: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    </footer>
</div>
</body>
</html>
"""

print(f"[*] Generating HTML report... {HTML_PATH}")
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)

# ==============================================================================
# 5. Git 작업
# ==============================================================================
print("[*] Running git operations...")
try:
    subprocess.run(["git", "add", HTML_PATH], check=True, cwd=WORKSPACE)
    subprocess.run(["git", "commit", "-m", f"Daily Report {DATE_STR}"], check=True, cwd=WORKSPACE)
    subprocess.run(["git", "push"], check=True, cwd=WORKSPACE)
except Exception as e:
    print(f"[!] Git failed: {e}")

# ==============================================================================
# 6. 이메일 발송 (curl 기반)
# ==============================================================================
print(f"[*] Sending email to {RECEIVER}...")
try:
    # Git 사용자 이름 가져오기 (GitHub Pages 링크 생성용)
    res = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, cwd=WORKSPACE)
    git_user = res.stdout.strip() or "clean"
    
    link = f"https://{git_user}.github.io/posco-daily-report/{DATE_STR}.html"
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
    subprocess.run(curl_cmd, check=True)
    os.remove("mail.txt")
    print("[+] Email sent successfully.")
except Exception as e:
    print(f"[!] Email failed: {e}")

print("[*] Done.")
