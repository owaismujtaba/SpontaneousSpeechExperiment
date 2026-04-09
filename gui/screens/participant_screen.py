from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ParticipantScreen(QWidget):
    """First screen — collects Participant ID and Session ID before the experiment."""

    confirmed = pyqtSignal(str, str)   # (participant_id, session_id)

    _FIELD_STYLE = """
        QLineEdit {
            background-color: #16213e;
            color: #e0e0e0;
            border: 2px solid #4a9eff;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 18px;
        }
        QLineEdit:focus { border-color: #7bbfff; }
    """
    _BTN_STYLE = """
        QPushButton {
            background-color: #4a9eff;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 12px 40px;
            font-size: 17px;
            font-weight: bold;
        }
        QPushButton:hover   { background-color: #6ab4ff; }
        QPushButton:pressed { background-color: #2a7edf; }
        QPushButton:disabled { background-color: #2a3a5a; color: #555; }
    """

    def __init__(self):
        super().__init__()
        self._build()

    # ── Build ───────────────────────────────────────────────────────────────

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(30)
        root.setContentsMargins(0, 0, 0, 0)

        # Card container (fixed width so it looks centred on full-screen)
        card = QWidget()
        card.setFixedWidth(520)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(24)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Identificación del Participante")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4a9eff;")
        card_layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2a4a; border: none; max-height: 1px;")
        card_layout.addWidget(sep)

        # Participant ID
        card_layout.addWidget(self._make_label("ID del Participante"))
        self._pid_field = QLineEdit()
        self._pid_field.setPlaceholderText("p.ej. P01")
        self._pid_field.setStyleSheet(self._FIELD_STYLE)
        self._pid_field.textChanged.connect(self._on_text_changed)
        self._pid_field.returnPressed.connect(self._try_confirm)
        card_layout.addWidget(self._pid_field)

        # Session ID
        card_layout.addWidget(self._make_label("ID de Sesión"))
        self._sid_field = QLineEdit()
        self._sid_field.setPlaceholderText("p.ej. S01")
        self._sid_field.setStyleSheet(self._FIELD_STYLE)
        self._sid_field.textChanged.connect(self._on_text_changed)
        self._sid_field.returnPressed.connect(self._try_confirm)
        card_layout.addWidget(self._sid_field)

        # Confirm button
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn = QPushButton("Confirmar y continuar")
        self._btn.setStyleSheet(self._BTN_STYLE)
        self._btn.setEnabled(False)
        self._btn.clicked.connect(self._try_confirm)
        btn_row.addWidget(self._btn)
        card_layout.addLayout(btn_row)

        # Hint
        hint = QLabel("ESC  =  salir")
        hint.setFont(QFont("Segoe UI", 11))
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #3a3a5a;")
        card_layout.addWidget(hint)

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def _make_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 14))
        lbl.setStyleSheet("color: #a0a0c0;")
        return lbl

    # ── Slots ───────────────────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        both_filled = bool(self._pid_field.text().strip()) and \
                      bool(self._sid_field.text().strip())
        self._btn.setEnabled(both_filled)

    def _try_confirm(self) -> None:
        pid = self._pid_field.text().strip()
        sid = self._sid_field.text().strip()
        if pid and sid:
            self.confirmed.emit(pid, sid)

    # ── Public ──────────────────────────────────────────────────────────────

    def focus_first_field(self) -> None:
        self._pid_field.setFocus()
