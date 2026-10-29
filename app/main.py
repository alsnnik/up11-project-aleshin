from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мир интерьера — Каталог")
        self.resize(800, 600)
        
        # Пути к вашим файлам (как на скриншоте VS Code)
        self.setWindowIcon(QIcon("resources/Мир интерьера.ico"))

        central = QWidget()
        layout = QVBoxLayout()

        # Логотип
        logo = QLabel()
        logo.setPixmap(QPixmap("resources/Мир интерьера.png"))
        logo.setScaledContents(False)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Заголовок с названием темы
        title = QLabel("Мир интерьера — автоматизация продаж")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Домашнее задание: Версия (если нужно)
        version = QLabel("v1.0")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #000000;
                font-family: Calibri;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #70B2AF;
            }
            QLabel#version {
                font-size: 14px;
                color: #70B2AF;
            }
        """)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()