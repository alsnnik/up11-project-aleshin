import mysql.connector
from mysql.connector import pooling

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

    # 1. МЕТОД ДЛЯ ПОЛУЧЕНИЯ КАТЕГОРИЙ (Задание 1)
    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            # Получаем уникальные названия категорий
            cursor.execute("SELECT DISTINCT name FROM categories")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # 2. ОБНОВЛЕННЫЙ МЕТОД ДЛЯ ТОВАРОВ (Задание 5)
    def get_products(self, search="", category="Все категории", order="ASC"):
        conn = self.get_connection()
        if conn is None:
            return []
        
        cursor = None
        try:
            cursor = conn.cursor()
            pattern = f"%{search}%"
            
            # Убрали p.composition из SELECT, так как её нет в БД
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
            # Передаем 3 параметра: паттерн поиска, категория, категория
            cursor.execute(query, (pattern, category, category))
            return cursor.fetchall()
            
        except mysql.connector.Error as e:
            print(f"Ошибка при получении товаров: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()