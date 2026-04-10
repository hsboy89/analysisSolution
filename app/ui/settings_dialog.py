"""설정 다이얼로그 - API 키 입력, 엔진/모델 선택"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QWidget, QMessageBox, QFileDialog,
)
from PyQt5.QtCore import Qt
from app.core.config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("설정")
        self.setFixedSize(500, 330)
        self.setup_ui()
        self.load_values()

    def _section(self, title):
        """타이틀이 박스 안에 있는 섹션 위젯"""
        box = QWidget()
        box.setStyleSheet("""
            QWidget#section {
                background: #1e2140;
                border: 1px solid #2d3154;
                border-radius: 8px;
            }
        """)
        box.setObjectName("section")
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(12, 8, 12, 8)
        vbox.setSpacing(6)
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #fbbf24; font-size: 9pt; font-weight: bold;")
        vbox.addWidget(lbl)
        return box, vbox

    def _row(self, label_text, widget, btn=None):
        row = QHBoxLayout()
        row.setSpacing(15)
        lbl = QLabel(label_text)
        lbl.setFixedWidth(50)
        lbl.setFixedHeight(20)
        lbl.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        widget.setFixedHeight(20)
        widget.setStyleSheet(widget.styleSheet() + "min-height:20px;max-height:20px;padding:2px 6px;font-size:8.5pt;")
        row.addWidget(lbl)
        row.addWidget(widget)
        if btn:
            row.addWidget(btn)
        return row

    def _test_btn(self, engine):
        btn = QPushButton("테스트")
        btn.setFixedSize(50, 22)
        btn.setStyleSheet("font-size: 7.5pt; padding: 0px 2px;")
        btn.clicked.connect(lambda: self.verify_key(engine))
        return btn

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)

        # ── Claude ──
        cg, cl = self._section("Claude (Anthropic)")
        self.claude_key = QLineEdit()
        self.claude_key.setEchoMode(QLineEdit.Password)
        self.claude_key.setPlaceholderText("sk-ant-...")
        cl.addLayout(self._row("API Key:", self.claude_key))
        self.claude_model = QComboBox()
        self.claude_model.addItems(self.config.get_models("claude"))
        cl.addLayout(self._row("모델:", self.claude_model, self._test_btn("claude")))

        # ── Gemini ──
        gg, gl = self._section("Gemini (Google)")
        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.Password)
        self.gemini_key.setPlaceholderText("AIza...")
        gl.addLayout(self._row("API Key:", self.gemini_key))
        self.gemini_model = QComboBox()
        self.gemini_model.addItems(self.config.get_models("gemini"))
        gl.addLayout(self._row("모델:", self.gemini_model, self._test_btn("gemini")))

        # ── 출력 설정 ──
        og, ol = self._section("출력 설정")
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("기본: 입력 파일과 같은 폴더")
        btn_browse = QPushButton("찾기")
        btn_browse.setFixedSize(50, 22)
        btn_browse.setStyleSheet("font-size: 7.5pt; padding: 0px 2px;")
        btn_browse.clicked.connect(self.browse_output_dir)
        ol.addLayout(self._row("저장 폴더:", self.output_dir, btn_browse))

        # ── 하단 버튼 ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_cancel = QPushButton("취소")
        btn_save = QPushButton("저장")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #d97706, stop:1 #f59e0b);
                color: #0f172a; border: none; border-radius: 6px;
                font-size: 9pt; font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #f59e0b, stop:1 #fbbf24);
            }
        """)
        for b in (btn_cancel, btn_save):
            b.setFixedSize(80, 30)
        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_and_close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addWidget(cg)
        layout.addWidget(gg)
        layout.addWidget(og)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def load_values(self):
        self.claude_key.setText(self.config.get_api_key("claude"))
        self.gemini_key.setText(self.config.get_api_key("gemini"))
        idx = self.claude_model.findText(self.config.get_model("claude"))
        if idx >= 0:
            self.claude_model.setCurrentIndex(idx)
        idx = self.gemini_model.findText(self.config.get_model("gemini"))
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
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_dir.setText(folder)
