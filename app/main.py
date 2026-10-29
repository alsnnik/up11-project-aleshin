import sys
import mysql.connector
from mysql.connector import pooling
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


# КЛАСС DATABASE

class Database:
    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="interior_pool",
                pool_size=5,
                host="localhost",
                port=3306,
                database="interior_db",
                user="root",
                password="1234"  # <--- ВАШ ПАРОЛЬ (верните правильный!)
            )
            print("Пул соединений MySQL успешно создан!")
        except mysql.connector.Error as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool is None:
            return None
        return self.connection_pool.get_connection()

    def release_connection(self, conn):
        if self.connection_pool and conn:
            conn.close()

    def close_all(self):
        pass

    def get_products(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# ГЛАВНОЕ ОКНО

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мир интерьера — Каталог")
        self.resize(800, 600)
        
        self.db = Database() 

        self.setWindowIcon(QIcon("../resources/Мир интерьера.ico"))

        central = QWidget()
        layout = QVBoxLayout()

        logo = QLabel()
        logo.setPixmap(QPixmap("../resources/Мир интерьера.png"))
        logo.setScaledContents(False)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Мир интерьера — автоматизация продаж")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: Calibri; }
            QLabel { color: #000000; font-family: Calibri; }
            QLabel#title { font-size: 24px; font-weight: bold; color: #70B2AF; }
        """)

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

# ЗАПУСК И ПРОВЕРКА

if __name__ == "__main__":
    # 1. Сначала выполним проверку для Задания 6 (выведем товары в консоль)
    print("--- ТЕСТ ДЛЯ ЗАДАНИЯ 6 ---")
    test_db = Database()
    products = test_db.get_products()
    print(f"Получено товаров для интерьера: {len(products)}")
    for row in products[:3]:
        print(row)
    print("--------------------------\n")

    # 2. Затем запускаем графическое окно
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())