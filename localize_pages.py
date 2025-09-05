#!/usr/bin/env python3
"""
Скрипт для автоматической локализации HTML страниц приложения
Добавляет атрибуты data-i18n к текстовым элементам
"""

import os
import re
from pathlib import Path

# Маппинг текстов на ключи локализации
TEXT_TO_KEY_MAPPING = {
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
    'Пополнение баланса': 'topup.title',
    'Текущий баланс': 'topup.current_balance',
    'Сумма пополнения': 'topup.amount',
    'Минимальная сумма: $1': 'topup.min_amount',
    'Способ оплаты': 'topup.payment_method',
    'Банковская карта': 'topup.card',
    'Криптовалюта': 'topup.crypto',
    'Оплатить': 'topup.pay',
    
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
    'Мгновенные аналитические отчеты по недвижимости': 'main.slogan',
    'Оценка объекта': 'main.object_evaluation',
    'Реальные данные': 'main.real_data',
    'Дополнительные данные': 'main.additional_data',
    'География': 'main.geography',
    
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
    'Сделать баланс 100': 'admin.make_balance_100',
    'Админ-панель': 'admin.admin_panel',
    'Статистика пользователей': 'admin.user_stats',
    'Управление публикациями': 'admin.publication_management',
    '← Вернуться в главное меню': 'admin.back_to_main',
    
    # Помощь
    'Помощь': 'help.title',
    'Часто задаваемые вопросы': 'help.faq',
    'Связаться с поддержкой': 'help.contact_support',
    
    # Поддержка
    'Поддержка': 'support.title',
    'Связаться с нами': 'support.contact_us',
    
    # О нас
    'О нас': 'about.title',
    'Описание компании': 'about.description',
    'Возможности': 'about.features',
    
    # Инструкция
    'Инструкция': 'instruction.title',
    'Как пользоваться': 'instruction.how_to_use',
    'Пошаговая инструкция': 'instruction.step_by_step',
    
    # Реферальная программа
    'Реферальная программа': 'referral.title',
    'Ваш код': 'referral.your_code',
    'Пригласите друзей': 'referral.invite_friends',
    'Заработок': 'referral.earnings',
    
    # Мои отчеты
    'У вас пока нет отчетов': 'my_reports.no_reports',
    'Создать первый отчет': 'my_reports.create_first',
    
    # Реальные данные
    'Описание раздела': 'real_data.description',
    
    # Дополнительные данные
    'Описание раздела': 'additional_data.description',
    
    # География
    'Описание раздела': 'geography.description',
    
    # Полный отчет
    'Генерация отчета...': 'full_report.generating',
}

def add_i18n_attributes(html_content):
    """Добавляет атрибуты data-i18n к текстовым элементам"""
    
    # Паттерн для поиска текста в различных HTML элементах
    patterns = [
        # Текст в тегах <span>, <div>, <p>, <h1>-<h6>, <button>, <a>
        (r'<(\w+)([^>]*?)>([^<]+?)</\1>', r'<\1\2 data-i18n="{}">\3</\1>'),
        # Текст в атрибутах title, placeholder, alt
        (r'(title|placeholder|alt)="([^"]+)"', r'\1="\2" data-i18n-\1="{}"'),
    ]
    
    modified_content = html_content
    
    for text, key in TEXT_TO_KEY_MAPPING.items():
        if text in modified_content:
            # Заменяем текст в тегах
            pattern = r'<(\w+)([^>]*?)>' + re.escape(text) + r'</\1>'
            replacement = r'<\1\2 data-i18n="' + key + r'">' + text + r'</\1>'
            modified_content = re.sub(pattern, replacement, modified_content)
            
            # Заменяем текст в атрибутах
            for attr in ['title', 'placeholder', 'alt']:
                pattern = attr + r'="' + re.escape(text) + r'"'
                replacement = attr + r'="' + text + r'" data-i18n-' + attr + r'="' + key + r'"'
                modified_content = re.sub(pattern, replacement, modified_content)
    
    return modified_content

def localize_html_file(file_path):
    """Локализует один HTML файл"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем подключение i18n-manager.js если его нет
        if 'i18n-manager.js' not in content and '<script' in content:
            content = content.replace(
                '<script src="https://telegram.org/js/telegram-web-app.js"></script>',
                '<script src="https://telegram.org/js/telegram-web-app.js"></script>\n    <script src="/static/i18n-manager.js"></script>'
            )
        
        # Добавляем атрибуты data-i18n
        localized_content = add_i18n_attributes(content)
        
        # Сохраняем изменения
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(localized_content)
        
        print(f"✅ Локализован: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при локализации {file_path}: {e}")
        return False

def main():
    """Основная функция"""
    print("🌐 Начинаем локализацию HTML страниц...")
    
    # Находим все HTML файлы
    html_files = list(Path('.').glob('webapp_*.html'))
    
    if not html_files:
        print("❌ HTML файлы не найдены")
        return
    
    print(f"📁 Найдено {len(html_files)} HTML файлов")
    
    success_count = 0
    for file_path in html_files:
        if localize_html_file(file_path):
            success_count += 1
    
    print(f"\n🎉 Локализация завершена!")
    print(f"✅ Успешно обработано: {success_count}/{len(html_files)} файлов")

if __name__ == "__main__":
    main()
