import mysql.connector

# Функция из вашего main.py (с добавленной защитой от дурака)
def calculate_price_interior(item_id, base_price):
    # Проверка на корректность типов данных
    if not isinstance(item_id, int):
        return "Ошибка: item_id должен быть числом"
    if not isinstance(base_price, (int, float)):
        return "Ошибка: base_price должен быть числом"
    if base_price <= 0:
        return "Ошибка: цена должна быть > 0"

    try:
        connection = mysql.connector.connect(
            database="interior_db",
            user="root",
            password="1234",
            host="127.0.0.1",
            port="3306",
        )
        cursor = connection.cursor()

        # Считаем заказы за последний месяц
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        orders_count = result[0]

        cursor.close()
        connection.close()

        # Если товар не заказывали, даем скидку 25% (базовая * 0.75)
        if orders_count == 0:
            return base_price * 0.75
        else:
            return base_price

    except Exception as e:
        return f"Ошибка БД: {e}"

# --- БЛОК ТЕСТИРОВАНИЯ ---
if __name__ == "__main__":
    print("--- ТЕСТИРОВАНИЕ СИСТЕМЫ СКИДОК МАГАЗИНА ИНТЕРЬЕРА ---")
    print()
    
    print("Тест 1 (Правильный товар с ID=1, проверка скидки):")
    # Подставьте ID товара, который ЕСТЬ в вашей базе и у которого НЕТ заказов
    res1 = calculate_price_interior(1, 1000)
    print(f"Результат расчета цены: {res1} руб.\n")

    print("Тест 2 (Несуществующий ID товара = 99999):")
    res2 = calculate_price_interior(99999, 1000)
    print(f"Результат: {res2} (БД не найдет заказов, поэтому сделает скидку)\n")

    print("Тест 3 (Некорректный тип ID - строка 'abc'):")
    res3 = calculate_price_interior('abc', 1000)
    print(f"Результат: {res3}\n")

    print("Тест 4 (Отрицательная базовая цена):")
    res4 = calculate_price_interior(1, -500)
    print(f"Результат: {res4}\n")

    print("Тест 5 (Пустая базовая цена None):")
    res5 = calculate_price_interior(1, None)
    print(f"Результат: {res5}\n")

    print("--- ТЕСТИРОВАНИЕ ПОЛНОСТЬЮ ЗАВЕРШЕНО ---")