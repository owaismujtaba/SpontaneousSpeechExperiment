import os

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent

from config import (
    FIXATION_DURATION_MS, TOTAL_SETS,
    TUTORIAL_IMG_PATH, TUTORIAL_ANN_PATH, TUTORIAL_NUM_IMAGES,
)
from annotation_loader import AnnotationLoader
from translator import Translator
from gui.screens.instruction_screen import InstructionScreen
from gui.screens.tutorial_screen import TutorialScreen
from gui.screens.trial_screen import TrialScreen
from gui.screens.between_set_screen import BetweenSetScreen
from gui.screens.end_screen import EndScreen

# ── Application-wide stylesheet ────────────────────────────────────────────
_STYLE = """
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: "Segoe UI";
}

/* Spinner ---------------------------------------------------------------- */
QSpinBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 2px solid #4a9eff;
    border-radius: 6px;
    padding: 4px 6px;
}
QSpinBox:focus {
    border-color: #7bbfff;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #16213e;
    border: none;
    width: 22px;
}
QSpinBox::up-arrow {
    image: none;
    border-left:  5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid #4a9eff;
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    image: none;
    border-left:  5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #4a9eff;
    width: 0; height: 0;
}
"""


class _AppKeyFilter(QObject):
    """
    Application-level event filter so MainWindow intercepts Space,
    Page Down / Down Arrow, and Escape before child widgets consume them.
    """

    _CAPTURED = {Qt.Key.Key_Space, Qt.Key.Key_PageDown, Qt.Key.Key_Down, Qt.Key.Key_Escape}

    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self._mw = main_window

    def eventFilter(self, obj, event) -> bool:  # type: ignore[override]
        if event.type() == QEvent.Type.KeyPress:
            key = Qt.Key(event.key())
            consumed = self._mw.handle_key(key)
            if consumed and key in self._CAPTURED:
                return True
        return False


# ── States ─────────────────────────────────────────────────────────────────
_INSTRUCTION  = "instruction"
_TUTORIAL     = "tutorial"
_TRIAL        = "trial"
_FIXATION     = "fixation"
_BETWEEN_SETS = "between_sets"
_END          = "end"

# ── Stack widget page indices ───────────────────────────────────────────────
_PAGE_INSTRUCTION  = 0
_PAGE_TUTORIAL     = 1
_PAGE_TRIAL        = 2
_PAGE_BETWEEN_SETS = 3
_PAGE_END          = 4


class MainWindow(QMainWindow):
    """
    Top-level window.  Owns the state machine, LSL communication, and timers.
    Screen widgets are pure display components.

    Full flow
    ─────────
    INSTRUCTION  ──[Space]──► TUTORIAL (practice session)
    TUTORIAL     ──[PgDn]──► IMAGE→CAPTION→IMAGE… → DONE slide
    TUTORIAL(done)──[Space]──► TRIAL (set 1)
    TRIAL        ──[PgDn]──► FIXATION
    FIXATION     ──[timer]──► TRIAL  (or BETWEEN_SETS if set done)
    BETWEEN_SETS ──[Space]──► TRIAL (next set)
    after set 20 ──────────► END
    any state    ──[Esc]───► close
    """

    def __init__(self, image_manager, lsl):
        super().__init__()
        self._image_manager = image_manager
        self._lsl = lsl

        self._state          = _INSTRUCTION
        self._current_set    = 0
        self._images: list[str] = []
        self._current_image  = ""
        self._shown          = 0
        self._total          = 0

        self._setup_ui()
        self._setup_timer()
        self._setup_key_filter()

    # ── Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setWindowTitle("Experimento de Habla Espontánea")
        self.setStyleSheet(_STYLE)
        self.showFullScreen()

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._instruction_screen  = InstructionScreen()
        self._tutorial_screen     = TutorialScreen(self._build_tutorial_trials())
        self._trial_screen        = TrialScreen()
        self._between_set_screen  = BetweenSetScreen()
        self._end_screen          = EndScreen()

        self._stack.addWidget(self._instruction_screen)   # _PAGE_INSTRUCTION
        self._stack.addWidget(self._tutorial_screen)       # _PAGE_TUTORIAL
        self._stack.addWidget(self._trial_screen)          # _PAGE_TRIAL
        self._stack.addWidget(self._between_set_screen)    # _PAGE_BETWEEN_SETS
        self._stack.addWidget(self._end_screen)            # _PAGE_END

    def _build_tutorial_trials(self):
        """Load the first TUTORIAL_NUM_IMAGES images + captions from train2017 (translated to Spanish)."""
        translator = Translator(source="en", target="es")
        loader = AnnotationLoader(TUTORIAL_ANN_PATH, translator=translator)
        ann_files = sorted(os.listdir(TUTORIAL_ANN_PATH))[:TUTORIAL_NUM_IMAGES]
        trials = []
        for ann_file in ann_files:
            img_name = ann_file.replace(".json", "")
            img_path = TUTORIAL_IMG_PATH / img_name
            captions = loader.captions(img_name)
            if img_path.exists() and captions:
                trials.append({"image": img_path, "captions": captions})
        return trials

    def _setup_timer(self) -> None:
        self._fixation_timer = QTimer(self)
        self._fixation_timer.setSingleShot(True)
        self._fixation_timer.timeout.connect(self._advance_trial)

    def _setup_key_filter(self) -> None:
        self._key_filter = _AppKeyFilter(self)
        QApplication.instance().installEventFilter(self._key_filter)  # type: ignore[union-attr]

    # ── Key dispatcher ─────────────────────────────────────────────────────

    def handle_key(self, key: Qt.Key) -> bool:
        """Return True if the key was consumed."""
        if key == Qt.Key.Key_Escape:
            self._lsl.push("experimentEnded;ESC pressed")
            self.close()
            return True

        if key == Qt.Key.Key_Space:
            if self._state == _INSTRUCTION:
                self._start_tutorial()
                return True
            if self._state == _TUTORIAL and \
                    self._tutorial_screen.phase == TutorialScreen.PHASE_DONE:
                self._start_set(1)
                return True
            if self._state == _BETWEEN_SETS:
                self._start_set(self._current_set + 1)
                return True

        if key in (Qt.Key.Key_PageDown, Qt.Key.Key_Down):
            if self._state == _TRIAL:
                self._show_fixation()
                return True
            if self._state == _TUTORIAL and \
                    self._tutorial_screen.phase != TutorialScreen.PHASE_DONE:
                self._advance_tutorial()
                return True

        return False

    # ── Tutorial flow ───────────────────────────────────────────────────────

    def _start_tutorial(self) -> None:
        self._state = _TUTORIAL
        self._lsl.push("tutorialStarted")
        self._stack.setCurrentIndex(_PAGE_TUTORIAL)
        self._tutorial_screen.start()
        # Send marker for the first image
        trial = self._tutorial_screen._trials[0]
        self._lsl.push(f"tutorialImage_{trial['image'].name}_{self._lsl.clock():.6f}")

    def _advance_tutorial(self) -> None:
        phase_before = self._tutorial_screen.phase
        self._tutorial_screen.advance()
        phase_after = self._tutorial_screen.phase

        img_name = self._tutorial_screen._trials[
            min(self._tutorial_screen._idx, len(self._tutorial_screen._trials) - 1)
        ]["image"].name

        if phase_after == TutorialScreen.PHASE_CAPTION:
            self._lsl.push(f"tutorialCaption_{img_name}_{self._lsl.clock():.6f}")
        elif phase_after == TutorialScreen.PHASE_IMAGE:
            self._lsl.push(f"tutorialImage_{img_name}_{self._lsl.clock():.6f}")
        elif phase_after == TutorialScreen.PHASE_DONE:
            self._lsl.push("tutorialEnded")

    # ── Experiment flow ────────────────────────────────────────────────────

    def _start_set(self, set_number: int) -> None:
        self._current_set = set_number
        self._images = self._image_manager.get_set(set_number)
        self._total  = len(self._images)
        self._shown  = 0

        self._trial_screen.init_set(set_number, self._total)
        self._lsl.push(f"setStarted;{set_number}")
        self._stack.setCurrentIndex(_PAGE_TRIAL)
        self._advance_trial()

    def _advance_trial(self) -> None:
        if not self._images:
            self._finish_set()
            return

        self._current_image = self._images.pop(0)
        self._shown += 1
        path = self._image_manager.get_image_path(self._current_image)
        self._trial_screen.show_image(path, self._shown)
        self._lsl.push(self._lsl.marker("start", self._current_image))
        self._state = _TRIAL

    def _show_fixation(self) -> None:
        self._state = _FIXATION
        self._lsl.push(self._lsl.marker("end", self._current_image))
        self._trial_screen.show_fixation()
        self._fixation_timer.start(FIXATION_DURATION_MS)

    def _finish_set(self) -> None:
        """Called when all trials in the current set are done."""
        self._lsl.push(f"setEnded;{self._current_set}")

        if self._current_set >= TOTAL_SETS:
            self._state = _END
            self._lsl.push("experimentEnded")
            self._stack.setCurrentIndex(_PAGE_END)
        else:
            self._state = _BETWEEN_SETS
            self._between_set_screen.update(self._current_set)
            self._stack.setCurrentIndex(_PAGE_BETWEEN_SETS)
