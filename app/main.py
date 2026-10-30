import sys
import os
import mysql.connector
from mysql.connector import pooling
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                               QPushButton, QMessageBox, QLineEdit, QComboBox)
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

    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД (категории): {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_products(self, search="", category="Все категории", order="ASC"):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            pattern = f"%{search}%"
            
            query = f"""
                SELECT p.product_id, p.name, c.name AS category, 
                       p.manufacturer, p.price,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                WHERE p.name LIKE %s
                  AND (c.name = %s OR %s = 'Все категории')
                GROUP BY p.product_id
                ORDER BY p.price {order}
            """
            cursor.execute(query, (pattern, category, category))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД (товары): {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

# ФУНКЦИЯ РАСЧЕТА СКИДКИ
def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

# 2. ФУНКЦИЯ СОЗДАНИЯ КАРТОЧКИ ТОВАРА
def create_card(product, index):
    (product_id, name, category, manufacturer, price, total_quantity) = product

    if index == 2:
        total_quantity = 0 # Имитация для голубой подсветки

    card = QWidget()
    card_layout = QHBoxLayout()

    # Изображение
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

    # Блок цен
    old_price = float(price)
    if product_id % 2 == 0:
        new_price = old_price * 0.8
    else:
        new_price = old_price

    discount = calculate_discount(old_price, new_price)

    price_layout = QHBoxLayout()
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px;")
    price_layout.addWidget(old_price_label)

    new_price_label = QLabel(f"{new_price:.2f} ₽")
    new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px;")
    price_layout.addWidget(new_price_label)
    
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    card_layout.addLayout(price_layout)

    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    card.setLayout(card_layout)

    # Подсветка
    if total_quantity == 0:
        card.setStyleSheet("background-color: #ADD8E6; border-radius: 10px; padding: 10px;")
    else:
        card.setStyleSheet("background-color: #D2F6E7; border-radius: 10px; padding: 10px;")

    return card

# 3. ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None): 
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.db = Database()
        
        role_names = {1: "Администратор", 2: "Менеджер", 3: "Клиент", None: "Гость"}
        role_title = role_names.get(self.role_id, "Гость")
        
        self.setWindowTitle(f"Мир интерьера — Каталог ({role_title})")
        self.resize(850, 600)
        self.setWindowIcon(QIcon(r"C:\Users\Sustesion\up11-project-aleshin\resources\Мир интерьера.ico"))

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: Calibri; }
            QPushButton {
                background-color: #70B2AF; color: #FFFFFF; 
                font-family: Calibri; font-weight: bold; 
                border-radius: 5px; padding: 5px 15px;
            }
            QPushButton:hover { background-color: #5c9694; }
            QLineEdit, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
                background-color: #FFFFFF;
                color: #000000;
                font-size: 13px;
            }
            QComboBox::drop-down { border: none; }
        """)

        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- ШАПКА ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_container = QWidget()
        logo_container.setStyleSheet("background-color: #D2F6E7; border-radius: 5px;")
        logo_layout = QHBoxLayout(logo_container)
        
        logo = QLabel()
        logo_path = r"C:\Users\Sustesion\up11-project-aleshin\resources\Мир интерьера.png"
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addWidget(logo)
        
        logo_text = QLabel("Мир интерьера")
        logo_text.setStyleSheet("font-weight: bold; color: #1a5e3a; font-size: 14px;")
        logo_layout.addWidget(logo_text)
        header_layout.addWidget(logo_container)
        
        header_layout.addStretch()

        text = f"ФИО: {self.full_name}" if self.full_name else "ФИО: Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("""
            QPushButton { background-color: #D2F6E7; color: #000000; font-weight: bold; border-radius: 3px; padding: 5px 15px; }
            QPushButton:hover { background-color: #b5e5d3; }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(header_widget)
        
        # Разделительная линия под шапкой
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E0E0E0;")
        main_layout.addWidget(line)

        # --- КНОПКИ РОЛЕЙ (Скрыты по умолчанию) ---
        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Купить товар")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # --- ПАНЕЛЬ ПОИСКА, КАТЕГОРИЙ И СОРТИРОВКИ ---
        filters_layout = QHBoxLayout()
        filters_layout.setContentsMargins(0, 10, 0, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или стилю...")
        self.search_input.textChanged.connect(self.load_products)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        for cat in self.db.get_categories():
            self.filter_combo.addItem(cat[0])
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        
        self.filter_combo.setMinimumWidth(150)
        self.sort_combo.setMinimumWidth(150)
        
        filters_layout.addWidget(self.search_input, 1)
        filters_layout.addWidget(self.filter_combo)
        filters_layout.addWidget(self.sort_combo)
        
        main_layout.addLayout(filters_layout)

        # --- КАТАЛОГ (ПРОКРУТКА) ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFFFFF;")
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        self.setCentralWidget(central)
        self.load_products()

    def load_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        search_text = self.search_input.text()
        category_text = self.filter_combo.currentText()
        sort_order = "ASC" if self.sort_combo.currentText() == "По возрастанию" else "DESC"

        try:
            products = self.db.get_products(search_text, category_text, sort_order)
            if products:
                for index, product in enumerate(products):
                    self.list_layout.addWidget(create_card(product, index))
            else:
                error_label = QLabel("Товары не найдены (БД вернула пустой список)")
                error_label.setAlignment(Qt.AlignCenter)
                self.list_layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(f"ОШИБКА SQL:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            self.list_layout.addWidget(error_label)
            
        self.list_layout.addStretch()

    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:
            self.manager_button.show()
        elif self.role_id == 3:
            self.order_button.show()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())