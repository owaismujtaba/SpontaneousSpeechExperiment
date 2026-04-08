from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class TrialScreen(QWidget):
    """
    Dual-purpose screen that renders either the current COCO image
    or the inter-trial fixation cross.

    Display logic is driven entirely by MainWindow; this widget only
    manages layout and pixel scaling.
    """

    def __init__(self):
        super().__init__()
        self._current_pixmap: QPixmap | None = None
        self._build()

    # ------------------------------------------------------------------
    # Public API (called by MainWindow)
    # ------------------------------------------------------------------

    def init_set(self, set_number: int, total: int) -> None:
        """Store set metadata shown in the header."""
        self._total = total
        self._set_lbl.setText(f"Set  {set_number}")

    def show_image(self, path: Path, trial_number: int) -> None:
        self._progress.setText(f"Imagen  {trial_number} / {self._total}")
        self._hint.setText("Presione  PAGE DOWN o ↓  cuando haya terminado de describir")
        self._hint.setStyleSheet("color: #4a4a6a;")

        self._current_pixmap = QPixmap(str(path))
        self._display.setStyleSheet("")
        self._display.setText("")
        self._rescale()

    def show_fixation(self) -> None:
        self._current_pixmap = None
        self._display.clear()
        self._display.setText("+")
        self._display.setFont(QFont("Segoe UI", 96, QFont.Weight.Bold))
        self._display.setStyleSheet("color: #e0e0e0;")
        self._progress.setText("")
        self._hint.setText("")

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._rescale()

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 12, 48, 12)
        layout.setSpacing(6)

        # ── Header ─────────────────────────────────────────────────────
        header = QHBoxLayout()

        self._progress = QLabel()
        self._progress.setFont(QFont("Segoe UI", 12))
        self._progress.setStyleSheet("color: #555;")

        self._set_lbl = QLabel()
        self._set_lbl.setFont(QFont("Segoe UI", 12))
        self._set_lbl.setStyleSheet("color: #555;")
        self._set_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        header.addWidget(self._progress)
        header.addStretch()
        header.addWidget(self._set_lbl)
        layout.addLayout(header)

        # ── Image / fixation display ────────────────────────────────────
        self._display = QLabel()
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setMinimumSize(100, 100)
        layout.addWidget(self._display, stretch=1)

        # ── Footer hint ────────────────────────────────────────────────
        self._hint = QLabel()
        self._hint.setFont(QFont("Segoe UI", 12))
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint)

    def _rescale(self) -> None:
        if self._current_pixmap is None or self._current_pixmap.isNull():
            return
        size = self._display.size()
        if size.width() < 1 or size.height() < 1:
            return
        scaled = self._current_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._display.setPixmap(scaled)
