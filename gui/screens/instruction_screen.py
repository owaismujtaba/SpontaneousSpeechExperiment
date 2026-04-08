from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import TRIALS_PER_SET, TOTAL_SETS, TUTORIAL_NUM_IMAGES


class InstructionScreen(QWidget):
    """Welcome screen — no set selector, just instructions and a start prompt."""

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(28)
        root.setContentsMargins(80, 60, 80, 60)

        # ── Title ──────────────────────────────────────────────────────
        title = QLabel("Experimento de Habla Espontánea")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4a9eff;")
        root.addWidget(title)

        # ── Divider ────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2a4a; border: none; max-height: 1px;")
        root.addWidget(sep)

        # ── Instructions ───────────────────────────────────────────────
        body = QLabel(
            "Describa detalladamente lo que ve en cada imagen.\n\n"
            "De vez en cuando aparecerá brevemente una  +  en la pantalla (cruz de fijación).\n"
            "En ese momento no tiene que decir nada — simplemente mire la cruz."
        )
        body.setFont(QFont("Segoe UI", 16))
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet("color: #c8c8c8;")
        root.addWidget(body)

        # ── Session info ───────────────────────────────────────────────
        info = QLabel(
            f"{TOTAL_SETS} sets  ·  {TRIALS_PER_SET} imágenes por set\n"
            f"Primero completará una sesión de práctica con {TUTORIAL_NUM_IMAGES} imágenes de ejemplo."
        )
        info.setFont(QFont("Segoe UI", 13))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet("color: #555;")
        root.addWidget(info)

        # ── Start prompt ───────────────────────────────────────────────
        start = QLabel("Presione la  BARRA ESPACIADORA  para comenzar la práctica")
        start.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start.setStyleSheet("color: #4a9eff; letter-spacing: 1px;")
        root.addWidget(start)

        esc = QLabel("ESC  =  salir")
        esc.setFont(QFont("Segoe UI", 11))
        esc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        esc.setStyleSheet("color: #3a3a5a;")
        root.addWidget(esc)
