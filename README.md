# Analysis Solution

AI 기출분석 & 보고서 생성 데스크톱 앱

## 주요 기능

- **AI 엔진 선택** - Claude / Gemini 토글 전환, 모델 선택
- **파일 업로드** - 드래그 앤 드롭 또는 버튼 클릭 (PDF, Word, TXT, HTML)
- **작업지시서 선택** - 분석 기준 프롬프트 파일 선택 가능
- **출력 형식** - HTML / PDF / Word 선택
- **다중 파일 분석** - 여러 파일 순차 자동 처리
- **다크 모던 UI** - PyQt5 기반

## 실행

```bash
pip install PyQt5
python main.py
```

## 전체 의존성 (API 사용 시)

```bash
pip install PyQt5 anthropic google-generativeai PyMuPDF python-docx htmldocx weasyprint
```

## 프로젝트 구조

```
├── main.py                # 엔트리포인트
├── app/
│   ├── core/
│   │   ├── config.py      # 설정 관리
│   │   ├── analyzer.py    # AI 엔진 (Claude/Gemini)
│   │   └── exporter.py    # 내보내기 (HTML/PDF/Word)
│   └── ui/
│       ├── styles.py      # 다크 테마
│       ├── main_window.py # 메인 윈도우
│       └── settings_dialog.py # 설정
└── PROJECT_SPEC.md        # 상세 설계 문서
```
