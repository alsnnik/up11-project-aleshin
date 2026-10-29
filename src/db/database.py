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
                password="wrong_password"  # <--- ВЕРНИТЕ СЮДА ВАШ ПРАВИЛЬНЫЙ ПАРОЛЬ!
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
            print(f"Ошибка при получении товаров: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()