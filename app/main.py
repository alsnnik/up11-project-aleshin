import sys
import os
import mysql.connector
from mysql.connector import pooling
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QScrollArea)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

# 1. КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
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
                password="1234"  # <--- ВАШ ПАРОЛЬ
            )
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
            cursor.execute("""
                SELECT p.product_id, p.name, c.name AS category, 
                       p.manufacturer, p.price,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                GROUP BY p.product_id
            """)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

# 2. ФУНКЦИЯ СОЗДАНИЯ КАРТОЧКИ ТОВАРА
# Добавляем параметр index (позиция карточки в списке)
def create_card(product, index):
    (product_id, name, category, manufacturer, price, total_quantity) = product

    card = QWidget()
    card.setStyleSheet("background-color: #D2F6E7; border-radius: 10px; padding: 10px;")
    card_layout = QHBoxLayout()

    # --- БЛОК ИЗОБРАЖЕНИЯ ---
    image_label = QLabel()
    pixmap = None
    
    # ЛОГИКА: Если это первый товар (index == 0), пытаемся загрузить картинку
    if index == 0:
        image_path = "IMG_13_001.png" 
        full_path = os.path.join(r"C:\Users\Sustesion\up11-project-aleshin\resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)

    # Если картинка не загрузилась (или это НЕ первый товар) — ставим заглушку
    if pixmap is None or pixmap.isNull():
       pixmap = QPixmap(r"C:\Users\Sustesion\up11-project-aleshin\resources\picture.png")

    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    # --- ТЕКСТОВАЯ ЧАСТЬ ---
    text_layout = QVBoxLayout()
    
    name_label = QLabel(f"{manufacturer} | {name}")
    name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
    
    cat_label = QLabel(f"Категория: {category}")
    cat_label.setStyleSheet("color: #000000; font-size: 13px;")
    
    qty_label = QLabel(f"Количество: {int(total_quantity)}")
    qty_label.setStyleSheet("color: #000000; font-size: 13px;")
    
    text_layout.addWidget(name_label)
    text_layout.addWidget(cat_label)
    text_layout.addWidget(qty_label)
    card_layout.addLayout(text_layout)

    # --- ЦЕНА ---
    price_label = QLabel(f"{price} ₽")
    price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
    price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    return card

# 3. ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мир интерьера — Каталог")
        self.resize(800, 600)
        
        self.db = Database() 
        self.setWindowIcon(QIcon(r"C:\Users\Sustesion\up11-project-aleshin\resources\Мир интерьера.ico"))

        container = QWidget()
        list_layout = QVBoxLayout()

        self.products = self.db.get_products()
        
        if self.products:
            # ИСПОЛЬЗУЕМ enumerate, чтобы получить индекс (номер) каждого товара
            for index, product in enumerate(self.products):
                # Передаем индекс в функцию create_card
                list_layout.addWidget(create_card(product, index))
        else:
            error_label = QLabel("Товары не найдены или нет подключения к БД")
            error_label.setAlignment(Qt.AlignCenter)
            list_layout.addWidget(error_label)
            
        list_layout.addStretch()
        container.setLayout(list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: Calibri; }
            QScrollArea { border: none; }
        """)

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

# ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())