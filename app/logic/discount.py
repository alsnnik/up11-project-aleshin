import mysql.connector

def calculate_price_interior(item_id, base_price):
    try:
        connection = mysql.connector.connect(
            database="interior_db",
            user="root",
            password="1234",  # Твой пароль
            host="127.0.0.1",
            port="3306",
        )
        cursor = connection.cursor()

        # Считаем, сколько раз этот товар заказывали за последние 3 месяца
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

        # Если товар не заказывали, даем скидку 15% для стимуляции продаж
        if orders_count == 0:
            discounted_price = base_price * 0.85
            print(f"[ID {item_id}] Заказов: 0. Применена скидка 15%.")
            return discounted_price
        else:
            print(f"[ID {item_id}] Заказов: {orders_count}. Цена без изменений.")
            return base_price

    except Exception as e:
        print(f"Ошибка БД: {e}")
        return base_price

# 5. Тестовый запуск
if __name__ == "__main__":
    print("--- ТЕСТИРОВАНИЕ СИСТЕМЫ СКИДОК МАГАЗИНА ИНТЕРЬЕРА ---")
    
    # Тестируем товар с заказами (ID: 1, Стул Сканди, 3990 руб.)
    price_1 = calculate_price_interior(1, 3990.00)
    print(f"Итоговая стоимость товара №1: {price_1} руб.\n")

    # Тестируем товар без заказов (например, ID: 31, Ваза Ветвь, 2570 руб.)
    price_31 = calculate_price_interior(31, 2570.00)
    print(f"Итоговая стоимость товара №31: {price_31} руб.")