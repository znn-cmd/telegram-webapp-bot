#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления атрибутов data-i18n к HTML файлам
"""

import os
import re
from bs4 import BeautifulSoup
import html

def add_i18n_attributes_to_html():
    """Добавляет атрибуты data-i18n к HTML файлам"""
    
    # Список файлов для обработки
    html_files = [
        'webapp_main.html',
        'webapp_profile.html',
        'webapp_reports.html',
        'webapp_balance.html',
        'webapp_settings.html',
        'webapp_help.html',
        'webapp_about.html',
        'webapp_support.html',
        'webapp_admin.html',
        'webapp_admin_users.html',
        'webapp_admin_settings.html',
        'webapp_admin_publication.html',
        'webapp_my_reports.html',
        'webapp_full_report.html',
        'webapp_object_evaluation.html',
        'webapp_region_analytics.html',
        'webapp_geography.html',
        'webapp_real_data.html',
        'webapp_additional_data.html',
        'webapp_saved.html',
        'webapp_stats.html',
        'webapp_referral.html',
        'webapp_topup.html',
        'webapp_instruction.html'
    ]
    
    # Словарь переводов для поиска текста
    translations = {
        'ru': {
            'common': {
                'loading': 'Загрузка...',
                'error': 'Ошибка',
                'success': 'Успешно',
                'cancel': 'Отмена',
                'confirm': 'Подтвердить',
                'back': 'Назад',
                'next': 'Далее',
                'save': 'Сохранить',
                'edit': 'Редактировать',
                'delete': 'Удалить',
                'search': 'Поиск',
                'filter': 'Фильтр',
                'sort': 'Сортировка',
                'refresh': 'Обновить',
                'close': 'Закрыть',
                'yes': 'Да',
                'no': 'Нет',
                'ok': 'OK',
                'copy': 'Копировать',
                'download': 'Скачать',
                'share': 'Поделиться',
                'print': 'Печать',
                'export': 'Экспорт',
                'import': 'Импорт',
                'settings': 'Настройки',
                'profile': 'Профиль',
                'logout': 'Выйти',
                'login': 'Войти',
                'register': 'Регистрация',
                'help': 'Помощь',
                'support': 'Поддержка',
                'about': 'О нас',
                'contact': 'Контакты',
                'privacy': 'Конфиденциальность',
                'terms': 'Условия',
                'language': 'Язык',
                'currency': 'Валюта',
                'timezone': 'Часовой пояс',
                'notifications': 'Уведомления',
                'dark_mode': 'Темная тема',
                'light_mode': 'Светлая тема'
            },
            'profile': {
                'title': 'Личный кабинет',
                'personal_info': 'Личная информация',
                'first_name': 'Имя',
                'last_name': 'Фамилия',
                'email': 'Email',
                'phone': 'Телефон',
                'telegram': 'Telegram',
                'balance': 'Баланс',
                'balance_amount': 'Баланс: $',
                'top_up': 'Пополнить',
                'withdraw': 'Вывести',
                'transaction_history': 'История транзакций',
                'referral_program': 'Реферальная программа',
                'edit_profile': 'Редактировать профиль',
                'language_settings': 'Настройки языка',
                'notification_settings': 'Настройки уведомлений',
                'security_settings': 'Настройки безопасности',
                'account_info': 'Информация об аккаунте',
                'user_id': 'ID пользователя',
                'registration_date': 'Дата регистрации',
                'last_login': 'Последний вход',
                'status': 'Статус',
                'admin': 'Администратор',
                'user': 'Пользователь',
                'premium': 'Премиум',
                'free': 'Бесплатный',
                'change_password': 'Изменить пароль',
                'delete_account': 'Удалить аккаунт',
                'save_changes': 'Сохранить изменения',
                'changes_saved': 'Изменения сохранены',
                'error_saving': 'Ошибка сохранения',
                'profile_updated': 'Профиль обновлен',
                'password_changed': 'Пароль изменен',
                'account_deleted': 'Аккаунт удален'
            },
            'balance': {
                'title': 'Баланс',
                'current_balance': 'Текущий баланс',
                'top_up_balance': 'Пополнить баланс',
                'withdraw_funds': 'Вывести средства',
                'transaction_history': 'История транзакций',
                'amount': 'Сумма',
                'date': 'Дата',
                'type': 'Тип',
                'status': 'Статус',
                'description': 'Описание',
                'income': 'Пополнение',
                'expense': 'Списание',
                'pending': 'В обработке',
                'completed': 'Завершено',
                'failed': 'Ошибка',
                'payment_method': 'Способ оплаты',
                'card': 'Карта',
                'bank_transfer': 'Банковский перевод',
                'crypto': 'Криптовалюта',
                'min_amount': 'Минимальная сумма',
                'max_amount': 'Максимальная сумма',
                'fee': 'Комиссия',
                'total': 'Итого'
            },
            'reports': {
                'title': 'Отчеты',
                'my_reports': 'Мои отчеты',
                'create_report': 'Создать отчет',
                'report_details': 'Детали отчета',
                'report_type': 'Тип отчета',
                'property_evaluation': 'Оценка недвижимости',
                'market_analysis': 'Анализ рынка',
                'investment_analysis': 'Инвестиционный анализ',
                'region_analytics': 'Аналитика региона',
                'full_report': 'Полный отчет',
                'report_date': 'Дата отчета',
                'property_address': 'Адрес объекта',
                'property_type': 'Тип недвижимости',
                'property_area': 'Площадь',
                'property_price': 'Цена',
                'market_value': 'Рыночная стоимость',
                'investment_potential': 'Инвестиционный потенциал',
                'risk_level': 'Уровень риска',
                'recommendations': 'Рекомендации',
                'download_report': 'Скачать отчет',
                'share_report': 'Поделиться отчетом',
                'delete_report': 'Удалить отчет',
                'edit_report': 'Редактировать отчет',
                'save_report': 'Сохранить отчет',
                'report_saved': 'Отчет сохранен',
                'report_deleted': 'Отчет удален',
                'report_shared': 'Отчет отправлен',
                'liquidity': 'Ликвидность'
            },
            'main': {
                'title': 'Главное меню',
                'welcome': 'Добро пожаловать',
                'quick_actions': 'Быстрые действия',
                'recent_reports': 'Последние отчеты',
                'popular_services': 'Популярные услуги',
                'news': 'Новости',
                'notifications': 'Уведомления',
                'menu': 'Меню',
                'home': 'Главная',
                'reports': 'Отчеты',
                'analytics': 'Аналитика',
                'profile': 'Профиль',
                'help': 'Помощь',
                'settings': 'Настройки'
            },
            'admin': {
                'title': 'Админ панель',
                'users': 'Пользователи',
                'publications': 'Публикации',
                'settings': 'Настройки',
                'statistics': 'Статистика',
                'user_management': 'Управление пользователями',
                'content_management': 'Управление контентом',
                'system_settings': 'Системные настройки',
                'backup': 'Резервное копирование',
                'logs': 'Логи',
                'security': 'Безопасность'
            }
        }
    }
    
    # Создаем плоский список всех переводов для поиска
    flat_translations = {}
    for section, items in translations['ru'].items():
        for key, value in items.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_translations[sub_value] = f"{section}.{key}.{sub_key}"
            else:
                flat_translations[value] = f"{section}.{key}"
    
    processed_files = 0
    
    for filename in html_files:
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден, пропускаем")
            continue
            
        print(f"🔍 Обрабатываем файл: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Ищем элементы с текстом, которые можно перевести
            elements_to_translate = []
            
            # Ищем заголовки, кнопки, ссылки и другие элементы
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'button', 'a', 'span', 'div', 'p', 'label']):
                if tag.get('data-i18n'):  # Пропускаем уже переведенные
                    continue
                    
                text = tag.get_text(strip=True)
                if text and len(text) > 2 and text in flat_translations:
                    elements_to_translate.append((tag, text, flat_translations[text]))
            
            # Добавляем атрибуты data-i18n
            for element, text, translation_key in elements_to_translate:
                element['data-i18n'] = translation_key
                print(f"  ✅ Добавлен перевод: {text} → {translation_key}")
            
            # Сохраняем файл
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            processed_files += 1
            print(f"  ✅ Файл {filename} обновлен ({len(elements_to_translate)} переводов)")
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")
    
    print(f"\n🎯 Обработано файлов: {processed_files}")
    print("✅ Добавление атрибутов data-i18n завершено!")

if __name__ == "__main__":
    add_i18n_attributes_to_html()
