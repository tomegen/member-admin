from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

ACCENT = "#2563eb"

# colors come from the palette wherever possible, so light and dark mode both work
STYLESHEET = """
QPushButton#primary {
    background-color: %(accent)s; color: white; border: none; border-radius: 6px;
    padding: 9px 18px; font-weight: 600;
}
QPushButton#primary:hover { background-color: #1d4ed8; }
QPushButton#primary:disabled { background-color: palette(mid); color: palette(midlight); }
QPushButton#secondary { padding: 8px 16px; border-radius: 6px; border: 1px solid palette(mid); }
QPushButton#secondary:hover { border-color: %(accent)s; }
QPushButton#link {
    border: none; background: transparent; color: %(accent)s; text-decoration: underline; padding: 2px 8px;
}
QFrame#card { border: 1px solid palette(mid); border-radius: 10px; }
QLabel#cardValue { font-size: 34px; font-weight: 700; }
QLabel#muted { color: palette(placeholder-text); }
QLabel#dropzone { border: 2px dashed palette(mid); border-radius: 12px; padding: 28px; }
QTabBar::tab { padding: 10px 18px; }
QTabBar::tab:selected { font-weight: 600; }
""" % {"accent": ACCENT}


def apply_theme(app):
    app.setStyle("Fusion")
    font = QFont(app.font())
    font.setPointSize(13)
    app.setFont(font)
    app.setStyleSheet(STYLESHEET)


def heading(text, size=22):
    label = QLabel(text)
    font = label.font()
    font.setPointSize(size)
    font.setBold(True)
    label.setFont(font)
    return label


def muted(text):
    label = QLabel(text)
    label.setObjectName("muted")
    label.setWordWrap(True)
    return label


def primary_button(text):
    button = QPushButton(text)
    button.setObjectName("primary")
    return button


def secondary_button(text):
    button = QPushButton(text)
    button.setObjectName("secondary")
    return button
