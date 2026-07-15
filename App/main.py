# --- Import Modules --- #

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPlainTextEdit, QVBoxLayout
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import QRegularExpression

# --- Define Direct+ Syntax Highlighter --- #
class DirectHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#f4d37b"))

        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor("#479fe1"))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#70c501"))

        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#ff6eff"))

        self.double_variable_format = QTextCharFormat()
        self.double_variable_format.setForeground(QColor("#01bf78"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#8e8e8e"))

        self.block_label_operator_format = QTextCharFormat()
        self.block_label_operator_format.setForeground(QColor("#fa5f58"))

        self.rules = [
            (
                QRegularExpression(r"\b(paste|var|run|add|sub|mul|div|if|loop|length|concat|letter|contains|console|wait|random|hash|slice|enter|delete|replace|item|numof|use|break|sqrt|round|mod|color|else|type|exists|turbo|scope|build)\b"),
                self.keyword_format,
            ),
        ]

    def highlightBlock(self, text):
        for expression, fmt in self.rules:
            it = expression.globalMatch(text)

            while it.hasNext():
                match = it.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt,
                )

        i = 0
        in_string = False
        in_argument = False
        in_variable = False
        in_double_variable = False
        in_label = False
        in_comment = False

        while i < len(text):
            char = text[i]

            if char == "$":
                in_comment = True

            if in_comment:
                self.setFormat(
                    i,
                    1,
                    self.comment_format,
                )

            if char in "([" and not in_comment:
                in_argument = True

            if char in ")]":
                in_argument = False

            if in_argument or char in ")]" and not in_string and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.argument_format,
                )

            if char == '"' and not in_comment:
                in_string = not in_string
            
            if in_string or char == '"' and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.string_format,
                )

            if char == "@" and not in_comment:
                in_variable = True
                if text[i - 1] == "@":
                    in_variable = False
                    in_double_variable = True

            if char in r'()[]{},. "':
                in_variable = False
                in_double_variable = False
                in_label = False

            if in_variable and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.variable_format,
                )

            if in_double_variable and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.double_variable_format,
                )
                self.setFormat(
                    i - 1,
                    1,
                    self.double_variable_format,
                )

            if char in "+-*/=<>!" and not in_string and not in_variable and not in_comment:
                in_label = True

            if char == r"\n":
                in_label = False
            
            if in_label == True:
                self.setFormat(
                    i,
                    1,
                    self.block_label_operator_format,
                )

            i += 1

# --- Define Main Application Window --- #
class App(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Setup --- #
        self.resize(900, 500)
        self.setMinimumSize(900, 500)
        self.setStyleSheet(
            """
            QMainWindow
            {
                background-color: #1c1c1c;
            }
            """
        )

        # --- QStackedWidget Setup - Make Multiple Pages --- #
        self.page_container = QStackedWidget()
        self.setCentralWidget(self.page_container)
        self.page_container.addWidget(Editor())
        self.page_container.setCurrentIndex(0)


# --- Text Editor Page --- #
class Editor(QWidget):
    def __init__(self):
        super().__init__()

        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlaceholderText("welcome to gemstone text!\nbased on the direct+ text editor\ndocumentation: \nbug report: \nstart typing to dismiss this message.")
        self.text_editor.setTabChangesFocus(False)
        self.text_editor.setCursorWidth(2)

        self.text_editor.setStyleSheet(
            """
                QWidget
                {
                    border: none;
                    background-color: #1c1c1c;
                    font-family: Consolas;
                    font-size: 32px;
                }
            """
        )

        self.syntax_highlighter = DirectHighlighter(
            self.text_editor.document()
        )

        self.line_number_area = QWidget(self)


        editor_layout = QVBoxLayout()
        editor_layout.addWidget(self.text_editor)
        self.setLayout(editor_layout)
            

# --- Main Loop --- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    QApplication.setCursorFlashTime(0)
    sys.exit(app.exec())