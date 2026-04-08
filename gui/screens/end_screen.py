from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import TOTAL_SETS


class EndScreen(QWidget):
    """Shown only after all sets have been completed."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        done = QLabel("Fin del experimento")
        done.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        done.setAlignment(Qt.AlignmentFlag.AlignCenter)
        done.setStyleSheet("color: #4a9eff;")
        layout.addWidget(done)

        summary = QLabel(f"Ha completado los {TOTAL_SETS} sets.")
        summary.setFont(QFont("Segoe UI", 18))
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary.setStyleSheet("color: #888;")
        layout.addWidget(summary)

        thanks = QLabel("¡Gracias por su participación!")
        thanks.setFont(QFont("Segoe UI", 20))
        thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks.setStyleSheet("color: #c8c8c8;")
        layout.addWidget(thanks)

        esc = QLabel("Presione  ESC  para salir")
        esc.setFont(QFont("Segoe UI", 13))
        esc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        esc.setStyleSheet("color: #3a3a5a; margin-top: 36px;")
        layout.addWidget(esc)
