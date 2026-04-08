from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import TOTAL_SETS


class BetweenSetScreen(QWidget):
    """
    Shown after each set completes (except the final one).
    Participant can continue to the next set or exit.
    """

    def __init__(self):
        super().__init__()
        self._set_lbl: QLabel | None = None
        self._next_lbl: QLabel | None = None
        self._build()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def update(self, completed_set: int) -> None:
        """Refresh labels for the set that just finished."""
        self._set_lbl.setText(f"Set {completed_set} de {TOTAL_SETS} completado")
        next_set = completed_set + 1
        self._next_lbl.setText(
            f"Presione  BARRA ESPACIADORA  para continuar con el Set {next_set}"
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(30)
        root.setContentsMargins(80, 60, 80, 60)

        # ── Completion badge ───────────────────────────────────────────
        self._set_lbl = QLabel()
        self._set_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._set_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_lbl.setStyleSheet("color: #4a9eff;")
        root.addWidget(self._set_lbl)

        # ── Divider ────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2a4a; border: none; max-height: 1px;")
        root.addWidget(sep)

        # ── Rest prompt ────────────────────────────────────────────────
        rest = QLabel("Puede tomarse un descanso si lo necesita.")
        rest.setFont(QFont("Segoe UI", 16))
        rest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rest.setStyleSheet("color: #c8c8c8;")
        root.addWidget(rest)

        # ── Next set prompt ────────────────────────────────────────────
        self._next_lbl = QLabel()
        self._next_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._next_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._next_lbl.setStyleSheet("color: #4a9eff; letter-spacing: 1px;")
        root.addWidget(self._next_lbl)

        # ── Exit hint ──────────────────────────────────────────────────
        esc = QLabel("ESC  =  salir del experimento")
        esc.setFont(QFont("Segoe UI", 11))
        esc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        esc.setStyleSheet("color: #3a3a5a;")
        root.addWidget(esc)
