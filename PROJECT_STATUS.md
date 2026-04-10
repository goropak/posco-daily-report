# POSCO 광양 2고로 일일공사보고서 자동화 프로젝트 (https://www.genspark.ai/agents?id=7a4fa6fd-146b-4d44-ace9-f12f572c6c0f)

## 목표
카카오톡 공사 데이터 → AI 인포그래픽 HTML 보고서 자동 생성 → GitHub Pages 공개 → 이메일 발송

## 환경
- Mac: MacBook Pro (사용자: clean)
- AI: Gemini CLI v0.37.0 (Gemini Pro 구독 중)
- GitHub: goropak / posco-daily-report
- GitHub Pages: https://goropak.github.io/posco-daily-report/
- Gmail: csband8@gmail.com
- 수신자: csband@posco.com
- Google Sheets: https://docs.google.com/spreadsheets/d/1hTSEWptRpjBf9Q-EJU2tl6HRgtubuVSuwd6iGwEn9Rk
- 보고서 폴더: ~/POSCO_카톡/
- 보고서 규칙: ~/POSCO_카톡/GEMINI.md
- 자동 실행 스크립트: ~/POSCO_카톡/daily_report.sh
- CronJob: launchd com.posco.dailyreport (매일 09:30)

## 카톡 단톡방 (2개)
- 이앤씨: 2고로(안전방)
- 플랜텍: G2R2_원료&PCI(종합)

## 도급사 구조
- 포스코이앤씨 (도급) → 남경건설, 동일산업, 삼진공작, 대아이앤씨, 대웅기전 (하도)
- 플랜텍 (도급) → 금양이앤씨 (하도)
- 향후 포스코DX 등 추가 예정

## 완료된 작업
✅ Homebrew 5.1.5 설치
✅ Node.js 설치
✅ Gemini CLI 0.37.0 설치 + Google 계정 인증
✅ ~/POSCO_카톡/ 폴더 생성
✅ GEMINI.md 보고서 규칙 파일 작성
✅ HTML 인포그래픽 보고서 생성 테스트 성공
✅ Google Sheets MCP 연결 + 데이터 읽기 성공
✅ GitHub 레포 생성 + push 성공 (토큰 인증)
✅ GitHub Pages 활성화 + 웹 공개 확인
✅ Gmail 발송 테스트 성공 (App Password 방식)
✅ 카톡 2개 방 텍스트 → 보고서 생성 → git push 성공
✅ daily_report.sh 스크립트 작성
✅ launchd 매일 09:30 자동 실행 등록
✅ 카카오톡 접근성 권한 추가

## 미완료 작업
⬜ daily_report.sh 실제 동작 테스트 (API 한도 초과로 미완)
⬜ Google Sheets 입력 방식 확정 (날짜별 시트탭 vs 단일시트)
⬜ 핸드폰 → Google Sheets 붙여넣기 워크플로우 확정
⬜ 전체 파이프라인 end-to-end 테스트

## 보고서 디자인 규칙 요약
- 상단 대시보드 5개: 총원, 주간, 야간, 철야, 65세이상
- 도급사별 독립 블록 (이앤씨/플랜텍/향후 추가)
- 컬럼: 업체명|구분|인원수|투입장비|비고
- 비고에 연장작업자, 65세↑ 표기
- "취약작업자" 용어 사용 금지
- 블록별 소계 행 (진한 파란 배경, 흰색 글씨)

## 일일 워크플로우 (확정)
1. 핸드폰에서 카톡 복사 → Google Sheets 붙여넣기 (09시 이전)
2. 09:30 자동실행: Gemini CLI가 시트 읽기 → HTML 보고서 생성
3. GitHub Pages 자동 업로드
4. csband@posco.com 메일 자동 발송

## 알려진 이슈
- Gemini API 429 (Too Many Requests) → 하루 한도 초과 시 발생
- git push 시 토큰 인증 필요 (remote URL에 토큰 포함됨)
- Google Chat MCP는 설정 복잡 → Google Sheets 방식으로 결정
- 카톡 완전자동화는 긴 메시지 잘림 문제로 불가 → 수동 붙여넣기
