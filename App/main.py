# --- Import Modules --- #

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget


# --- Define Main Application Window --- #
class App(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Setup --- #
        self.resize(900, 500)
        self.setMinimumSize(900, 500)

        # --- QStackedWidget Setup - Make Multiple Pages --- #
        self.page_container = QStackedWidget()
        self.setCentralWidget(self.page_container)
        self.page_container.addWidget(Editor())
        self.page_container.setCurrentIndex(0)


# --- Text Editor Page --- #
class Editor(QWidget):
    pass

# --- Main Loop --- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())