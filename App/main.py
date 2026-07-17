# --- Import Modules --- #

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QPushButton
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

        self.arrow_format = QTextCharFormat()
        self.arrow_format.setForeground(QColor("#f29901"))

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
        in_arrow = False
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

            if char in '()[]}{,. \n"':
                in_variable = False
                in_double_variable = False
                in_arrow = False
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

            if char == "/" and not in_string and not in_variable and not in_comment:
                in_label = True

            if char == r"\n" or char == "\n":
                in_label = False
            
            if in_label and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.block_label_operator_format,
                )

            if char in "+-*/!=<>" and not in_variable and not in_string and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.block_label_operator_format,
                )

            if char == ">" and text[i - 1] == "=":
                in_arrow = True

            if in_arrow and not in_comment and not in_string:
                self.setFormat(
                    i,
                    1,
                    self.arrow_format,
                )
                self.setFormat(
                    i - 1,
                    1,
                    self.arrow_format,
                )

            if char == ";" and not in_comment:
                self.setFormat(
                    i,
                    1,
                    self.arrow_format,
                )

            i += 1

# --- Define Python Syntax Highlighter --- #

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#f4d37b"))

        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor("#479fe1"))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#70c501"))

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#ff6eff"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#8e8e8e"))

        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#fa5f58"))

        self.pre_keyword_format = QTextCharFormat()
        self.pre_keyword_format.setForeground(QColor("#f29901"))

        self.post_keyword_format = QTextCharFormat()
        self.post_keyword_format.setForeground(QColor("#01bf78"))

        self.colon_format = QTextCharFormat()
        self.colon_format.setForeground(QColor("#FFFFFF"))
        
        self.rules = [
            (
                QRegularExpression(r"\b(import|from|as|if|elif|else|for|while|break|continue|return|try|except|finally|with|pass|yield|raise|print|input)\b"),
                self.keyword_format,
            ),
            (
                QRegularExpression(r"\b(def|class|lambda)\b"),
                self.pre_keyword_format,
            ),
            (
                QRegularExpression(r"\b(and|or|not|is|in|True|False|None|int|float|complex|str|dict|set|frozenset|bool|bytes|bytearray|memoryview|NoneType|super|self)\b"),
                self.post_keyword_format,
            )
        ]

    def highlightBlock(self, text):
        i = 0
        in_string = False
        in_argument = False
        in_comment = False
        quote_type = None
        escaped = False

        while i < len(text):
            char = text[i]

            if in_string:
                self.setFormat(
                    i,
                    1,
                    self.string_format,
                )

                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote_type:
                    in_string = False
                    quote_type = None

                i += 1
                continue

            if char == "#" and not in_comment:
                in_comment = True

            if in_comment:
                self.setFormat(
                    i,
                    1,
                    self.comment_format,
                )
                i += 1
                continue

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

            if char in '"\'':
                in_string = True
                quote_type = char
                self.setFormat(
                    i,
                    1,
                    self.string_format,
                )
                i += 1
                continue

            if char in "+-*/=!<>":
                self.setFormat(
                    i,
                    1,
                    self.operator_format,
                )
                
            i += 1

        if not in_string and not in_comment:
            function_matcher = QRegularExpression(r"\b(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)")
            function_it = function_matcher.globalMatch(text)

            while function_it.hasNext():
                match = function_it.next()
                self.setFormat(
                    match.capturedStart(2),
                    match.capturedLength(2),
                    self.function_format,
                )

        if ":" in text and not in_string and not in_comment:
            self.setFormat(
                text.rindex(":"),
                1,
                self.colon_format
            )

        for expression, fmt in self.rules:
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                if not in_string and not in_comment:
                    self.setFormat(
                        match.capturedStart(),
                        match.capturedLength(),
                        fmt,
                    )

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
        self.page_container.addWidget(File())
        self.page_container.addWidget(Settings())
        self.page_container.setCurrentIndex(0)


# --- Text Editor Page --- #
class Editor(QWidget):
    def __init__(self):
        super().__init__()

        self.button_stylesheet = """QPushButton {font-family: Consolas; font-size: 28px; background-color: none; border: none; color: #ababab; font-weight: 550; margin: 4px; margin-right: 18px;}"""

        self.file_button = QPushButton("File")
        self.file_button.setStyleSheet(self.button_stylesheet)
        self.run_button = QPushButton("Run")
        self.run_button.setStyleSheet(self.button_stylesheet)
        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet(self.button_stylesheet)

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
                    font-size: 30px;
                }
            """
        )

        self.syntax_highlighter = PythonHighlighter(
            self.text_editor.document()
        )

        self.line_number_area = QWidget(self)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.file_button)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()

        editor_layout = QHBoxLayout()
        editor_layout.addWidget(self.text_editor)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(editor_layout)

        self.setLayout(main_layout)

class File(QWidget):
    def __init__(self):
        super().__init__()

class Settings(QWidget):
    def __init__(self):
        super().__init__()
            

# --- Main Loop --- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    QApplication.setCursorFlashTime(0)
    sys.exit(app.exec())