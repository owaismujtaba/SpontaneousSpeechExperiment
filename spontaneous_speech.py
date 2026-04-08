import sys
from PyQt6.QtWidgets import QApplication

from image_manager import ImageManager
from lsl_manager import LSLManager
from gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Experimento de Habla Espontánea")

    image_manager = ImageManager()
    lsl           = LSLManager()
    window        = MainWindow(image_manager, lsl)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
