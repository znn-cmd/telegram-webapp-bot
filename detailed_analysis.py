#!/usr/bin/env python3
"""
Детальный анализ возможных вариантов расчета цен в таблице трендов
"""

# Данные из таблицы
data = [
    {"date": "дек. 2024", "price": 51127, "change": -2.25},
    {"date": "янв. 2025", "price": 49977, "change": -0.54},
    {"date": "фев. 2025", "price": 49707, "change": -0.10},
    {"date": "мар. 2025", "price": 49657, "change": 1.40},
    {"date": "апр. 2025", "price": 50352, "change": 2.24},
    {"date": "май. 2025", "price": 51480, "change": 3.32},
    {"date": "июн. 2025", "price": 53190, "change": 3.74},
    {"date": "июл. 2025", "price": 48035, "change": 4.43},
    {"date": "авг. 2025", "price": 50184, "change": 4.47},
    {"date": "сен. 2025", "price": 50836, "change": 1.30},
]

print("ДЕТАЛЬНЫЙ АНАЛИЗ ВОЗМОЖНЫХ ЛОГИК РАСЧЕТА")
print("=" * 80)

# Гипотеза 1: Процент в строке показывает изменение К следующему месяцу
print("\n1. ГИПОТЕЗА: Процент показывает изменение К СЛЕДУЮЩЕМУ месяцу")
print("   (процент в строке N относится к изменению от месяца N к месяцу N+1)")
print("-" * 80)

matches = 0
for i in range(len(data) - 1):
    current = data[i]
    next_month = data[i + 1]
    
    # Расчет ожидаемой цены следующего месяца
    expected_next = current["price"] * (1 + next_month["change"] / 100)
    diff = abs(expected_next - next_month["price"])
    is_match = diff < 10
    
    if is_match:
        matches += 1
        
    print(f"{current['date']} → {next_month['date']}:")
    print(f"  {current['price']} × (1 + {next_month['change']}%) = {expected_next:.0f}")
    print(f"  Фактически: {next_month['price']}, Разница: {diff:.0f} {'✓' if is_match else '✗'}")

print(f"\nСовпадений: {matches} из {len(data)-1}")

# Гипотеза 2: Обратная логика - процент показывает изменение ОТ предыдущего
print("\n\n2. ГИПОТЕЗА: Процент показывает изменение ОТ ПРЕДЫДУЩЕГО месяца")
print("   (цена месяца N = цена месяца N-1 × (1 + процент в строке N))")
print("-" * 80)

# Проверка с начала
print("Проверка с начала (от декабря 2024):")
current_price = data[0]["price"]
for i in range(1, len(data)):
    month = data[i]
    expected = current_price * (1 + month["change"] / 100)
    actual = month["price"]
    diff = abs(expected - actual)
    
    print(f"{data[i-1]['date']} → {month['date']}:")
    print(f"  {current_price:.0f} × (1 + {month['change']}%) = {expected:.0f}")
    print(f"  Фактически: {actual}, Разница: {diff:.0f}")
    
    current_price = actual  # Используем фактическую цену для следующего расчета

# Гипотеза 3: Особая логика для июля (аномальное значение)
print("\n\n3. АНАЛИЗ АНОМАЛИИ В ИЮЛЕ 2025")
print("-" * 80)

july_idx = 7
june = data[july_idx - 1]
july = data[july_idx]
august = data[july_idx + 1]

print(f"Июнь: {june['price']} ({june['change']}%)")
print(f"Июль: {july['price']} ({july['change']}%)")  
print(f"Август: {august['price']} ({august['change']}%)")

# Проверка различных вариантов
print("\nВозможные варианты расчета июля:")

# Вариант 1: От июня с процентом июля
calc1 = june["price"] * (1 + july["change"] / 100)
print(f"1) Июнь × (1 + 4.43%) = {june['price']} × 1.0443 = {calc1:.0f} (факт: {july['price']})")

# Вариант 2: От августа обратно с процентом августа
calc2 = august["price"] / (1 + august["change"] / 100)
print(f"2) Август / (1 + 4.47%) = {august['price']} / 1.0447 = {calc2:.0f} (факт: {july['price']})")

# Вариант 3: Проверка, может быть это опечатка и должно быть отрицательное значение
calc3 = june["price"] * (1 - july["change"] / 100)
print(f"3) Июнь × (1 - 4.43%) = {june['price']} × 0.9557 = {calc3:.0f} (факт: {july['price']})")

# Вариант 4: Проверка правильности расчета процента
actual_change = (july["price"] - june["price"]) / june["price"] * 100
print(f"\n4) Фактическое изменение июнь→июль: ({july['price']} - {june['price']}) / {june['price']} × 100 = {actual_change:.2f}%")
print(f"   Заявленное изменение: {july['change']}%")

# Итоговый анализ
print("\n" + "=" * 80)
print("ИТОГОВЫЙ АНАЛИЗ:")
print("=" * 80)
print("\n1. Основная проблема в данных - июль 2025:")
print(f"   - Цена резко падает с {june['price']} до {july['price']} (-9.67%)")
print(f"   - Но процент изменения указан как +{july['change']}%")
print("\n2. Для остальных месяцев логика более последовательна")
print("\n3. Возможные объяснения:")
print("   a) Ошибка в данных июля (неправильная цена или процент)")
print("   b) Особая корректировка в июле (сезонность, изменение методологии)")
print("   c) Проценты рассчитываются по другой формуле")
print("\n4. Рекомендации:")
print("   - Проверить исходный код расчета процентов")
print("   - Уточнить, есть ли особая обработка для июля")
print("   - Проверить исходные данные на наличие опечаток")