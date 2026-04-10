"""다크 모던 테마 스타일시트"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1a1b2e;
    color: #e0e0e0;
}

QDialog QLabel {
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

/* ── 텍스트 에디터 (로그) ── */
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
