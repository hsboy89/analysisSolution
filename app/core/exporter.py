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
