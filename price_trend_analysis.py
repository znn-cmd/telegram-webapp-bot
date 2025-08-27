#!/usr/bin/env python3
"""
Анализ таблицы трендов цен из отчета об оценке недвижимости
"""

# Данные из таблицы
data = [
    {"date": "сен. 2025", "price": 50836, "change": 1.30},
    {"date": "авг. 2025", "price": 50184, "change": 4.47},
    {"date": "июл. 2025", "price": 48035, "change": 4.43},
    {"date": "июн. 2025", "price": 53190, "change": 3.74},
    {"date": "май. 2025", "price": 51480, "change": 3.32},
    {"date": "апр. 2025", "price": 50352, "change": 2.24},
    {"date": "мар. 2025", "price": 49657, "change": 1.40},
    {"date": "фев. 2025", "price": 49707, "change": -0.10},
    {"date": "янв. 2025", "price": 49977, "change": -0.54},
    {"date": "дек. 2024", "price": 51127, "change": -2.25},
]

print("Анализ таблицы трендов цен\n")
print("=" * 80)

# Проверка 1: Прямой расчет (текущий месяц = предыдущий × (1 + изменение%))
print("\n1. Проверка прямого расчета (текущий = предыдущий × (1 + изменение%)):")
print("-" * 80)
for i in range(len(data) - 1):
    current = data[i]
    previous = data[i + 1]
    
    # Расчет текущей цены на основе предыдущей и процента изменения
    calculated_price = previous["price"] * (1 + current["change"] / 100)
    difference = current["price"] - calculated_price
    
    print(f"{current['date']} = {previous['date']} × (1 + {current['change']}%)")
    print(f"  Ожидается: {previous['price']:.0f} × {1 + current['change']/100:.4f} = {calculated_price:.0f}")
    print(f"  Фактически: {current['price']:.0f}")
    print(f"  Разница: {difference:.0f} ({difference/current['price']*100:.2f}%)")
    print()

# Проверка 2: Обратный расчет (предыдущий = текущий / (1 + изменение%))
print("\n2. Проверка обратного расчета (предыдущий = текущий / (1 + изменение%)):")
print("-" * 80)
for i in range(len(data) - 1):
    current = data[i]
    next_month = data[i + 1]
    
    # Расчет предыдущей цены на основе текущей и процента изменения следующего месяца
    calculated_previous = current["price"] / (1 + next_month["change"] / 100)
    difference = next_month["price"] - calculated_previous
    
    print(f"{next_month['date']} = {current['date']} / (1 + {next_month['change']}%)")
    print(f"  Ожидается: {current['price']:.0f} / {1 + next_month['change']/100:.4f} = {calculated_previous:.0f}")
    print(f"  Фактически: {next_month['price']:.0f}")
    print(f"  Разница: {difference:.0f} ({difference/next_month['price']*100:.2f}%)")
    print()

# Проверка 3: Рекурсивный расчет от базового месяца
print("\n3. Рекурсивный расчет от декабря 2024 (базовый месяц):")
print("-" * 80)
base_price = data[-1]["price"]  # Декабрь 2024
print(f"Базовая цена (дек. 2024): {base_price:.0f}")
print()

# Накопленные проценты изменений
accumulated_changes = []
for i in range(len(data) - 2, -1, -1):  # От января 2025 до сентября 2025
    accumulated_changes.append(data[i]["change"])

# Рекурсивный расчет
current_price = base_price
for i, change in enumerate(reversed(accumulated_changes)):
    month_data = data[-(i+2)]
    current_price = current_price * (1 + change / 100)
    actual_price = month_data["price"]
    difference = actual_price - current_price
    
    print(f"{month_data['date']}: {current_price:.0f} (расчет) vs {actual_price:.0f} (факт)")
    print(f"  Изменение: +{change}%, Разница: {difference:.0f} ({difference/actual_price*100:.2f}%)")

# Анализ возможной логики
print("\n" + "=" * 80)
print("ВЫВОДЫ:")
print("=" * 80)
print("\n1. Проценты изменений НЕ соответствуют изменениям между соседними месяцами")
print("2. Возможные причины несоответствия:")
print("   - Проценты могут быть относительно другого базового периода")
print("   - Может использоваться сглаживание или корректировка")
print("   - Возможна ошибка в формуле расчета")
print("\n3. Рекомендации:")
print("   - Проверить исходную формулу расчета в коде")
print("   - Уточнить, относительно какого периода считаются проценты")
print("   - Проверить, нет ли дополнительных корректировок")