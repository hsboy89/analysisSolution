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
