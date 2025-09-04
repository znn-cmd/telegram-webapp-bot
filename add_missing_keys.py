#!/usr/bin/env python3
"""
Скрипт для добавления недостающих ключей переводов в i18n-manager.js
"""

import re

def add_missing_keys():
    """Добавляет недостающие ключи переводов"""
    
    # Читаем файл
    with open('i18n-manager.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем недостающие ключи для всех языков
    missing_keys = {
        'ru': {
            'reports': {
                'liquidity': 'Ликвидность'
            }
        },
        'en': {
            'reports': {
                'liquidity': 'Liquidity'
            }
        },
        'de': {
            'reports': {
                'liquidity': 'Liquidität'
            }
        },
        'fr': {
            'reports': {
                'liquidity': 'Liquidité'
            }
        },
        'tr': {
            'reports': {
                'liquidity': 'Likidite'
            }
        }
    }
    
    # Добавляем ключи для каждого языка
    for lang, categories in missing_keys.items():
        for category, keys in categories.items():
            for key, value in keys.items():
                # Находим секцию для языка и категории
                pattern = rf"'{lang}': \{{[^}}]*'{category}': \{{[^}}]*\}}"
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    # Добавляем ключ в конец секции категории
                    category_pattern = rf"'{category}': \{{([^}}]*)\}}"
                    category_match = re.search(category_pattern, match.group(0))
                    
                    if category_match:
                        category_content = category_match.group(1)
                        if f"'{key}':" not in category_content:
                            # Добавляем ключ в конец секции
                            new_category_content = category_content.rstrip() + f", '{key}': '{value}'"
                            new_content = content.replace(category_match.group(0), f"'{category}': {{{new_category_content}}}")
                            content = new_content
    
    # Записываем обновленный файл
    with open('i18n-manager.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Недостающие ключи добавлены!")

def main():
    print("🔧 Добавляем недостающие ключи переводов...")
    add_missing_keys()
    print("✅ Готово!")

if __name__ == "__main__":
    main()
