"""AI 분석 엔진 - 공통 인터페이스 + Claude/Gemini 구현"""
import re
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

    @staticmethod
    def extract_html(text: str) -> str:
        """AI 응답에서 순수 HTML을 추출한다.

        - ```html ... ``` 코드블록이 있으면 내부 HTML만 추출
        - <!DOCTYPE html> 또는 <html 태그가 있으면 그 부분부터 끝까지 추출
        - 아무것도 없으면 원본 그대로 반환
        """
        # 1) ```html ... ``` 코드블록 추출
        m = re.search(r'```html\s*\n(.*?)```', text, re.DOTALL)
        if m:
            return m.group(1).strip()

        # 2) ``` ... ``` 일반 코드블록 안에 HTML이 있는 경우
        m = re.search(r'```\s*\n(<!DOCTYPE|<html)(.*?)```', text, re.DOTALL | re.IGNORECASE)
        if m:
            return (m.group(1) + m.group(2)).strip()

        # 3) 코드블록 없이 HTML이 직접 포함된 경우
        m = re.search(r'(<!DOCTYPE html.*)', text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()

        m = re.search(r'(<html.*)', text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 4) HTML 태그가 전혀 없으면 원본 반환
        return text


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

            result = self.extract_html(message.content[0].text)

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

            result = self.extract_html(response.text)

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
