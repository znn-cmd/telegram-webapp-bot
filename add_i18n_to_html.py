#!/usr/bin/env python3
"""
Скрипт для автоматического добавления мультиязычности в HTML файлы
"""

import os
import re
import glob
from pathlib import Path

def add_i18n_to_html_files():
    """Добавляет мультиязычность в HTML файлы"""
    # Находим все HTML файлы в проекте
    html_files = []
    html_files.extend(glob.glob("webapp_*.html"))
    html_files.extend(glob.glob("*.html"))
    
    # Исключаем файлы, которые уже обработаны или не нужны
    exclude_files = ['template.html', 'index.html', 'aaadvisor_landing.html']
    html_files = [f for f in html_files if f not in exclude_files]
    
    for html_file in html_files:
        print(f"Обрабатываем файл: {html_file}")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Добавляем i18n-manager.js, если его еще нет
            if 'i18n-manager.js' not in content:
                if 'telegram-web-app.js' in content:
                    content = re.sub(
                        r'(<script src="https://telegram\.org/js/telegram-web-app\.js"></script>)',
                        r'\1\n    <script src="/i18n-manager.js"></script>',
                        content
                    )
                else:
                    content = re.sub(
                        r'(<head>)',
                        r'\1\n    <script src="https://telegram.org/js/telegram-web-app.js"></script>\n    <script src="/i18n-manager.js"></script>',
                        content
                    )

            # Добавляем data-i18n атрибуты
            content = add_data_i18n_attributes(content)
            
            # Обновляем атрибут lang у html
            content = re.sub(r'<html[^>]*>', f'<html lang="{get_dynamic_lang()}">', content)

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Файл {html_file} обновлен")
        except Exception as e:
            print(f"❌ Ошибка обработки файла {html_file}: {e}")

def get_dynamic_lang():
    """Возвращает динамический атрибут lang"""
    return 'ru'  # По умолчанию русский, будет изменяться через JavaScript

def add_data_i18n_attributes(content):
    """Добавляет data-i18n атрибуты к элементам"""
    translations = {
        # Общие элементы
        'Загрузка...': 'common.loading',
        'Ошибка': 'common.error',
        'Успешно': 'common.success',
        'Отмена': 'common.cancel',
        'Подтвердить': 'common.confirm',
        'Назад': 'common.back',
        'Далее': 'common.next',
        'Сохранить': 'common.save',
        'Редактировать': 'common.edit',
        'Удалить': 'common.delete',
        'Поиск': 'common.search',
        'Фильтр': 'common.filter',
        'Сортировка': 'common.sort',
        'Обновить': 'common.refresh',
        'Закрыть': 'common.close',
        'Да': 'common.yes',
        'Нет': 'common.no',
        'OK': 'common.ok',
        'Копировать': 'common.copy',
        'Скачать': 'common.download',
        'Поделиться': 'common.share',
        'Печать': 'common.print',
        'Экспорт': 'common.export',
        'Импорт': 'common.import',
        'Настройки': 'common.settings',
        'Профиль': 'common.profile',
        'Выйти': 'common.logout',
        'Войти': 'common.login',
        'Регистрация': 'common.register',
        'Помощь': 'common.help',
        'Поддержка': 'common.support',
        'О нас': 'common.about',
        'Контакты': 'common.contact',
        'Конфиденциальность': 'common.privacy',
        'Условия': 'common.terms',
        'Язык': 'common.language',
        'Валюта': 'common.currency',
        'Часовой пояс': 'common.timezone',
        'Уведомления': 'common.notifications',
        'Темная тема': 'common.dark_mode',
        'Светлая тема': 'common.light_mode',
        
        # Профиль
        'Личный кабинет': 'profile.title',
        'Личная информация': 'profile.personal_info',
        'Имя': 'profile.first_name',
        'Фамилия': 'profile.last_name',
        'Email': 'profile.email',
        'Телефон': 'profile.phone',
        'Telegram': 'profile.telegram',
        'Баланс': 'profile.balance',
        'Баланс: $': 'profile.balance_amount',
        'Пополнить': 'profile.top_up',
        'Вывести': 'profile.withdraw',
        'История транзакций': 'profile.transaction_history',
        'Реферальная программа': 'profile.referral_program',
        'Редактировать профиль': 'profile.edit_profile',
        'Настройки языка': 'profile.language_settings',
        'Настройки уведомлений': 'profile.notification_settings',
        'Настройки безопасности': 'profile.security_settings',
        'Информация об аккаунте': 'profile.account_info',
        'ID пользователя': 'profile.user_id',
        'Дата регистрации': 'profile.registration_date',
        'Последний вход': 'profile.last_login',
        'Статус': 'profile.status',
        'Администратор': 'profile.admin',
        'Пользователь': 'profile.user',
        'Премиум': 'profile.premium',
        'Бесплатный': 'profile.free',
        'Изменить пароль': 'profile.change_password',
        'Удалить аккаунт': 'profile.delete_account',
        'Сохранить изменения': 'profile.save_changes',
        'Изменения сохранены': 'profile.changes_saved',
        'Ошибка сохранения': 'profile.error_saving',
        'Профиль обновлен': 'profile.profile_updated',
        'Пароль изменен': 'profile.password_changed',
        'Аккаунт удален': 'profile.account_deleted',
        
        # Баланс
        'Текущий баланс': 'balance.current_balance',
        'Пополнить баланс': 'balance.top_up_balance',
        'Вывести средства': 'balance.withdraw_funds',
        'Сумма': 'balance.amount',
        'Дата': 'balance.date',
        'Тип': 'balance.type',
        'Описание': 'balance.description',
        'Пополнение': 'balance.income',
        'Списание': 'balance.expense',
        'В обработке': 'balance.pending',
        'Завершено': 'balance.completed',
        'Ошибка': 'balance.failed',
        'Способ оплаты': 'balance.payment_method',
        'Карта': 'balance.card',
        'Банковский перевод': 'balance.bank_transfer',
        'Криптовалюта': 'balance.crypto',
        'Минимальная сумма': 'balance.min_amount',
        'Максимальная сумма': 'balance.max_amount',
        'Комиссия': 'balance.fee',
        'Итого': 'balance.total',
        
        # Отчеты
        'Отчеты': 'reports.title',
        'Мои отчеты': 'reports.my_reports',
        'Создать отчет': 'reports.create_report',
        'Детали отчета': 'reports.report_details',
        'Тип отчета': 'reports.report_type',
        'Оценка недвижимости': 'reports.property_evaluation',
        'Анализ рынка': 'reports.market_analysis',
        'Инвестиционный анализ': 'reports.investment_analysis',
        'Аналитика региона': 'reports.region_analytics',
        'Полный отчет': 'reports.full_report',
        'Дата отчета': 'reports.report_date',
        'Адрес объекта': 'reports.property_address',
        'Тип недвижимости': 'reports.property_type',
        'Площадь': 'reports.property_area',
        'Цена': 'reports.property_price',
        'Рыночная стоимость': 'reports.market_value',
        'Инвестиционный потенциал': 'reports.investment_potential',
        'Уровень риска': 'reports.risk_level',
        'Рекомендации': 'reports.recommendations',
        'Скачать отчет': 'reports.download_report',
        'Поделиться отчетом': 'reports.share_report',
        'Удалить отчет': 'reports.delete_report',
        'Редактировать отчет': 'reports.edit_report',
        'Сохранить отчет': 'reports.save_report',
        'Отчет сохранен': 'reports.report_saved',
        'Отчет удален': 'reports.report_deleted',
        'Отчет отправлен': 'reports.report_shared',
        
        # Главное меню
        'Главное меню': 'main.title',
        'Добро пожаловать': 'main.welcome',
        'Быстрые действия': 'main.quick_actions',
        'Последние отчеты': 'main.recent_reports',
        'Популярные услуги': 'main.popular_services',
        'Новости': 'main.news',
        'Меню': 'main.menu',
        'Главная': 'main.home',
        'Аналитика': 'main.analytics',
        
        # Админ
        'Админ панель': 'admin.title',
        'Пользователи': 'admin.users',
        'Публикации': 'admin.publications',
        'Статистика': 'admin.statistics',
        'Управление пользователями': 'admin.user_management',
        'Управление контентом': 'admin.content_management',
        'Системные настройки': 'admin.system_settings',
        'Резервное копирование': 'admin.backup',
        'Логи': 'admin.logs',
        'Безопасность': 'admin.security',
        
        # Дополнительные элементы
        'Вернуться в главное меню': 'common.back',
        'Выберите язык': 'common.language',
        'Язык успешно изменен': 'common.success',
        'Ошибка сохранения языка': 'common.error',
        'Ошибка сети': 'common.error',
        'Пользователь не определен': 'common.error',
        'Откройте WebApp из Telegram': 'common.error',
        'Ошибка загрузки данных профиля': 'common.error',
        'Failed to load user data': 'common.error',
        'Ошибка сети': 'common.error'
    }

    for text, key in translations.items():
        # Заменяем текст в элементах
        content = re.sub(
            rf'>\s*{re.escape(text)}\s*<',
            f' data-i18n="{key}">{text}<',
            content
        )
        
        # Заменяем заголовки страниц
        content = re.sub(
            rf'<title[^>]*>\s*{re.escape(text)}',
            f'<title data-i18n-title="{key}">{text}',
            content
        )
        
        # Заменяем placeholder
        content = re.sub(
            rf'placeholder="\s*{re.escape(text)}\s*"',
            f'placeholder="{text}" data-i18n-placeholder="{key}"',
            content
        )
        
        # Заменяем alt атрибуты
        content = re.sub(
            rf'alt="\s*{re.escape(text)}\s*"',
            f'alt="{text}" data-i18n-alt="{key}"',
            content
        )

    return content

def main():
    print("🚀 Начинаем добавление мультиязычности в HTML файлы...")
    
    if not os.path.exists('app.py'):
        print("❌ Файл app.py не найден. Убедитесь, что вы находитесь в корневой директории проекта.")
        return
    
    add_i18n_to_html_files()
    
    print("✅ Обработка завершена!")
    print("\n📝 Следующие шаги:")
    print("1. Проверьте обновленные HTML файлы")
    print("2. Добавьте недостающие переводы в i18n-manager.js")
    print("3. Протестируйте мультиязычность в браузере")
    print("4. Обновите переводы для всех 5 языков")
    print("\n🌍 Поддерживаемые языки:")
    print("- 🇷🇺 Русский (ru)")
    print("- 🇺🇸 English (en)")
    print("- 🇩🇪 Deutsch (de)")
    print("- 🇫🇷 Français (fr)")
    print("- 🇹🇷 Türkçe (tr)")

if __name__ == "__main__":
    main()
