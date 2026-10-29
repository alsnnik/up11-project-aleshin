import mysql.connector
import sys
import os

# Настраиваем путь к папке, где лежит discount.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'logic')))

import mysql.connector
from discount import calculate_price

def test_all_products():
    try:
        connection = mysql.connector.connect(
            database="interior_db",
            user="root",
            password="1234",  # Твой пароль
            host="127.0.0.1",
            port="3306",
        )
        cursor = connection.cursor()

        # Запрос с ценой из таблицы остатков
        query = "SELECT p.product_id, p.name, s.price FROM products p JOIN stock_items s ON p.product_id = s.product_id WHERE s.size_id = 1;"
        cursor.execute(query)
        products = cursor.fetchall()

        cursor.close()
        connection.close()

        print(f"--- НАЧАЛО ПРОВЕРКИ (Всего товаров: {len(products)}) ---\n")

        for row in products:
            product_id = row[0]
            name = row[1]
            price = row[2]

            final_price = calculate_price(product_id, price)

            print(f"ID: {product_id} | {name} | Стартовая цена: {price} руб. -> Итоговая: {final_price} руб.")

        print("\n--- ПРОВЕРКА ЗАВЕРШЕНА ---")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_all_products()