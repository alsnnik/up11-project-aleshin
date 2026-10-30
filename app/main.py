import sys
import os
import mysql.connector
from mysql.connector import pooling
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                               QPushButton, QMessageBox, QLineEdit, QComboBox,
                               QDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from login_window import LoginWindow

# Константа для расчета скидки
DISCOUNT_RATE = 0.75

def calculate_price_interior(item_id, base_price):
    try:
        connection = mysql.connector.connect(
            database="interior_db",
            user="root",
            password="1234",
            host="127.0.0.1",
            port="3306",
        )
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= '2026-01-01';
        """
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        orders_count = result[0]
        cursor.close()
        connection.close()

        if orders_count == 0:
            return base_price * DISCOUNT_RATE
        else:
            return base_price
    except Exception as e:
        print(f"Ошибка БД (расчет скидки): {e}")
        return base_price

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
                password="1234"
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
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
                WHERE (p.name LIKE %s OR c.name LIKE %s)
                  AND (c.name = %s OR %s = 'Все категории')
                GROUP BY p.product_id
                ORDER BY p.price {order}
            """
            cursor.execute(query, (pattern, pattern, category, category))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД (товары): {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_orders(self):
        """Получает список всех заказов для менеджера"""
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT o.order_id, o.order_date, 
                       CONCAT(u.last_name, ' ', u.first_name) AS client_name,
                       COALESCE(SUM(oi.quantity * p.price), 0) AS total_sum
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                LEFT JOIN products p ON oi.product_id = p.product_id
                GROUP BY o.order_id
                ORDER BY o.order_date DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД (заказы): {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_users(self):
        """Получает список всех пользователей для админа"""
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT u.user_id, u.last_name, u.first_name, u.login, r.name AS role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
            """
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД (пользователи): {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# КЛАСС ДЛЯ КЛИКАБЕЛЬНОЙ КАРТОЧКИ
class ClickableCard(QWidget):
    def __init__(self, product_data, click_callback):
        super().__init__()
        self.product_data = product_data
        self.click_callback = click_callback
        self.setCursor(Qt.PointingHandCursor) # Курсор в виде руки

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_callback(self.product_data)

def create_card(product, index, main_window):
    (product_id, name, category, manufacturer, price, total_quantity) = product

    if not manufacturer:
        manufacturer = "Без бренда"

    if index == 2:
        total_quantity = 0 

    # Создаем кликабельную карточку
    card = ClickableCard(product, main_window.show_product_info)
    card_layout = QHBoxLayout()

    # Картинка
    image_label = QLabel()
    img_name = f"IMG_13_{product_id:03d}.png"
    img_path = os.path.join(r"C:\Users\Sustesion\up11-project-aleshin\resources", img_name)
    
    if os.path.exists(img_path):
        pixmap = QPixmap(img_path)
    else:
        pixmap = QPixmap(r"C:\Users\Sustesion\up11-project-aleshin\resources\picture.png")
       
    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    # Текст
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

    # Цены
    old_price = float(price)
    new_price = calculate_price_interior(product_id, old_price)
    
    discount_percent = 0
    if old_price > 0:
        discount_percent = (old_price - new_price) / old_price * 100

    price_layout = QHBoxLayout()
    
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px;")
    price_layout.addWidget(old_price_label)

    new_price_label = QLabel(f"{new_price:.2f} ₽")
    
    if discount_percent > 15:
        new_price_label.setStyleSheet("color: #2E8B57; font-weight: bold; font-size: 18px;")
    else:
        new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px;")
        
    price_layout.addWidget(new_price_label)
    
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    card_layout.addLayout(price_layout)

    if discount_percent > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    card.setLayout(card_layout)

    if total_quantity == 0:
        card.setStyleSheet("background-color: #ADD8E6; border-radius: 10px; padding: 10px;")
    else:
        card.setStyleSheet("background-color: #D2F6E7; border-radius: 10px; padding: 10px;")

    return card

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
        
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E0E0E0;")
        main_layout.addWidget(line)

        # --- КНОПКИ ---
        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Купить товар")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        self.order_button.clicked.connect(self.buy_product)
        self.manager_button.clicked.connect(self.show_orders)
        self.admin_button.clicked.connect(self.show_admin_panel) # Подключаем Админ-панель
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # --- ФИЛЬТРЫ ---
        filters_layout = QHBoxLayout()
        filters_layout.setContentsMargins(0, 10, 0, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию, стилю или категории...")
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

        # --- КАТАЛОГ ---
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
                    self.list_layout.addWidget(create_card(product, index, self))
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

    # --- ФУНКЦИИ КНОПОК ---

    def show_product_info(self, product_data):
        (p_id, name, category, manufacturer, price, total_quantity) = product_data
        new_price = calculate_price_interior(p_id, float(price))
        
        QMessageBox.information(
            self, 
            "Информация о товаре", 
            f"Товар: {name}\n"
            f"Производитель: {manufacturer}\n"
            f"Категория: {category}\n"
            f"В наличии: {int(total_quantity)} шт.\n"
            f"Цена: {new_price:.2f} ₽"
        )

    def buy_product(self):
        QMessageBox.information(
            self, 
            "Оформление заказа", 
            "Товар успешно добавлен в корзину! Спасибо за покупку в магазине «Мир интерьера»."
        )

    def show_orders(self):
        orders = self.db.get_orders()
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление заказами")
        dialog.resize(600, 400)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID заказа", "Дата", "Клиент", "Сумма (₽)"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            o_id, o_date, client, total = order
            table.setItem(row, 0, QTableWidgetItem(str(o_id)))
            table.setItem(row, 1, QTableWidgetItem(str(o_date)))
            table.setItem(row, 2, QTableWidgetItem(str(client)))
            table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}"))
            
        layout.addWidget(table)
        dialog.exec()

    def show_admin_panel(self):
        """Открывает панель администратора со списком пользователей"""
        users = self.db.get_users()
        dialog = QDialog(self)
        dialog.setWindowTitle("Админ-панель: Пользователи")
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Логин", "Роль"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table.setRowCount(len(users))
        for row, user in enumerate(users):
            u_id, last_name, first_name, login, role = user
            table.setItem(row, 0, QTableWidgetItem(str(u_id)))
            table.setItem(row, 1, QTableWidgetItem(str(last_name)))
            table.setItem(row, 2, QTableWidgetItem(str(first_name)))
            table.setItem(row, 3, QTableWidgetItem(str(login)))
            table.setItem(row, 4, QTableWidgetItem(str(role)))
            
        layout.addWidget(table)
        dialog.exec()

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