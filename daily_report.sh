#!/bin/bash
export PATH="/usr/local/bin:$PATH"
cd ~/POSCO_카톡
echo "Google Sheets https://docs.google.com/spreadsheets/d/1hTSEWptRpjBf9Q-EJU2tl6HRgtubuVSuwd6iGwEn9Rk 에서 가장 최신 날짜 행의 B열 데이터를 읽고, ~/POSCO_카톡/GEMINI.md 규칙에 따라 HTML 보고서를 생성해서 ~/POSCO_카톡/ 폴더에 날짜.html로 저장해줘. 그리고 git add, commit, push하고, csband8@gmail.com에서 csband@posco.com으로 보고서 GitHub Pages 링크를 메일로 보내줘. 제목: [일일공사보고] 광양 2고로 2차개수 오늘날짜" | gemini
