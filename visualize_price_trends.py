#!/usr/bin/env python3
"""
Визуализация анализа трендов цен и выявление возможной логики расчета
"""

import matplotlib.pyplot as plt
import numpy as np

# Данные из таблицы
months = ["дек'24", "янв'25", "фев'25", "мар'25", "апр'25", "май'25", 
          "июн'25", "июл'25", "авг'25", "сен'25"]
prices = [51127, 49977, 49707, 49657, 50352, 51480, 53190, 48035, 50184, 50836]
changes = [None, -0.54, -0.10, 1.40, 2.24, 3.32, 3.74, 4.43, 4.47, 1.30]

# Создание графиков
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# График 1: Фактические цены
ax1.plot(months, prices, 'b-o', linewidth=2, markersize=8, label='Фактические цены')
ax1.set_title('Фактические цены по месяцам', fontsize=14, fontweight='bold')
ax1.set_ylabel('Цена (₽/м²)', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Добавление значений на график
for i, (month, price) in enumerate(zip(months, prices)):
    ax1.text(i, price + 200, f'{price:,}', ha='center', va='bottom', fontsize=9)

# График 2: Процентные изменения
changes_plot = [0 if c is None else c for c in changes]
colors = ['green' if c > 0 else 'red' if c < 0 else 'gray' for c in changes_plot]
bars = ax2.bar(months, changes_plot, color=colors, alpha=0.7)
ax2.set_title('Заявленные процентные изменения', fontsize=14, fontweight='bold')
ax2.set_ylabel('Изменение (%)', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')
ax2.axhline(y=0, color='black', linewidth=0.5)

# Добавление значений на график
for bar, change in zip(bars, changes):
    if change is not None:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1 if height > 0 else height - 0.1,
                f'{change:.2f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

# График 3: Сравнение различных интерпретаций
ax3.plot(months, prices, 'b-o', linewidth=2, markersize=8, label='Фактические цены')

# Вариант 1: Расчет от предыдущего месяца
calc_prices_1 = [prices[0]]
for i in range(1, len(prices)):
    if i < len(changes) and changes[i] is not None:
        # Обратный расчет: предыдущий = текущий / (1 + изменение%)
        calc_price = prices[i] / (1 + changes[i] / 100)
        calc_prices_1.append(prices[i])

# Вариант 2: Накопительный расчет от базы
calc_prices_2 = [prices[0]]
base_price = prices[0]
cumulative_change = 1.0
for i in range(1, len(changes)):
    if changes[i] is not None:
        cumulative_change *= (1 + changes[i] / 100)
        calc_prices_2.append(base_price * cumulative_change)

ax3.plot(months[:len(calc_prices_2)], calc_prices_2, 'r--o', linewidth=1.5, markersize=6, 
         label='Накопительный расчет от базы', alpha=0.7)

ax3.set_title('Сравнение фактических и расчетных цен', fontsize=14, fontweight='bold')
ax3.set_ylabel('Цена (₽/м²)', fontsize=12)
ax3.set_xlabel('Месяц', fontsize=12)
ax3.grid(True, alpha=0.3)
ax3.legend()
ax3.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('/workspace/price_trends_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# Анализ возможной логики
print("АНАЛИЗ ВОЗМОЖНОЙ ЛОГИКИ РАСЧЕТА:")
print("=" * 60)

# Проверка гипотезы: проценты показывают изменение к следующему месяцу
print("\nГипотеза 1: Процент показывает, на сколько изменится цена В СЛЕДУЮЩЕМ месяце")
print("(т.е. процент в строке июля показывает изменение июля к августу)")
print("-" * 60)

for i in range(len(prices) - 1):
    if i + 1 < len(changes) and changes[i + 1] is not None:
        expected_next = prices[i] * (1 + changes[i + 1] / 100)
        actual_next = prices[i + 1]
        diff = abs(expected_next - actual_next)
        match = "✓" if diff < 10 else "✗"
        
        print(f"{months[i]} → {months[i+1]}: ")
        print(f"  {prices[i]:,} × (1 + {changes[i+1]}%) = {expected_next:,.0f}")
        print(f"  Факт: {actual_next:,}, Разница: {diff:,.0f} {match}")

# Проверка гипотезы: проценты считаются относительно какого-то другого периода
print("\n\nГипотеза 2: Проценты считаются относительно скользящего среднего")
print("-" * 60)

window_sizes = [3, 6, 12]
for window in window_sizes:
    print(f"\nОкно {window} месяцев:")
    matches = 0
    for i in range(window, len(prices)):
        if i < len(changes) and changes[i] is not None:
            # Расчет скользящего среднего
            ma = np.mean(prices[max(0, i-window):i])
            actual_change = (prices[i] - ma) / ma * 100
            declared_change = changes[i]
            diff = abs(actual_change - declared_change)
            if diff < 0.5:
                matches += 1
            print(f"  {months[i]}: МА={ma:.0f}, Факт.изм={actual_change:.2f}%, Заявл.изм={declared_change}%")
    print(f"  Совпадений: {matches}")

print("\n" + "=" * 60)
print("ВЫВОД: Наиболее вероятная проблема - проценты изменений не соответствуют")
print("изменениям между соседними месяцами. Возможные причины:")
print("1. Ошибка в формуле расчета")
print("2. Проценты относятся к другому базовому периоду")
print("3. Используется сглаживание или корректировка, которая не отражена в таблице")
print("\nГрафики сохранены в price_trends_analysis.png")