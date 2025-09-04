// Менеджер интернационализации для административных страниц
class I18nManager {
    constructor() {
        this.currentLanguage = 'ru';
        this.translations = {
            ru: {
                // Общие
                'back': 'Назад',
                'loading': 'Загрузка...',
                'error': 'Ошибка',
                'success': 'Успешно',
                'cancel': 'Отмена',
                'save': 'Сохранить',
                'delete': 'Удалить',
                'edit': 'Редактировать',
                'add': 'Добавить',
                'search': 'Поиск',
                'refresh': 'Обновить',
                'export': 'Экспорт',
                'import': 'Импорт',
                
                // Административная панель
                'admin_panel': 'Административная панель',
                'admin_badge': 'АДМИНИСТРАТОР',
                'performance_monitoring': 'Мониторинг производительности',
                'user_management': 'Управление пользователями',
                'settings': 'Настройки',
                'publications': 'Публикации',
                'api_keys': 'API ключи',
                'statistics': 'Статистика',
                'reports': 'Отчеты',
                'cache_management': 'Управление кэшем',
                
                // Статистика производительности
                'uptime': 'Время работы',
                'total_requests': 'Всего запросов',
                'success_rate': 'Успешность',
                'avg_response_time': 'Среднее время ответа',
                'active_connections': 'Активные соединения',
                'total_metrics': 'Всего метрик',
                'cache_hit_rate': 'Cache Hit Rate',
                'memory_usage': 'Использование памяти',
                'error_rate': 'Процент ошибок',
                
                // Кэши
                'cache_stats': 'Статистика кэшей',
                'cache_clear': 'Очистить кэши',
                'cache_size': 'Размер кэша',
                'cache_ttl': 'TTL кэша',
                'cache_entries': 'записей',
                'location_cache': 'Локации',
                'currency_cache': 'Курсы валют',
                'market_cache': 'Рыночные данные',
                'user_cache': 'Пользователи',
                
                // Метрики
                'api_metrics': 'Метрики API',
                'db_metrics': 'Метрики БД',
                'endpoint': 'Endpoint',
                'query': 'Запрос',
                'execution_time': 'Время выполнения',
                'requests_count': 'Количество запросов',
                'queries_count': 'Количество запросов',
                
                // Пользователи
                'users': 'Пользователи',
                'total_users': 'Всего пользователей',
                'new_users': 'Новых пользователей',
                'active_users': 'Активных пользователей',
                'expired_users': 'Истекших пользователей',
                'admin_users': 'Администраторов',
                'user_balance': 'Баланс пользователей',
                'total_balance': 'Общий баланс',
                'active_balance': 'Активный баланс',
                'expired_balance': 'Истекший баланс',
                
                // Отчеты
                'total_reports': 'Всего отчетов',
                'reports_this_week': 'Отчетов за неделю',
                'reports_this_month': 'Отчетов за месяц',
                'reports_this_quarter': 'Отчетов за квартал',
                'reports_this_year': 'Отчетов за год',
                'deleted_reports': 'Удаленных отчетов',
                'reports_cost': 'Стоимость отчетов',
                
                // Сообщения
                'access_denied': 'Доступ запрещен',
                'admin_required': 'Требуются права администратора',
                'operation_successful': 'Операция выполнена успешно',
                'operation_failed': 'Операция не выполнена',
                'confirm_delete': 'Вы уверены, что хотите удалить?',
                'confirm_clear_cache': 'Вы уверены, что хотите очистить все кэши?',
                'confirm_clear_metrics': 'Вы уверены, что хотите очистить старые метрики?',
                
                // Время
                'days': 'дней',
                'hours': 'часов',
                'minutes': 'минут',
                'seconds': 'секунд',
                'week': 'неделя',
                'day': 'день',
                'month': 'месяц',
                'quarter': 'квартал',
                'year': 'год'
            },
            en: {
                // General
                'back': 'Back',
                'loading': 'Loading...',
                'error': 'Error',
                'success': 'Success',
                'cancel': 'Cancel',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'add': 'Add',
                'search': 'Search',
                'refresh': 'Refresh',
                'export': 'Export',
                'import': 'Import',
                
                // Admin panel
                'admin_panel': 'Admin Panel',
                'admin_badge': 'ADMINISTRATOR',
                'performance_monitoring': 'Performance Monitoring',
                'user_management': 'User Management',
                'settings': 'Settings',
                'publications': 'Publications',
                'api_keys': 'API Keys',
                'statistics': 'Statistics',
                'reports': 'Reports',
                'cache_management': 'Cache Management',
                
                // Performance statistics
                'uptime': 'Uptime',
                'total_requests': 'Total Requests',
                'success_rate': 'Success Rate',
                'avg_response_time': 'Average Response Time',
                'active_connections': 'Active Connections',
                'total_metrics': 'Total Metrics',
                'cache_hit_rate': 'Cache Hit Rate',
                'memory_usage': 'Memory Usage',
                'error_rate': 'Error Rate',
                
                // Caches
                'cache_stats': 'Cache Statistics',
                'cache_clear': 'Clear Caches',
                'cache_size': 'Cache Size',
                'cache_ttl': 'Cache TTL',
                'cache_entries': 'entries',
                'location_cache': 'Locations',
                'currency_cache': 'Currency Rates',
                'market_cache': 'Market Data',
                'user_cache': 'Users',
                
                // Metrics
                'api_metrics': 'API Metrics',
                'db_metrics': 'Database Metrics',
                'endpoint': 'Endpoint',
                'query': 'Query',
                'execution_time': 'Execution Time',
                'requests_count': 'Requests Count',
                'queries_count': 'Queries Count',
                
                // Users
                'users': 'Users',
                'total_users': 'Total Users',
                'new_users': 'New Users',
                'active_users': 'Active Users',
                'expired_users': 'Expired Users',
                'admin_users': 'Administrators',
                'user_balance': 'User Balance',
                'total_balance': 'Total Balance',
                'active_balance': 'Active Balance',
                'expired_balance': 'Expired Balance',
                
                // Reports
                'total_reports': 'Total Reports',
                'reports_this_week': 'Reports This Week',
                'reports_this_month': 'Reports This Month',
                'reports_this_quarter': 'Reports This Quarter',
                'reports_this_year': 'Reports This Year',
                'deleted_reports': 'Deleted Reports',
                'reports_cost': 'Reports Cost',
                
                // Messages
                'access_denied': 'Access Denied',
                'admin_required': 'Administrator privileges required',
                'operation_successful': 'Operation completed successfully',
                'operation_failed': 'Operation failed',
                'confirm_delete': 'Are you sure you want to delete?',
                'confirm_clear_cache': 'Are you sure you want to clear all caches?',
                'confirm_clear_metrics': 'Are you sure you want to clear old metrics?',
                
                // Time
                'days': 'days',
                'hours': 'hours',
                'minutes': 'minutes',
                'seconds': 'seconds',
                'week': 'week',
                'day': 'day',
                'month': 'month',
                'quarter': 'quarter',
                'year': 'year'
            }
        };
    }
    
    setLanguage(lang) {
        this.currentLanguage = lang;
        this.updatePage();
    }
    
    getText(key) {
        const lang = this.currentLanguage;
        const translation = this.translations[lang] || this.translations['en'];
        return translation[key] || key;
    }
    
    updatePage() {
        // Обновляем все элементы с data-i18n атрибутом
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.getText(key);
        });
        
        // Обновляем placeholder атрибуты
        const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
        placeholders.forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.getText(key);
        });
        
        // Обновляем title атрибуты
        const titles = document.querySelectorAll('[data-i18n-title]');
        titles.forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.getText(key);
        });
    }
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}${this.getText('days')} ${hours}${this.getText('hours')} ${minutes}${this.getText('minutes')}`;
        } else if (hours > 0) {
            return `${hours}${this.getText('hours')} ${minutes}${this.getText('minutes')}`;
        } else {
            return `${minutes}${this.getText('minutes')}`;
        }
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat(this.currentLanguage === 'ru' ? 'ru-RU' : 'en-US').format(num);
    }
    
    formatPercentage(num) {
        return new Intl.NumberFormat(this.currentLanguage === 'ru' ? 'ru-RU' : 'en-US', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(num / 100);
    }
}

// Глобальный экземпляр менеджера интернационализации
window.i18n = new I18nManager();

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Определяем язык из URL или используем русский по умолчанию
    const urlParams = new URLSearchParams(window.location.search);
    const lang = urlParams.get('lang') || 'ru';
    window.i18n.setLanguage(lang);
    
    // Добавляем переключатель языка если нужно
    if (document.querySelector('.language-switcher')) {
        const switcher = document.querySelector('.language-switcher');
        switcher.addEventListener('change', function(e) {
            window.i18n.setLanguage(e.target.value);
        });
    }
});
