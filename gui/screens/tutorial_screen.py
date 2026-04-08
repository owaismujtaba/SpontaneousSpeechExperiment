from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap


class TutorialScreen(QWidget):
    """
    Practice session shown before the real experiment.

    Each practice trial has two phases:

      IMAGE   — participant describes the image aloud, then presses PAGE DOWN
      CAPTION — the same image + 5 example captions are shown side-by-side;
                participant reads them and presses PAGE DOWN to continue

    After all practice images a DONE slide prompts the participant to press
    SPACE to begin the actual experiment.

    The parent MainWindow drives phase transitions by calling advance()
    on PAGE DOWN and by checking .phase to decide when SPACE starts the run.
    """

    PHASE_IMAGE   = "image"
    PHASE_CAPTION = "caption"
    PHASE_DONE    = "done"

    # ── Construction ───────────────────────────────────────────────────────

    def __init__(self, trials):
        """
        Args:
            trials: list of {"image": Path, "captions": [str, ...]}
        """
        super().__init__()
        self._trials  = list(trials)
        self._idx     = 0
        self._phase   = self.PHASE_IMAGE
        self._pixmap: QPixmap | None = None
        self._build()

    # ── Public API ─────────────────────────────────────────────────────────

    @property
    def phase(self) -> str:
        return self._phase

    def start(self) -> None:
        self._idx = 0
        self._load_image_phase()

    def advance(self) -> None:
        """Called by MainWindow on PAGE DOWN."""
        if self._phase == self.PHASE_IMAGE:
            self._load_caption_phase()
        elif self._phase == self.PHASE_CAPTION:
            self._idx += 1
            if self._idx < len(self._trials):
                self._load_image_phase()
            else:
                self._load_done()

    # ── Qt overrides ───────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._rescale()

    # ── Private — layout builder ───────────────────────────────────────────

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 12, 48, 12)
        root.setSpacing(6)

        # ── Header ─────────────────────────────────────────────────────
        self._header = QLabel()
        self._header.setFont(QFont("Segoe UI", 12))
        self._header.setStyleSheet("color: #555;")
        self._header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._header)

        # ── Inner stacked area (3 pages) ───────────────────────────────
        self._inner = QStackedWidget()
        root.addWidget(self._inner, stretch=1)

        self._inner.addWidget(self._build_image_page())    # 0
        self._inner.addWidget(self._build_caption_page())  # 1
        self._inner.addWidget(self._build_done_page())     # 2

        # ── Footer hint ────────────────────────────────────────────────
        self._hint = QLabel()
        self._hint.setFont(QFont("Segoe UI", 12))
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet("color: #4a4a6a;")
        root.addWidget(self._hint)

    def _build_image_page(self) -> QWidget:
        """Full-width image for the describe phase."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        self._img_full = QLabel()
        self._img_full.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_full.setMinimumSize(10, 10)
        layout.addWidget(self._img_full)
        return page

    def _build_caption_page(self) -> QWidget:
        """Image on the left, example captions on the right."""
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(24)

        # Left: image
        self._img_split = QLabel()
        self._img_split.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_split.setMinimumSize(10, 10)
        layout.addWidget(self._img_split, stretch=1)

        # Right: captions panel
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: #16213e; border-radius: 10px; }"
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 18, 22, 18)
        panel_layout.setSpacing(0)

        panel_title = QLabel("Ejemplos de descripción")
        panel_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        panel_title.setStyleSheet("color: #4a9eff; background: transparent;")
        panel_layout.addWidget(panel_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2a4a; border: none; max-height: 1px; margin: 10px 0;")
        panel_layout.addWidget(sep)

        self._captions_label = QLabel()
        self._captions_label.setFont(QFont("Segoe UI", 13))
        self._captions_label.setWordWrap(True)
        self._captions_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._captions_label.setStyleSheet(
            "color: #c8c8c8; background: transparent; line-height: 1.6;"
        )
        panel_layout.addWidget(self._captions_label)
        panel_layout.addStretch()

        layout.addWidget(panel, stretch=1)
        return page

    def _build_done_page(self) -> QWidget:
        """Completion slide — shown after all practice trials."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        check = QLabel("✓  Práctica completada")
        check.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check.setStyleSheet("color: #4a9eff;")
        layout.addWidget(check)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            "background: #2a2a4a; border: none; max-height: 1px; margin: 4px 80px;"
        )
        layout.addWidget(sep)

        body = QLabel(
            "Ahora comenzará el experimento real.\n\n"
            "Describa cada imagen con el mayor detalle posible.\n"
            "Cuando haya terminado de describir, presione  PAGE DOWN  o  ↓"
        )
        body.setFont(QFont("Segoe UI", 16))
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet("color: #c8c8c8;")
        layout.addWidget(body)

        start_hint = QLabel("Presione  BARRA ESPACIADORA  para comenzar el experimento")
        start_hint.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        start_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start_hint.setStyleSheet("color: #4a9eff; letter-spacing: 1px;")
        layout.addWidget(start_hint)

        esc = QLabel("ESC  =  salir")
        esc.setFont(QFont("Segoe UI", 11))
        esc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        esc.setStyleSheet("color: #3a3a5a;")
        layout.addWidget(esc)

        return page

    # ── Private — phase transitions ────────────────────────────────────────

    def _load_image_phase(self) -> None:
        self._phase = self.PHASE_IMAGE
        trial = self._trials[self._idx]
        self._pixmap = QPixmap(str(trial["image"]))
        n, total = self._idx + 1, len(self._trials)
        self._header.setText(f"Práctica — Imagen {n} de {total}")
        self._hint.setText(
            "Describa esta imagen en voz alta  ·  "
            "PAGE DOWN  o  ↓  cuando haya terminado"
        )
        self._inner.setCurrentIndex(0)
        QTimer.singleShot(0, self._rescale)

    def _load_caption_phase(self) -> None:
        self._phase = self.PHASE_CAPTION
        trial = self._trials[self._idx]
        n, total = self._idx + 1, len(self._trials)
        self._header.setText(
            f"Práctica — Imagen {n} de {total}  ·  Ejemplos de descripción"
        )
        self._hint.setText("Lea los ejemplos  ·  PAGE DOWN  o  ↓  para continuar")
        captions = trial["captions"]
        self._captions_label.setText(
            "\n\n".join(f"•  {c}" for c in captions)
        )
        self._inner.setCurrentIndex(1)
        QTimer.singleShot(0, self._rescale)

    def _load_done(self) -> None:
        self._phase = self.PHASE_DONE
        self._pixmap = None
        self._header.setText("")
        self._hint.setText("")
        self._inner.setCurrentIndex(2)

    # ── Private — image scaling ────────────────────────────────────────────

    def _rescale(self) -> None:
        if self._pixmap is None or self._pixmap.isNull():
            return
        page = self._inner.currentIndex()
        if page == 0:
            self._scale_into(self._img_full)
        elif page == 1:
            self._scale_into(self._img_split)

    def _scale_into(self, label: QLabel) -> None:
        size = label.size()
        if size.width() < 1 or size.height() < 1:
            return
        label.setPixmap(
            self._pixmap.scaled(  # type: ignore[union-attr]
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
