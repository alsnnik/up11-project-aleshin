# Задание 2.3. Схема авторизации

USERS_IN_DB = ["admin", "manager1", "manager2", "client01", "client02"] # логины из БД

def check_login(login):
    if login in USERS_IN_DB:
        return "Вход разрешён"
    else:
        return "Ошибка: неверный логин"

print("Проверка авторизации")
print(check_login("admin"))     # Вход разрешён
print(check_login("hacker"))    # Ошибка: неверный логин
print("\n")


# Задание 3.2. Схема расчёта скидки 25%

def calculate_price(price, has_orders):
    if not has_orders:
        return price * 0.75
    else:
        return price

print("Проверка скидки ")
print(calculate_price(3990, False))   # 2992.5 (скидка 25%)
print(calculate_price(3990, True))    # 3990 (без скидки)
print("\n")

# Задание 4.2. Схема оформления заказа

def check_order(size, quantity, stock):
    if size is None:
        return "Ошибка: выберите размер"
    if quantity <= 0:
        return "Ошибка: количество должно быть > 0"
    if quantity > stock:
        return "Ошибка: недостаточно на складе"
    return "Можно добавить в заказ"

print("Проверка оформления заказа")
print(check_order("Стандарт", 2, 10))   # Можно добавить в заказ
print(check_order(None, 2, 10))         # Ошибка: выберите размер
print(check_order("Компакт", 0, 10))    # Ошибка: количество должно быть > 0
print(check_order("XL", 20, 10))        # Ошибка: недостаточно на складе
print("\n")


# Задание 6. Код для своей схемы (Мир интерьера)

def calculate_interior_order(price, category, quantity, stock):
    if quantity > stock:
        return "Ошибка: нет в наличии"
    if category == "Текстиль":
        price = price * 0.9
    return price * quantity

print("Своя схема (Мир интерьера)")
print(calculate_interior_order(790, "Текстиль", 2, 20))  # 1422.0
print(calculate_interior_order(790, "Стулья", 2, 10))    # 1580
print(calculate_interior_order(790, "Декор", 20, 5))     # Ошибка: нет в наличии