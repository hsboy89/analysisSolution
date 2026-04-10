# Analysis Solution - AI 기출분석 & 보고서 생성 도우미

> **프로젝트 목적:** 기출문제, 기출보고서 등 자료를 업로드하면 AI API를 통해 분석하여 분석지/작업지시서 형식에 맞는 결과물(PDF, Word, HTML)을 자동 생성하는 Python 데스크톱 앱(exe)
> **최종 수정:** 2026.04.10

---

## 1. 프로젝트 개요

### 1-1. 핵심 워크플로우

```
사용자가 파일 업로드 (PDF, Word, HWP, TXT, HTML)
    ↓
AI 엔진 선택 (Claude 또는 Gemini, GUI에서 토글)
    ↓
작업지시서(분석지_작업지시서_v12.1.md)를 프롬프트로 자동 로드
    ↓
API 호출 → 분석 결과(HTML) 수신
    ↓
출력 형식 선택 (HTML / PDF / Word) → 파일 저장
```

### 1-2. 핵심 요구사항

| 항목 | 설명 |
|------|------|
| **AI 엔진 선택** | Claude(Anthropic) / Gemini(Google) 중 택1, GUI에서 토글 버튼으로 전환 |
| **모델 선택** | 엔진별 모델 드롭다운 (Claude: opus/sonnet/haiku, Gemini: pro/flash/lite) |
| **API Key 관리** | 엔진별 개별 저장, 설정 다이얼로그에서 입력/변경, 연결 테스트 버튼 |
| **파일 업로드** | 우측 패널에서 [+파일 추가] 버튼 또는 드래그 앤 드롭, 복수 파일 지원 |
| **중복 방지** | 같은 파일 경로는 중복 추가되지 않음 |
| **출력 형식** | HTML(기본), PDF, Word (.docx) — HWP는 라이브러리 미성숙으로 제외 |
| **작업지시서 선택** | 프로젝트 루트에서 `*작업지시서*.md` 자동 검색 + 외부 파일 추가 가능, 드롭다운 선택 |
| **다중 파일 분석** | 업로드된 모든 파일을 순차 분석, 오류 시 다음 파일 계속 진행 |
| **HTML 추출** | AI 응답에서 ` ```html ``` ` 코드블록/태그 자동 추출, 순수 HTML만 저장 |
| **디자인** | 다크 모던 테마 (딥 네이비 + 골드 엑센트), 기본 폰트 9pt 기준 통일 |
| **배포** | PyInstaller로 단일 exe 패키징 |

---

## 2. 기술 스택

| 구분 | 기술 | 비고 |
|------|------|------|
| **언어** | Python 3.11 | |
| **GUI** | PyQt5 (5.15.11) | 이미 설치됨 |
| **Claude API** | anthropic SDK | `pip install anthropic` |
| **Gemini API** | google-generativeai SDK | `pip install google-generativeai` |
| **PDF 읽기** | PyMuPDF (fitz) | `pip install PyMuPDF` |
| **Word 읽기** | python-docx | `pip install python-docx` |
| **PDF 내보내기** | weasyprint 또는 playwright | `pip install weasyprint` |
| **Word 내보내기** | python-docx + htmldocx | `pip install htmldocx` |
| **exe 패키징** | PyInstaller | `pip install pyinstaller` |

---

## 3. 프로젝트 구조

```
analysisSolution/
├── main.py                          # 엔트리포인트
├── PROJECT_SPEC.md                  # 이 문서
├── 분석지_작업지시서_v12.1.md         # AI 프롬프트 (작업지시서)
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                        # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── config.py                # 설정 관리 (API키, 엔진, 모델, 출력 경로)
│   │   ├── analyzer.py              # AI 분석 엔진 (BaseAnalyzer → Claude/Gemini)
│   │   └── exporter.py              # 내보내기 (HTML, PDF, Word)
│   │
│   └── ui/                          # GUI
│       ├── __init__.py
│       ├── styles.py                # 다크 모던 테마 QSS 스타일시트
│       ├── main_window.py           # 메인 윈도우
│       └── settings_dialog.py       # 설정 다이얼로그
│
├── 제철고2_26년_*.html              # 기존 분석지 HTML 샘플들
└── 포항제철고_2025_*.html           # 기존 보고서 HTML 샘플들
```

---

## 4. 모듈별 상세 설계

### 4-1. config.py — 설정 관리

- 설정 파일 위치: `~/.analysisSolution/config.json`
- 엔진별 API Key, 모델, 사용 가능 모델 목록 저장
- 출력 형식(html/pdf/word), 출력 폴더 저장
- `Config` 클래스: `load()`, `save()`, property 기반 접근

```json
{
  "engine": "claude",
  "claude": {
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-20250514",
    "models": ["claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"]
  },
  "gemini": {
    "api_key": "AIza...",
    "model": "gemini-2.0-flash",
    "models": ["gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
  },
  "output": {
    "format": "html",
    "output_dir": ""
  }
}
```

### 4-2. analyzer.py — AI 분석 엔진

```
BaseAnalyzer (ABC)
├── analyze(file_path, prompt, on_progress) → str (HTML)
├── validate_key() → bool
├── read_file(file_path) → str  (PDF/Word/TXT/HTML 자동 판별)
│
├── ClaudeAnalyzer
│   └── anthropic SDK 사용, messages.create() 호출
│
└── GeminiAnalyzer
    └── google.generativeai SDK 사용, generate_content() 호출
```

- `create_analyzer(engine, api_key, model)` 팩토리 함수로 인스턴스 생성
- `on_progress` 콜백으로 진행률(0~100) GUI에 전달
- 나중에 GPT 등 새 엔진 추가 시 `BaseAnalyzer` 상속만 하면 됨

### 4-3. exporter.py — 내보내기

| 함수 | 입력 | 출력 |
|------|------|------|
| `export_html()` | HTML 문자열 | `.html` 파일 저장 |
| `export_pdf()` | HTML 문자열 | weasyprint 또는 playwright로 `.pdf` 변환 |
| `export_word()` | HTML 문자열 | htmldocx로 `.docx` 변환 |
| `export()` | HTML + 형식명 | 통합 호출 함수 |

### 4-4. styles.py — 다크 모던 테마

- **컬러 팔레트:**
  - 배경: `#1a1b2e` (딥 다크 네이비)
  - 패널: `#1e2140` / `#2d3154`
  - 엑센트: `#fbbf24` (골드) / `#d97706` (앰버)
  - 텍스트: `#e0e0e0` (밝은 회색) / `#8892b0` (보조) / `#94a3b8` (라벨)
  - 성공: `#22c55e` / 오류: `#ef4444`
- **폰트 크기 기준 (통일):**
  - 기본: `9pt`
  - 타이틀: `13pt`
  - 서브타이틀: `8pt`
  - 분석 시작 버튼: `10pt`
  - 설정 기어: `11pt`
  - 상태바: `8pt`
  - 업로드 아이콘: `22pt`
  - 나머지 모든 요소: `9pt`

---

## 5. GUI 화면 구성

### 5-1. 메인 윈도우 레이아웃

- 기본 창 크기: `1100 x 700`
- 최소 크기: `1050 x 660`
- 좌측 패널 고정 폭: `320px`

```
┌──────────────────────────────────────────────────────────────────┐
│  [타이틀 바 — 딥 네이비 그라디언트, 골드 하단 보더]                    │
│  Analysis Solution (13pt, 골드)                         ⚙ 설정  │
│  AI 기출분석 & 보고서 생성 도우미 (8pt)                              │
├─────────────────┬────────────────────────────────────────────────┤
│  좌측 (320px)    │  우측 (나머지 전체)                               │
│                 │                                                │
│ ┌─────────────┐ │  분석 파일      [+파일 추가] [선택 제거] [전체 비우기] │
│ │ AI 엔진 선택  │ │ ┌──────────────────────────────────────────┐  │
│ │[Claude][Gemini]│ │ │ 포항제철고_2025_1학년_기말고사.html         │  │
│ │ 모델: ▼      │ │ │ 제철고2_26년_중간_분석지.html              │  │
│ │ ● API 상태   │ │ │ (드래그 앤 드롭으로도 추가 가능)             │  │
│ └─────────────┘ │ │                                          │  │
│ ┌─────────────┐ │ └──────────────────────────────────────────┘  │
│ │ 작업지시서    │ │                                                │
│ │[▼ v12.1.md ] │ │  결과 미리보기                                   │
│ │[+추가][새로고침]│ │ ┌──────────────────────────────────────────┐  │
│ └─────────────┘ │ │ │ 분석 결과가 여기에 표시됩니다...              │  │
│ ┌─────────────┐ │ │                                          │  │
│ │ 출력 형식     │ │ │                                          │  │
│ │◉HTML ○PDF   │ │ │                                          │  │
│ │○Word        │ │ │                                          │  │
│ └─────────────┘ │ │                                          │  │
│                 │ └──────────────────────────────────────────┘  │
│ [████ 분석 시작]  │                                                │
│ [진행바 (숨김)]   │                                                │
│                 │                                                │
├─────────────────┴────────────────────────────────────────────────┤
│  상태바: 준비 완료 / 파일 3개 등록됨 / 저장 완료: ...                  │
└──────────────────────────────────────────────────────────────────┘
```

**핵심 설계 결정:**
- 로그 패널 제거 → 상태바로 대체 (간결함 우선)
- 파일 리스트를 우측 넓은 영역에 배치 (파일명 잘림 방지)
- 파일 리스트는 `FileDropList` 커스텀 위젯 (QListWidget 상속, 드래그 앤 드롭 지원)
- 파일명만 표시, 전체 경로는 `data(Qt.UserRole)`에 저장 + 툴팁으로 확인
- 중복 파일 자동 방지 (경로 기준 비교)

### 5-2. 설정 다이얼로그

- 고정 크기: `520 x 420`

```
┌─────────────────────────────────────────┐
│  설정                              [X]  │
│                                         │
│ ┌─ Claude (Anthropic) ────────────────┐ │
│ │ API Key: [sk-ant-●●●●●●●     ]     │ │
│ │ 모델:    [claude-sonnet-4 ▼   ]     │ │
│ │          [연결 테스트]               │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Gemini (Google) ───────────────────┐ │
│ │ API Key: [AIza●●●●●●●●      ]      │ │
│ │ 모델:    [gemini-2.0-flash ▼ ]      │ │
│ │          [연결 테스트]               │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ 출력 설정 ─────────────────────────┐ │
│ │ 저장 폴더: [           ] [찾아보기] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│                    [취소]  [██ 저장 ██]  │
└─────────────────────────────────────────┘
```

### 5-3. 엔진 선택 동작

- **Claude / Gemini 토글 버튼**: QButtonGroup exclusive, 한쪽 선택 시 다른 쪽 해제
- 선택된 엔진 버튼: 골드 그라디언트 배경 + 진한 테두리
- 엔진 전환 시:
  - 모델 드롭다운이 해당 엔진의 모델 목록으로 자동 갱신
  - API 상태 표시가 해당 엔진 키 유무에 따라 갱신
  - 설정은 즉시 `config.json`에 저장

### 5-4. 팝업(QMessageBox) 스타일

- 다크 배경(`#1e2140`) + 흰색 글자(`#ffffff`)
- `max-width: 360px`로 가로 크기 제한 (글자가 너무 퍼지지 않게)

---

## 6. 분석 실행 흐름

```
[분석 시작] 클릭
    │
    ├─ 파일 리스트 비어있으면 → 경고 팝업
    ├─ API Key 없으면 → 경고 팝업 ("설정에서 입력하세요")
    ├─ 작업지시서 없으면 → 경고 팝업
    │
    ├─ 전체 파일 큐 생성 (file_list의 모든 파일)
    │
    ├─ 파일별 순차 처리 (AnalysisWorker QThread)
    │   ├─ 10%: 파일 읽기 (read_file — PDF/Word/TXT/HTML 자동 판별)
    │   ├─ 30%: API 호출 (선택된 작업지시서 + 파일내용)
    │   ├─ 90%: 응답 수신 → extract_html()로 순수 HTML 추출
    │   └─ 100%: 완료 → 선택 형식으로 저장 → 다음 파일로
    │
    ├─ 진행바: 전체 파일 기준 진행률 표시
    ├─ 오류 시: 경고 팝업 후 다음 파일 계속 진행
    │
    └─ 전체 완료 시
        ├─ 마지막 결과 미리보기에 HTML 표시
        └─ 상태바에 "전체 N개 파일 분석 완료!" 표시
```

---

## 7. 기존 산출물 참조

프로젝트에는 이미 완성된 HTML 분석지/보고서 샘플이 포함되어 있음:

| 파일 | 유형 |
|------|------|
| `제철고2_26년_1학기_중간_수능실감_독해_6회_분석지.html` | 분석지 (지문별 상세 분석) |
| `제철고2_26년_1학기_중간_불변의패턴1_5_통합_변형_A.html` | 변형 문제지 |
| `제철고2_26년_1학기_중간_불변의패턴1_5_통합_변형_A_정답해설.html` | 정답 해설지 |
| `포항제철고_2025_1학년_1학기_기말고사_기출분석_보고서.html` | 기출분석 보고서 |
| `포항제철고_2025_1학년_2학기_중간고사_기출분석_보고서.html` | 기출분석 보고서 |
| `포항제철고_2025_1학년_출제경향_비교분석_보고서.html` | 출제경향 비교분석 |

- 분석지는 `분석지_작업지시서_v12.1.md`의 디자인 시스템(CSS 변수, 카테고리 컬러코딩)에 따라 제작됨
- 보고서는 별도 디자인 (네이비 + 레드 엑센트 헤더, 차트, 테이블)
- **이 HTML 결과물과 동일한 품질**이 AI API를 통해 자동 생성되는 것이 최종 목표

---

## 8. 전체 소스 코드

### 8-1. main.py

```python
"""Analysis Solution - AI 기출분석 & 보고서 생성 도우미"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.ui.styles import DARK_STYLE


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    app.setApplicationName("Analysis Solution")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

### 8-2. app/core/config.py

```python
"""설정 관리 모듈 - API 키, 엔진 선택, 모델 설정 저장/로드"""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".analysisSolution"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "engine": "claude",  # "claude" or "gemini"
    "claude": {
        "api_key": "",
        "model": "claude-sonnet-4-20250514",
        "models": [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-haiku-4-5-20251001",
        ],
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-2.0-flash",
        "models": [
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ],
    },
    "output": {
        "format": "html",  # "html", "pdf", "word"
        "output_dir": "",
    },
    "template": "analysis",  # "analysis" or "report"
}


class Config:
    def __init__(self):
        self._data = {}
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self._data = {**DEFAULT_CONFIG, **saved}
        else:
            self._data = DEFAULT_CONFIG.copy()

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def engine(self):
        return self._data["engine"]

    @engine.setter
    def engine(self, value):
        self._data["engine"] = value

    def get_api_key(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["api_key"]

    def set_api_key(self, key, engine=None):
        engine = engine or self.engine
        self._data[engine]["api_key"] = key

    def get_model(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["model"]

    def set_model(self, model, engine=None):
        engine = engine or self.engine
        self._data[engine]["model"] = model

    def get_models(self, engine=None):
        engine = engine or self.engine
        return self._data[engine]["models"]

    @property
    def output_format(self):
        return self._data["output"]["format"]

    @output_format.setter
    def output_format(self, value):
        self._data["output"]["format"] = value

    @property
    def output_dir(self):
        return self._data["output"]["output_dir"]

    @output_dir.setter
    def output_dir(self, value):
        self._data["output"]["output_dir"] = value

    @property
    def template(self):
        return self._data["template"]

    @template.setter
    def template(self, value):
        self._data["template"] = value
```

### 8-3. app/core/analyzer.py

```python
"""AI 분석 엔진 - 공통 인터페이스 + Claude/Gemini 구현"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseAnalyzer(ABC):
    """AI 분석 엔진 공통 인터페이스"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def analyze(self, file_path: str, prompt: str, on_progress=None) -> str:
        """파일을 분석하고 HTML 결과를 반환한다.

        Args:
            file_path: 업로드된 파일 경로
            prompt: 작업지시서 프롬프트
            on_progress: 진행 상태 콜백 (0~100)

        Returns:
            생성된 HTML 문자열
        """
        pass

    @abstractmethod
    def validate_key(self) -> bool:
        """API 키 유효성 검증"""
        pass

    def read_file(self, file_path: str) -> str:
        """파일 내용을 읽어온다 (텍스트 기반)"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in (".txt", ".md", ".html", ".htm"):
            return path.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            return self._read_pdf(path)
        elif suffix in (".docx",):
            return self._read_docx(path)
        elif suffix in (".hwp", ".hwpx"):
            return self._read_hwp(path)
        else:
            return path.read_text(encoding="utf-8")

    def _read_pdf(self, path: Path) -> str:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            raise ImportError("PDF 읽기에 PyMuPDF가 필요합니다: pip install PyMuPDF")

    def _read_docx(self, path: Path) -> str:
        try:
            import docx
            doc = docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            raise ImportError("Word 읽기에 python-docx가 필요합니다: pip install python-docx")

    def _read_hwp(self, path: Path) -> str:
        raise NotImplementedError("HWP 파일 읽기는 아직 지원되지 않습니다.")


class ClaudeAnalyzer(BaseAnalyzer):
    """Claude API를 사용한 분석 엔진"""

    def analyze(self, file_path: str, prompt: str, on_progress=None) -> str:
        if on_progress:
            on_progress(10)

        file_content = self.read_file(file_path)

        if on_progress:
            on_progress(30)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model=self.model,
                max_tokens=16000,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n---\n\n아래는 분석할 자료입니다:\n\n{file_content}",
                    }
                ],
            )

            if on_progress:
                on_progress(90)

            result = message.content[0].text

            if on_progress:
                on_progress(100)

            return result

        except ImportError:
            raise ImportError("Claude 사용에 anthropic SDK가 필요합니다: pip install anthropic")

    def validate_key(self) -> bool:
        if not self.api_key:
            return False
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except Exception:
            return False


class GeminiAnalyzer(BaseAnalyzer):
    """Google Gemini API를 사용한 분석 엔진"""

    def analyze(self, file_path: str, prompt: str, on_progress=None) -> str:
        if on_progress:
            on_progress(10)

        file_content = self.read_file(file_path)

        if on_progress:
            on_progress(30)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            response = model.generate_content(
                f"{prompt}\n\n---\n\n아래는 분석할 자료입니다:\n\n{file_content}"
            )

            if on_progress:
                on_progress(90)

            result = response.text

            if on_progress:
                on_progress(100)

            return result

        except ImportError:
            raise ImportError(
                "Gemini 사용에 google-generativeai SDK가 필요합니다: pip install google-generativeai"
            )

    def validate_key(self) -> bool:
        if not self.api_key:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-lite")
            model.generate_content("hi")
            return True
        except Exception:
            return False


def create_analyzer(engine: str, api_key: str, model: str) -> BaseAnalyzer:
    """팩토리 함수 - 엔진 이름으로 분석기 인스턴스 생성"""
    engines = {
        "claude": ClaudeAnalyzer,
        "gemini": GeminiAnalyzer,
    }
    if engine not in engines:
        raise ValueError(f"지원하지 않는 엔진: {engine}. 사용 가능: {list(engines.keys())}")
    return engines[engine](api_key=api_key, model=model)
```

### 8-4. app/core/exporter.py

```python
"""내보내기 모듈 - HTML, PDF, Word 출력"""
from pathlib import Path


def export_html(html_content: str, output_path: str) -> str:
    """HTML 파일로 저장"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_content, encoding="utf-8")
    return str(path)


def export_pdf(html_content: str, output_path: str) -> str:
    """HTML을 PDF로 변환하여 저장"""
    path = Path(output_path).with_suffix(".pdf")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(str(path))
        return str(path)
    except ImportError:
        pass

    # fallback: playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            page.pdf(path=str(path), format="A4", print_background=True)
            browser.close()
        return str(path)
    except ImportError:
        raise ImportError(
            "PDF 변환에 weasyprint 또는 playwright가 필요합니다.\n"
            "pip install weasyprint 또는 pip install playwright && playwright install chromium"
        )


def export_word(html_content: str, output_path: str) -> str:
    """HTML을 Word(.docx) 파일로 변환하여 저장"""
    path = Path(output_path).with_suffix(".docx")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from htmldocx import HtmlToDocx
        from docx import Document

        doc = Document()
        parser = HtmlToDocx()
        parser.add_html_to_document(html_content, doc)
        doc.save(str(path))
        return str(path)
    except ImportError:
        raise ImportError(
            "Word 변환에 python-docx, htmldocx가 필요합니다.\n"
            "pip install python-docx htmldocx"
        )


EXPORTERS = {
    "html": export_html,
    "pdf": export_pdf,
    "word": export_word,
}


def export(html_content: str, output_path: str, fmt: str) -> str:
    """통합 내보내기 함수"""
    if fmt not in EXPORTERS:
        raise ValueError(f"지원하지 않는 형식: {fmt}. 사용 가능: {list(EXPORTERS.keys())}")
    return EXPORTERS[fmt](html_content, output_path)
```

### 8-5. app/ui/styles.py

```python
"""다크 모던 테마 스타일시트"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1a1b2e;
    color: #e0e0e0;
}

QWidget {
    font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
    font-size: 9pt;
}

/* ── 상단 타이틀 바 ── */
#titleBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0f172a, stop:1 #1e3a5c);
    padding: 12px 20px;
    border-bottom: 2px solid #fbbf24;
}
#titleLabel {
    color: #fbbf24;
    font-size: 13pt;
    font-weight: bold;
}
#subtitleLabel {
    color: #94a3b8;
    font-size: 8pt;
}

/* ── 엔진 선택 영역 ── */
#enginePanel {
    background: #1e2140;
    border: 1px solid #2d3154;
    border-radius: 10px;
    padding: 12px;
    margin: 4px 0;
}
#enginePanel QLabel {
    color: #94a3b8;
    font-size: 9pt;
    font-weight: bold;
}

/* 엔진 토글 버튼 */
QPushButton#btnClaude, QPushButton#btnGemini {
    background: #2d3154;
    color: #8892b0;
    border: 2px solid #3d4470;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 9pt;
    font-weight: bold;
    min-width: 100px;
}
QPushButton#btnClaude:checked, QPushButton#btnGemini:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #d97706, stop:1 #f59e0b);
    color: #0f172a;
    border: 2px solid #fbbf24;
}
QPushButton#btnClaude:hover, QPushButton#btnGemini:hover {
    background: #3d4470;
    border-color: #fbbf24;
}

/* ── 모델 드롭다운 ── */
QComboBox {
    background: #2d3154;
    color: #e0e0e0;
    border: 1px solid #3d4470;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 32px;
}
QComboBox:hover {
    border-color: #fbbf24;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94a3b8;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background: #2d3154;
    color: #e0e0e0;
    border: 1px solid #3d4470;
    selection-background-color: #d97706;
    selection-color: #0f172a;
}

/* ── 파일 업로드 영역 ── */
#uploadArea {
    background: #1e2140;
    border: 2px dashed #3d4470;
    border-radius: 10px;
    padding: 16px;
    margin: 6px 0;
}
#uploadArea:hover {
    border-color: #fbbf24;
    background: #232650;
}
#uploadIcon {
    color: #fbbf24;
    font-size: 22pt;
}
#uploadText {
    color: #8892b0;
    font-size: 9pt;
}
#uploadSubText {
    color: #5a6180;
    font-size: 7.5pt;
}

/* ── 파일 리스트 ── */
QListWidget {
    background: #1e2140;
    border: 2px dashed #3d4470;
    border-radius: 10px;
    padding: 8px;
    font-size: 9pt;
    outline: none;
}
QListWidget::item {
    padding: 10px 12px;
    margin: 3px 0;
    border-radius: 6px;
    background: #252850;
    color: #ffffff;
    min-height: 30px;
}
QListWidget::item:selected {
    background: #3a3f6e;
    color: #fbbf24;
    border: 1px solid #fbbf24;
}
QListWidget::item:hover:!selected {
    background: #2e3360;
    color: #ffffff;
}

/* ── 출력 형식 라디오 ── */
QRadioButton {
    color: #8892b0;
    spacing: 6px;
    font-size: 9pt;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #3d4470;
    background: #2d3154;
}
QRadioButton::indicator:checked {
    background: #fbbf24;
    border-color: #fbbf24;
}
QRadioButton:hover {
    color: #e0e0e0;
}

/* ── 메인 액션 버튼 ── */
QPushButton#btnAnalyze {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #d97706, stop:1 #f59e0b);
    color: #0f172a;
    border: none;
    border-radius: 8px;
    padding: 10px 30px;
    font-size: 10pt;
    font-weight: bold;
    min-height: 40px;
}
QPushButton#btnAnalyze:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f59e0b, stop:1 #fbbf24);
}
QPushButton#btnAnalyze:pressed {
    background: #b45309;
}
QPushButton#btnAnalyze:disabled {
    background: #3d4470;
    color: #5a6180;
}

/* ── 일반 버튼 ── */
QPushButton {
    background: #2d3154;
    color: #e0e0e0;
    border: 1px solid #3d4470;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 9pt;
}
QPushButton:hover {
    background: #3d4470;
    border-color: #fbbf24;
}
QPushButton:pressed {
    background: #1e2140;
}

/* ── 설정 버튼 ── */
QPushButton#btnSettings {
    background: transparent;
    border: 1px solid #3d4470;
    border-radius: 6px;
    color: #94a3b8;
    padding: 6px 12px;
    font-size: 11pt;
}
QPushButton#btnSettings:hover {
    border-color: #fbbf24;
    color: #fbbf24;
}

/* ── 진행 바 ── */
QProgressBar {
    background: #2d3154;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #d97706, stop:1 #fbbf24);
    border-radius: 6px;
}

/* ── 상태 바 ── */
QStatusBar {
    background: #0f172a;
    color: #5a6180;
    font-size: 8pt;
    border-top: 1px solid #2d3154;
}

/* ── 텍스트 입력 ── */
QLineEdit {
    background: #2d3154;
    color: #e0e0e0;
    border: 1px solid #3d4470;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 32px;
}
QLineEdit:focus {
    border-color: #fbbf24;
}
QLineEdit[echoMode="2"] {
    lineedit-password-character: 9679;
}

/* ── 텍스트 에디터 ── */
QTextEdit {
    background: #12132a;
    color: #8892b0;
    border: 1px solid #2d3154;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'D2Coding', monospace;
    font-size: 9pt;
}

/* ── 그룹 박스 ── */
QGroupBox {
    background: #1e2140;
    border: 1px solid #2d3154;
    border-radius: 10px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 28px;
    font-weight: bold;
    color: #94a3b8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #fbbf24;
    font-size: 9pt;
}

/* ── 스크롤바 ── */
QScrollBar:vertical {
    background: #1a1b2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3d4470;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #fbbf24;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── 탭 위젯 ── */
QTabWidget::pane {
    border: 1px solid #2d3154;
    border-radius: 8px;
    background: #1e2140;
}
QTabBar::tab {
    background: #2d3154;
    color: #8892b0;
    padding: 8px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #1e2140;
    color: #fbbf24;
    border-bottom: 2px solid #fbbf24;
}
QTabBar::tab:hover {
    background: #3d4470;
}

/* ── 체크박스 ── */
QCheckBox {
    color: #8892b0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #3d4470;
    background: #2d3154;
}
QCheckBox::indicator:checked {
    background: #fbbf24;
    border-color: #fbbf24;
}

/* ── 메시지 박스 ── */
QMessageBox {
    background-color: #1e2140;
    color: #ffffff;
    max-width: 360px;
}
QMessageBox QLabel {
    color: #ffffff;
    font-size: 9pt;
    padding: 4px;
}
QMessageBox QPushButton {
    min-width: 70px;
    padding: 6px 16px;
}

/* ── 툴팁 ── */
QToolTip {
    background: #2d3154;
    color: #e0e0e0;
    border: 1px solid #fbbf24;
    border-radius: 4px;
    padding: 4px 8px;
}
"""
```

### 8-6. app/ui/main_window.py

```python
"""메인 윈도우 - 파일 업로드, 엔진 선택, 분석 실행"""
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QProgressBar,
    QTextEdit, QRadioButton, QButtonGroup, QFileDialog,
    QStatusBar, QMessageBox, QComboBox, QGroupBox,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from app.core.config import Config
from app.core.analyzer import create_analyzer
from app.core.exporter import export
from app.ui.settings_dialog import SettingsDialog


class AnalysisWorker(QThread):
    """백그라운드 분석 스레드"""
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_result = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, analyzer, file_path, prompt):
        super().__init__()
        self.analyzer = analyzer
        self.file_path = file_path
        self.prompt = prompt

    def run(self):
        try:
            self.log.emit(f"분석 시작: {os.path.basename(self.file_path)}")
            result = self.analyzer.analyze(
                self.file_path,
                self.prompt,
                on_progress=lambda v: self.progress.emit(v),
            )
            self.log.emit("분석 완료!")
            self.finished_result.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.worker = None
        self.prompt_text = self._load_prompt()
        self.setup_ui()
        self.update_engine_ui()

    def _load_prompt(self) -> str:
        prompt_path = Path(__file__).parent.parent.parent / "분석지_작업지시서_v12.1.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    def setup_ui(self):
        self.setWindowTitle("Analysis Solution - AI 기출분석 도우미")
        self.setMinimumSize(1050, 660)
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 타이틀 바 ──
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 8, 20, 8)

        title_left = QVBoxLayout()
        title_label = QLabel("Analysis Solution")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("AI 기출분석 & 보고서 생성 도우미")
        subtitle_label.setObjectName("subtitleLabel")
        title_left.addWidget(title_label)
        title_left.addWidget(subtitle_label)

        btn_settings = QPushButton("\u2699")
        btn_settings.setObjectName("btnSettings")
        btn_settings.setToolTip("설정")
        btn_settings.clicked.connect(self.open_settings)

        title_layout.addLayout(title_left)
        title_layout.addStretch()
        title_layout.addWidget(btn_settings)

        main_layout.addWidget(title_bar)

        # ── 본문 영역 ──
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(16, 12, 16, 12)
        body_layout.setSpacing(16)

        # =============================================
        # 좌측: 엔진 선택 + 출력 형식 + 분석 버튼
        # =============================================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # 엔진 선택 패널
        engine_panel = QWidget()
        engine_panel.setObjectName("enginePanel")
        engine_layout = QVBoxLayout(engine_panel)
        engine_layout.setSpacing(8)

        engine_title = QLabel("AI 엔진 선택")
        engine_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #fbbf24;")

        btn_row = QHBoxLayout()
        self.btn_claude = QPushButton("Claude")
        self.btn_claude.setObjectName("btnClaude")
        self.btn_claude.setCheckable(True)
        self.btn_claude.clicked.connect(lambda: self.set_engine("claude"))

        self.btn_gemini = QPushButton("Gemini")
        self.btn_gemini.setObjectName("btnGemini")
        self.btn_gemini.setCheckable(True)
        self.btn_gemini.clicked.connect(lambda: self.set_engine("gemini"))

        self.engine_group = QButtonGroup()
        self.engine_group.addButton(self.btn_claude)
        self.engine_group.addButton(self.btn_gemini)
        self.engine_group.setExclusive(True)

        btn_row.addWidget(self.btn_claude)
        btn_row.addWidget(self.btn_gemini)

        # 모델 선택
        model_row = QHBoxLayout()
        model_label = QLabel("모델:")
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_combo, 1)

        # API 상태 표시
        self.api_status = QLabel("\u25cf API 미설정")
        self.api_status.setStyleSheet("color: #ef4444; font-size: 8pt;")

        engine_layout.addWidget(engine_title)
        engine_layout.addLayout(btn_row)
        engine_layout.addLayout(model_row)
        engine_layout.addWidget(self.api_status)

        left_panel.addWidget(engine_panel)

        # 출력 형식
        format_group = QGroupBox("출력 형식")
        format_layout = QHBoxLayout(format_group)
        self.radio_html = QRadioButton("HTML")
        self.radio_pdf = QRadioButton("PDF")
        self.radio_word = QRadioButton("Word")
        self.radio_html.setChecked(True)
        self.format_group = QButtonGroup()
        self.format_group.addButton(self.radio_html)
        self.format_group.addButton(self.radio_pdf)
        self.format_group.addButton(self.radio_word)
        format_layout.addWidget(self.radio_html)
        format_layout.addWidget(self.radio_pdf)
        format_layout.addWidget(self.radio_word)
        format_layout.addStretch()
        left_panel.addWidget(format_group)

        # 분석 시작 버튼
        self.btn_analyze = QPushButton("분석 시작")
        self.btn_analyze.setObjectName("btnAnalyze")
        self.btn_analyze.clicked.connect(self.start_analysis)
        left_panel.addWidget(self.btn_analyze)

        # 진행 바
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        left_panel.addWidget(self.progress)

        left_panel.addStretch()

        # =============================================
        # 우측: 파일 업로드 + 파일 리스트 + 결과 미리보기
        # =============================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        # 파일 업로드 버튼 행
        upload_row = QHBoxLayout()
        upload_label = QLabel("분석 파일")
        upload_label.setStyleSheet("font-size: 9pt; font-weight: bold; color: #fbbf24;")
        btn_add_files = QPushButton("+ 파일 추가")
        btn_add_files.clicked.connect(self.browse_files)
        btn_remove = QPushButton("선택 제거")
        btn_remove.clicked.connect(self.remove_selected_file)
        btn_clear = QPushButton("전체 비우기")
        btn_clear.clicked.connect(self.clear_files)
        upload_row.addWidget(upload_label)
        upload_row.addStretch()
        upload_row.addWidget(btn_add_files)
        upload_row.addWidget(btn_remove)
        upload_row.addWidget(btn_clear)

        right_panel.addLayout(upload_row)

        # 파일 리스트 (드래그 앤 드롭 지원)
        self.file_list = FileDropList()
        self.file_list.files_dropped.connect(self.add_files)
        self.file_list.setMinimumHeight(180)

        right_panel.addWidget(self.file_list, 1)

        # 결과 미리보기
        result_label = QLabel("결과 미리보기")
        result_label.setStyleSheet("font-size: 9pt; font-weight: bold; color: #fbbf24;")
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText("분석 결과가 여기에 표시됩니다...")

        right_panel.addWidget(result_label)
        right_panel.addWidget(self.result_view, 1)

        # ── 좌우 배치 ──
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(320)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        body_layout.addWidget(left_widget)
        body_layout.addWidget(right_widget, 1)

        main_layout.addWidget(body, 1)

        # 상태바
        self.statusBar().showMessage("준비 완료")

    def update_engine_ui(self):
        engine = self.config.engine
        self.btn_claude.setChecked(engine == "claude")
        self.btn_gemini.setChecked(engine == "gemini")

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(self.config.get_models(engine))
        current_model = self.config.get_model(engine)
        idx = self.model_combo.findText(current_model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        self.model_combo.blockSignals(False)

        api_key = self.config.get_api_key(engine)
        if api_key:
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "****"
            self.api_status.setText(f"\u25cf {engine.title()} 연결됨 ({masked})")
            self.api_status.setStyleSheet("color: #22c55e; font-size: 8pt;")
        else:
            self.api_status.setText(f"\u25cf {engine.title()} API 미설정")
            self.api_status.setStyleSheet("color: #ef4444; font-size: 8pt;")

    def set_engine(self, engine):
        self.config.engine = engine
        self.config.save()
        self.update_engine_ui()

    def on_model_changed(self, model):
        if model:
            self.config.set_model(model)
            self.config.save()

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "파일 선택",
            "",
            "지원 파일 (*.pdf *.docx *.hwp *.hwpx *.txt *.md *.html *.htm);;모든 파일 (*)",
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        existing = [self.file_list.item(i).data(Qt.UserRole)
                    for i in range(self.file_list.count())]
        for f in files:
            if f not in existing:
                item = QListWidgetItem(os.path.basename(f))
                item.setData(Qt.UserRole, f)
                item.setToolTip(f)
                self.file_list.addItem(item)
        self.statusBar().showMessage(f"파일 {self.file_list.count()}개 등록됨")

    def remove_selected_file(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def clear_files(self):
        self.file_list.clear()
        self.statusBar().showMessage("파일 목록 비움")

    def get_output_format(self):
        if self.radio_pdf.isChecked():
            return "pdf"
        elif self.radio_word.isChecked():
            return "word"
        return "html"

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec_():
            self.update_engine_ui()

    def start_analysis(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "알림", "분석할 파일을 추가하세요.")
            return

        api_key = self.config.get_api_key()
        if not api_key:
            QMessageBox.warning(
                self, "알림",
                "API Key가 설정되지 않았습니다.\n설정(톱니바퀴) 버튼에서 API Key를 입력하세요."
            )
            return

        self.btn_analyze.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        file_path = self.file_list.item(0).data(Qt.UserRole)
        engine = self.config.engine
        model = self.config.get_model()

        try:
            analyzer = create_analyzer(engine, api_key, model)
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
            self.btn_analyze.setEnabled(True)
            self.progress.setVisible(False)
            return

        self.worker = AnalysisWorker(analyzer, file_path, self.prompt_text)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_result.connect(self.on_analysis_done)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_progress(self, value):
        self.progress.setValue(value)

    def on_analysis_done(self, html_result):
        self.progress.setValue(100)
        self.result_view.setHtml(html_result[:5000])

        fmt = self.get_output_format()
        file_path = self.file_list.item(0).data(Qt.UserRole)
        stem = Path(file_path).stem
        output_dir = self.config.output_dir or str(Path(file_path).parent)
        output_path = os.path.join(output_dir, f"{stem}_분석결과.{fmt if fmt != 'word' else 'docx'}")

        try:
            saved = export(html_result, output_path, fmt)
            self.statusBar().showMessage(f"저장 완료: {saved}")
        except Exception as e:
            QMessageBox.warning(self, "저장 오류", str(e))

        self.btn_analyze.setEnabled(True)
        self.progress.setVisible(False)

    def on_analysis_error(self, error_msg):
        QMessageBox.critical(self, "분석 오류", error_msg)
        self.btn_analyze.setEnabled(True)
        self.progress.setVisible(False)


class FileDropList(QListWidget):
    """드래그 앤 드롭을 지원하는 파일 리스트"""
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.NoDragDrop)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setWordWrap(True)
        self.setAlternatingRowColors(False)
        self.viewport().setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if files:
            self.files_dropped.emit(files)
```

### 8-7. app/ui/settings_dialog.py

```python
"""설정 다이얼로그 - API 키 입력, 엔진/모델 선택"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QFormLayout, QMessageBox,
)
from PyQt5.QtCore import Qt
from app.core.config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("설정")
        self.setFixedSize(520, 420)
        self.setup_ui()
        self.load_values()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Claude 설정 ──
        claude_group = QGroupBox("Claude (Anthropic)")
        claude_form = QFormLayout()
        self.claude_key = QLineEdit()
        self.claude_key.setEchoMode(QLineEdit.Password)
        self.claude_key.setPlaceholderText("sk-ant-...")
        self.claude_model = QComboBox()
        self.claude_model.addItems(self.config.get_models("claude"))
        claude_form.addRow("API Key:", self.claude_key)
        claude_form.addRow("모델:", self.claude_model)

        # 키 검증 버튼
        self.btn_verify_claude = QPushButton("연결 테스트")
        self.btn_verify_claude.clicked.connect(lambda: self.verify_key("claude"))
        claude_form.addRow("", self.btn_verify_claude)
        claude_group.setLayout(claude_form)

        # ── Gemini 설정 ──
        gemini_group = QGroupBox("Gemini (Google)")
        gemini_form = QFormLayout()
        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.Password)
        self.gemini_key.setPlaceholderText("AIza...")
        self.gemini_model = QComboBox()
        self.gemini_model.addItems(self.config.get_models("gemini"))
        gemini_form.addRow("API Key:", self.gemini_key)
        gemini_form.addRow("모델:", self.gemini_model)

        self.btn_verify_gemini = QPushButton("연결 테스트")
        self.btn_verify_gemini.clicked.connect(lambda: self.verify_key("gemini"))
        gemini_form.addRow("", self.btn_verify_gemini)
        gemini_group.setLayout(gemini_form)

        # ── 출력 설정 ──
        output_group = QGroupBox("출력 설정")
        output_form = QFormLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("기본: 입력 파일과 같은 폴더")
        btn_browse = QPushButton("찾아보기...")
        btn_browse.clicked.connect(self.browse_output_dir)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(btn_browse)
        output_form.addRow("저장 폴더:", dir_layout)
        output_group.setLayout(output_form)

        # ── 버튼 ──
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("저장")
        btn_save.setObjectName("btnAnalyze")  # 강조 스타일 재사용
        btn_save.clicked.connect(self.save_and_close)
        btn_cancel = QPushButton("취소")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addWidget(claude_group)
        layout.addWidget(gemini_group)
        layout.addWidget(output_group)
        layout.addLayout(btn_layout)

    def load_values(self):
        self.claude_key.setText(self.config.get_api_key("claude"))
        self.gemini_key.setText(self.config.get_api_key("gemini"))
        claude_model = self.config.get_model("claude")
        gemini_model = self.config.get_model("gemini")
        idx = self.claude_model.findText(claude_model)
        if idx >= 0:
            self.claude_model.setCurrentIndex(idx)
        idx = self.gemini_model.findText(gemini_model)
        if idx >= 0:
            self.gemini_model.setCurrentIndex(idx)
        self.output_dir.setText(self.config.output_dir)

    def save_and_close(self):
        self.config.set_api_key(self.claude_key.text().strip(), "claude")
        self.config.set_api_key(self.gemini_key.text().strip(), "gemini")
        self.config.set_model(self.claude_model.currentText(), "claude")
        self.config.set_model(self.gemini_model.currentText(), "gemini")
        self.config.output_dir = self.output_dir.text().strip()
        self.config.save()
        self.accept()

    def verify_key(self, engine):
        key = self.claude_key.text().strip() if engine == "claude" else self.gemini_key.text().strip()
        model = self.claude_model.currentText() if engine == "claude" else self.gemini_model.currentText()

        if not key:
            QMessageBox.warning(self, "알림", "API Key를 입력하세요.")
            return

        from app.core.analyzer import create_analyzer
        try:
            analyzer = create_analyzer(engine, key, model)
            if analyzer.validate_key():
                QMessageBox.information(self, "성공", f"{engine.title()} API 연결 성공!")
            else:
                QMessageBox.warning(self, "실패", f"{engine.title()} API 키가 유효하지 않습니다.")
        except ImportError as e:
            QMessageBox.warning(self, "패키지 필요", str(e))
        except Exception as e:
            QMessageBox.critical(self, "오류", f"연결 실패:\n{e}")

    def browse_output_dir(self):
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_dir.setText(folder)
```

---

## 9. 실행 방법

```bash
# 의존성 설치
pip install PyQt5 anthropic google-generativeai PyMuPDF python-docx htmldocx weasyprint

# 앱 실행
python main.py

# exe 빌드 (향후)
pyinstaller --onefile --windowed --name "AnalysisSolution" main.py
```

---

## 10. Git 정보

- **리포지토리**: https://github.com/hsboy89/analysisSolution
- **브랜치**: `dev` (개발), `main` (안정)
- **이전 리모트**: `http://172.31.1.96:9999/ax/visionTools.git` (내부 서버, 필요 시 재연결 가능)
  ```bash
  git remote add internal http://172.31.1.96:9999/ax/visionTools.git
  ```

---

## 11. 향후 확장 계획

| 우선순위 | 항목 | 비고 |
|---------|------|------|
| 1 | API 연동 실제 테스트 | API Key 확보 후 |
| 2 | 복수 파일 순차 분석 | 현재 첫 번째 파일만, 큐 방식으로 확장 |
| 3 | 프롬프트 편집기 | GUI에서 작업지시서 직접 편집/선택 |
| 4 | GPT(OpenAI) 엔진 추가 | BaseAnalyzer 상속으로 쉽게 확장 |
| 5 | PyInstaller exe 빌드 | 단일 실행파일 배포 |
| 6 | 결과물 미리보기 브라우저 | QWebEngineView로 실제 HTML 렌더링 |
