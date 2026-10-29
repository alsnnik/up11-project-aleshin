import sys
import os
import mysql.connector
from mysql.connector import pooling
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from login_window import LoginWindow

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
def create_card(product, index):
    (product_id, name, category, manufacturer, price, total_quantity) = product

    card = QWidget()
    card.setStyleSheet("background-color: #D2F6E7; border-radius: 10px; padding: 10px;")
    card_layout = QHBoxLayout()

    # Блок изображения
    image_label = QLabel()
    pixmap = None
    
    if index == 0:
        image_path = "IMG_13_001.png" 
        full_path = os.path.join(r"C:\Users\Sustesion\up11-project-aleshin\resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)

    if pixmap is None or pixmap.isNull():
       pixmap = QPixmap(r"C:\Users\Sustesion\up11-project-aleshin\resources\picture.png")

    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    # Текстовая часть
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

    # Цена
    price_label = QLabel(f"{price} ₽")
    price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
    price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    return card

# 3. ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None): 
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.db = Database()
        
        self.setWindowTitle("Мир интерьера — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon(r"C:\Users\Sustesion\up11-project-aleshin\resources\Мир интерьера.ico"))

        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # --- ШАПКА С ЛОГОТИПОМ, ФИО И КНОПКОЙ ВЫХОД ---
        header_layout = QHBoxLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap(r"C:\Users\Sustesion\up11-project-aleshin\resources\picture.png").scaled(
            60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(logo)

        header_layout.addStretch()

        # ФИО (Белое, крупное и жирное)
        text = f"ФИО: {self.full_name}" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #FFFFFF;")
        header_layout.addWidget(self.name_label)

        # Кнопка Выход (Красивая, с белым фоном)
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; 
                color: #000000; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #D2F6E7;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addLayout(header_layout)

        # --- КНОПКИ РОЛЕЙ (Бирюзовые, чтобы было видно) ---
        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Купить товар")
        self.order_button.setStyleSheet("background-color: #70B2AF; color: #FFFFFF; font-weight: bold; border-radius: 5px; padding: 5px 15px;")
        
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setStyleSheet("background-color: #70B2AF; color: #FFFFFF; font-weight: bold; border-radius: 5px; padding: 5px 15px;")
        
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setStyleSheet("background-color: #70B2AF; color: #FFFFFF; font-weight: bold; border-radius: 5px; padding: 5px 15px;")
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # --- КАТАЛОГ ---
        container = QWidget()
        list_layout = QVBoxLayout()
        self.products = self.db.get_products()
        
        if self.products:
            for index, product in enumerate(self.products):
                list_layout.addWidget(create_card(product, index))
        else:
            error_label = QLabel("Товары не найдены")
            error_label.setAlignment(Qt.AlignCenter)
            list_layout.addWidget(error_label)
            
        list_layout.addStretch()
        container.setLayout(list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def setup_role_interface(self):
        # По умолчанию скрываем всё (Гость)
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()

        # Показываем в зависимости от роли
        if self.role_id == 1:        # Администратор
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:      # Менеджер
            self.manager_button.show()
        elif self.role_id == 3:      # Клиент
            self.order_button.show()

    # --- МЕТОД ВЫХОДА ---
    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.login_window = LoginWindow(Database())
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

# ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())