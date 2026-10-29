import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database

# Создаем экземпляр базы
db = Database()
conn = db.get_connection()

if conn:
    cursor = conn.cursor()
    # Считаем количество товаров в вашей БД
    cursor.execute("SELECT COUNT(*) FROM products") 
    result = cursor.fetchone()
    print(f"Количество товаров в 'Мире интерьера': {result[0]}")

    cursor.close()
    db.release_connection(conn)
else:
    print("Не удалось подключиться к базе данных. Проверьте настройки.")

db.close_all()