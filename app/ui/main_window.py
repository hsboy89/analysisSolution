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
        """현재 선택된 작업지시서를 로드"""
        if hasattr(self, 'prompt_combo') and self.prompt_combo.currentData():
            path = Path(self.prompt_combo.currentData())
            if path.exists():
                return path.read_text(encoding="utf-8")
        # fallback: 기본 파일
        prompt_path = self._get_project_root() / "분석지_작업지시서_v12.1.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    @staticmethod
    def _get_project_root() -> Path:
        return Path(__file__).parent.parent.parent

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

        # 작업지시서 선택 (엔진 패널 안에 포함)
        separator = QLabel("")
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #3d4470; margin: 4px 0;")
        engine_layout.addWidget(separator)

        prompt_title = QLabel("작업지시서")
        prompt_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #fbbf24;")
        engine_layout.addWidget(prompt_title)

        self.prompt_combo = QComboBox()
        self.prompt_combo.setToolTip("분석에 사용할 작업지시서 파일을 선택하세요")
        self._scan_prompts()
        self.prompt_combo.currentIndexChanged.connect(self._on_prompt_changed)
        engine_layout.addWidget(self.prompt_combo)

        prompt_btn_row = QHBoxLayout()
        btn_add_prompt = QPushButton("+ 추가")
        btn_add_prompt.setToolTip("외부 작업지시서 파일 불러오기")
        btn_add_prompt.clicked.connect(self._add_prompt_file)
        btn_reload_prompt = QPushButton("새로고침")
        btn_reload_prompt.clicked.connect(self._scan_prompts)
        prompt_btn_row.addWidget(btn_add_prompt)
        prompt_btn_row.addWidget(btn_reload_prompt)
        prompt_btn_row.addStretch()
        engine_layout.addLayout(prompt_btn_row)

        # 출력 형식 (엔진 패널 안에 포함)
        separator2 = QLabel("")
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background: #3d4470; margin: 4px 0;")
        engine_layout.addWidget(separator2)

        format_title = QLabel("출력 형식")
        format_title.setStyleSheet("font-size: 9pt; font-weight: bold; color: #fbbf24;")
        engine_layout.addWidget(format_title)

        format_row = QHBoxLayout()
        self.radio_html = QRadioButton("HTML")
        self.radio_pdf = QRadioButton("PDF")
        self.radio_word = QRadioButton("Word")
        self.radio_html.setChecked(True)
        self.format_group = QButtonGroup()
        self.format_group.addButton(self.radio_html)
        self.format_group.addButton(self.radio_pdf)
        self.format_group.addButton(self.radio_word)
        format_row.addWidget(self.radio_html)
        format_row.addWidget(self.radio_pdf)
        format_row.addWidget(self.radio_word)
        format_row.addStretch()
        engine_layout.addLayout(format_row)

        left_panel.addWidget(engine_panel)

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

    def _scan_prompts(self):
        """프로젝트 루트에서 작업지시서 .md 파일을 검색"""
        self.prompt_combo.blockSignals(True)
        current = self.prompt_combo.currentData()
        self.prompt_combo.clear()

        root = self._get_project_root()
        md_files = sorted(root.glob("*작업지시서*.md")) + sorted(root.glob("*지시서*.md"))
        # 중복 제거
        seen = set()
        for f in md_files:
            if str(f) not in seen:
                seen.add(str(f))
                self.prompt_combo.addItem(f.name, str(f))

        # 없으면 안내 항목
        if self.prompt_combo.count() == 0:
            self.prompt_combo.addItem("(작업지시서 없음 - 추가하세요)", "")

        # 이전 선택 복원
        if current:
            idx = self.prompt_combo.findData(current)
            if idx >= 0:
                self.prompt_combo.setCurrentIndex(idx)

        self.prompt_combo.blockSignals(False)
        self.prompt_text = self._load_prompt()

    def _add_prompt_file(self):
        """외부 작업지시서 파일을 선택해서 추가"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "작업지시서 파일 선택", "",
            "마크다운 (*.md);;텍스트 (*.txt);;모든 파일 (*)"
        )
        if file_path:
            # 이미 목록에 있는지 확인
            for i in range(self.prompt_combo.count()):
                if self.prompt_combo.itemData(i) == file_path:
                    self.prompt_combo.setCurrentIndex(i)
                    return
            self.prompt_combo.addItem(Path(file_path).name, file_path)
            self.prompt_combo.setCurrentIndex(self.prompt_combo.count() - 1)

    def _on_prompt_changed(self, index):
        """작업지시서 변경 시 프롬프트 다시 로드"""
        self.prompt_text = self._load_prompt()
        name = self.prompt_combo.currentText()
        self.statusBar().showMessage(f"작업지시서: {name}")

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

        # 프롬프트 최신 로드
        self.prompt_text = self._load_prompt()
        if not self.prompt_text:
            QMessageBox.warning(self, "알림", "작업지시서가 선택되지 않았습니다.")
            return

        self.btn_analyze.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # 분석할 파일 목록 준비 (전체 파일 순차 처리)
        self._analysis_queue = []
        for i in range(self.file_list.count()):
            self._analysis_queue.append(self.file_list.item(i).data(Qt.UserRole))
        self._analysis_index = 0
        self._analysis_total = len(self._analysis_queue)

        engine = self.config.engine
        model = self.config.get_model()

        try:
            self._analyzer = create_analyzer(engine, api_key, model)
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
            self.btn_analyze.setEnabled(True)
            self.progress.setVisible(False)
            return

        self._run_next_analysis()

    def _run_next_analysis(self):
        """큐에서 다음 파일 분석 시작"""
        if self._analysis_index >= self._analysis_total:
            self.btn_analyze.setEnabled(True)
            self.progress.setVisible(False)
            self.statusBar().showMessage(
                f"전체 {self._analysis_total}개 파일 분석 완료!"
            )
            return

        file_path = self._analysis_queue[self._analysis_index]
        name = os.path.basename(file_path)
        self.statusBar().showMessage(
            f"분석 중 ({self._analysis_index + 1}/{self._analysis_total}): {name}"
        )

        self.worker = AnalysisWorker(self._analyzer, file_path, self.prompt_text)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(lambda msg: self.statusBar().showMessage(msg))
        self.worker.finished_result.connect(self.on_analysis_done)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_progress(self, value):
        # 전체 진행률 계산
        base = (self._analysis_index / self._analysis_total) * 100
        chunk = (1 / self._analysis_total) * value
        self.progress.setValue(int(base + chunk))

    def on_analysis_done(self, html_result):
        file_path = self._analysis_queue[self._analysis_index]
        stem = Path(file_path).stem

        # 결과 미리보기 (마지막 결과만)
        self.result_view.setHtml(html_result[:5000])

        # 내보내기
        fmt = self.get_output_format()
        output_dir = self.config.output_dir or str(Path(file_path).parent)
        ext = fmt if fmt != "word" else "docx"
        output_path = os.path.join(output_dir, f"{stem}_분석결과.{ext}")

        try:
            saved = export(html_result, output_path, fmt)
            self.statusBar().showMessage(f"저장 완료: {saved}")
        except Exception as e:
            QMessageBox.warning(self, "저장 오류", str(e))

        # 다음 파일로
        self._analysis_index += 1
        self._run_next_analysis()

    def on_analysis_error(self, error_msg):
        file_path = self._analysis_queue[self._analysis_index]
        name = os.path.basename(file_path)
        QMessageBox.critical(self, "분석 오류", f"{name}:\n{error_msg}")

        # 오류 나도 다음 파일 계속 진행
        self._analysis_index += 1
        self._run_next_analysis()


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
