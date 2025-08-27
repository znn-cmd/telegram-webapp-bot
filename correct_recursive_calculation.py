#!/usr/bin/env python3
"""
Правильная рекурсивная реализация расчета цен на основе процентных изменений
"""

def calculate_price_forward(base_price, change_percent):
    """Расчет цены вперед: новая_цена = старая_цена × (1 + изменение%)"""
    return base_price * (1 + change_percent / 100)

def calculate_price_backward(current_price, change_percent):
    """Расчет цены назад: старая_цена = новая_цена / (1 + изменение%)"""
    return current_price / (1 + change_percent / 100)

def recursive_price_calculation(data, base_index=0):
    """
    Рекурсивный расчет цен от базового месяца
    
    Args:
        data: список словарей с ценами и процентами изменений
        base_index: индекс базового месяца (по умолчанию 0)
    
    Returns:
        список расчетных цен
    """
    calculated_prices = [None] * len(data)
    calculated_prices[base_index] = data[base_index]["price"]
    
    # Расчет вперед от базового месяца
    for i in range(base_index + 1, len(data)):
        if data[i]["change"] is not None:
            # Вариант 1: процент в текущей строке показывает изменение от предыдущего
            calculated_prices[i] = calculate_price_forward(
                calculated_prices[i-1], 
                data[i]["change"]
            )
    
    # Расчет назад от базового месяца
    for i in range(base_index - 1, -1, -1):
        if i + 1 < len(data) and data[i + 1]["change"] is not None:
            # Вариант 1: процент в следующей строке показывает изменение от текущего
            calculated_prices[i] = calculate_price_backward(
                calculated_prices[i + 1], 
                data[i + 1]["change"]
            )
    
    return calculated_prices

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

print("ПРАВИЛЬНАЯ РЕКУРСИВНАЯ РЕАЛИЗАЦИЯ РАСЧЕТА ЦЕН")
print("=" * 80)

# Тест 1: Базовый месяц - декабрь 2024
print("\n1. Расчет от декабря 2024 (базовый месяц)")
print("-" * 80)

calculated = recursive_price_calculation(data, base_index=0)

print(f"{'Месяц':<15} {'Факт.цена':>10} {'Расч.цена':>10} {'Разница':>10} {'Процент':>8}")
print("-" * 80)
for i, (actual, calc) in enumerate(zip(data, calculated)):
    if calc is not None:
        diff = actual["price"] - calc
        percent_diff = (diff / actual["price"]) * 100
        print(f"{actual['date']:<15} {actual['price']:>10,} {calc:>10,.0f} {diff:>10,.0f} {percent_diff:>7.1f}%")

# Проверка обратной совместимости
print("\n\n2. Проверка обратной совместимости расчетов")
print("-" * 80)
print("Если логика правильная, то:")
print("- Расчет вперед: цена[i] = цена[i-1] × (1 + процент[i]/100)")
print("- Расчет назад: цена[i-1] = цена[i] / (1 + процент[i]/100)")
print("-" * 80)

for i in range(1, len(data)):
    prev = data[i-1]
    curr = data[i]
    
    # Проверка прямого расчета
    forward_calc = calculate_price_forward(prev["price"], curr["change"])
    forward_diff = abs(forward_calc - curr["price"])
    
    # Проверка обратного расчета
    backward_calc = calculate_price_backward(curr["price"], curr["change"])
    backward_diff = abs(backward_calc - prev["price"])
    
    print(f"\n{prev['date']} → {curr['date']} (изменение: {curr['change']}%):")
    print(f"  Прямой: {prev['price']:,} × {1 + curr['change']/100:.4f} = {forward_calc:,.0f} (факт: {curr['price']:,}, разн: {forward_diff:,.0f})")
    print(f"  Обратный: {curr['price']:,} / {1 + curr['change']/100:.4f} = {backward_calc:,.0f} (факт: {prev['price']:,}, разн: {backward_diff:,.0f})")

# Исправленная логика для таблицы
print("\n\n3. ИСПРАВЛЕННАЯ ЛОГИКА ДЛЯ ТАБЛИЦЫ")
print("=" * 80)
print("\nВЫВОД: Основная проблема в том, что проценты в таблице НЕ соответствуют")
print("фактическим изменениям между месяцами. Особенно это заметно в июле 2025.")
print("\nДля корректной рекурсивной логики нужно:")
print("1. Пересчитать проценты изменений на основе фактических цен")
print("2. Или исправить цены на основе заданных процентов")
print("\nПример корректных процентов изменений:")
print("-" * 80)

print(f"{'Месяц':<15} {'Цена':>10} {'Корректный %':>15} {'Заявленный %':>15}")
print("-" * 80)
for i in range(1, len(data)):
    prev = data[i-1]["price"]
    curr = data[i]["price"]
    actual_change = ((curr - prev) / prev) * 100
    declared_change = data[i]["change"]
    
    print(f"{data[i]['date']:<15} {curr:>10,} {actual_change:>14.2f}% {declared_change:>14.2f}%")

print("\n" + "=" * 80)
print("РЕКОМЕНДАЦИИ ДЛЯ ИСПРАВЛЕНИЯ:")
print("1. Проверить исходный код, генерирующий эту таблицу")
print("2. Убедиться, что проценты рассчитываются правильно")
print("3. Особое внимание уделить июлю 2025 - там явная ошибка")
print("4. Возможно, используется другая база для расчета процентов")