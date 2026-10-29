import os

# Проверяем наличие заглушки и файлов товаров
files = [
    r"C:\Users\Sustesion\up11-project-aleshin\resources\picture.png",
    r"C:\Users\Sustesion\up11-project-aleshin\resources\Мир интерьера.png",
    r"C:\Users\Sustesion\up11-project-aleshin\resources\chair_1.png"  # Пример имени файла товара
]

for path in files:
    if os.path.exists(path):
        print(f"{path}: файл есть")
    else:
        print(f"{path}: файла нет")