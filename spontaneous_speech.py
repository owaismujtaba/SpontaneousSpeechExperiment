import sys
from PyQt6.QtWidgets import QApplication

from image_manager import ImageManager
from lsl_manager import LSLManager
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Experimento de Habla Espontánea")

    image_manager = ImageManager() # for getting the imgeas and sets
    lsl           = LSLManager() # for sending the data to LSL markers
    window        = MainWindow(image_manager, lsl) # main window of the experiment
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
