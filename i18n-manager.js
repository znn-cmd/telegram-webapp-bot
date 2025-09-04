// Универсальная система мультиязычности для всех страниц приложения
class I18nManager {
    constructor() {
        this.currentLanguage = 'ru';
        this.translations = {};
        this.init();
    }

    async init() {
        console.log('🚀 Инициализация I18nManager...');
        this.currentLanguage = this.getInitialLanguage();
        console.log(`🌐 Установлен язык: ${this.currentLanguage}`);
        
        await this.loadTranslations();
        console.log('📚 Переводы загружены:', this.translations);
        
        this.applyTranslations();
        console.log('✅ Переводы применены');
        
        this.addLanguageSelector();
        console.log('🎯 I18nManager инициализирован');
    }

    getInitialLanguage() {
        // Пытаемся получить язык из Telegram WebApp
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            if (tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) {
                const lang = tg.initDataUnsafe.user.language_code.substring(0, 2);
                if (['ru', 'en', 'de', 'fr', 'tr'].includes(lang)) {
                    return lang;
                }
            }
        }

        // Пытаемся получить из localStorage
        try {
            const stored = localStorage.getItem('aaadviser_language');
            if (stored && ['ru', 'en', 'de', 'fr', 'tr'].includes(stored)) {
                return stored;
            }
        } catch (e) {}

        // По умолчанию русский
        return 'ru';
    }

    async loadTranslations() {
        // Всегда используем локальные переводы для надежности
        this.loadFallbackTranslations();
        
        // Дополнительно пытаемся загрузить с сервера (но не блокируем)
        try {
            const response = await fetch('/api/translations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: this.currentLanguage })
            });

            if (response.ok) {
                const serverTranslations = await response.json();
                // Объединяем с локальными переводами
                this.translations = { ...this.translations, ...serverTranslations };
                console.log('✅ Переводы загружены с сервера');
            } else {
                console.warn('⚠️ Сервер недоступен, используем локальные переводы');
            }
        } catch (error) {
            console.warn('⚠️ Ошибка загрузки с сервера, используем локальные переводы:', error);
        }
    }

    loadFallbackTranslations() {
        // Базовые переводы для всех языков
        this.translations = {
            'ru': {
                'common': {
                    'loading': 'Загрузка...', 'error': 'Ошибка', 'success': 'Успешно',
                    'cancel': 'Отмена', 'confirm': 'Подтвердить', 'back': 'Назад',
                    'next': 'Далее', 'save': 'Сохранить', 'edit': 'Редактировать',
                    'delete': 'Удалить', 'search': 'Поиск', 'filter': 'Фильтр',
                    'sort': 'Сортировка', 'refresh': 'Обновить', 'close': 'Закрыть',
                    'yes': 'Да', 'no': 'Нет', 'ok': 'OK', 'copy': 'Копировать',
                    'download': 'Скачать', 'share': 'Поделиться', 'print': 'Печать',
                    'export': 'Экспорт', 'import': 'Импорт', 'settings': 'Настройки',
                    'profile': 'Профиль', 'logout': 'Выйти', 'login': 'Войти',
                    'register': 'Регистрация', 'help': 'Помощь', 'support': 'Поддержка',
                    'about': 'О нас', 'contact': 'Контакты', 'privacy': 'Конфиденциальность',
                    'terms': 'Условия', 'language': 'Язык', 'currency': 'Валюта',
                    'timezone': 'Часовой пояс', 'notifications': 'Уведомления',
                    'dark_mode': 'Темная тема', 'light_mode': 'Светлая тема',
                    'about_app': 'О приложении',
                    'instruction': 'Инструкция',
                    'our_geography': 'Наша география',
                    'technical_support': 'Техническая поддержка',
                    'about_app_title': 'О приложении',
                    'about_app_what_is': 'Что такое Aaadviser?',
                    'about_app_description': 'Aaadviser — это интеллектуальная платформа для анализа рынка недвижимости, которая помогает инвесторам и покупателям принимать обоснованные решения.',
                    'about_app_capabilities': 'Наши возможности:',
                    'about_app_capability1': 'Детальный анализ цен в районе',
                    'about_app_capability2': 'Статистика рынка недвижимости',
                    'about_app_capability3': 'Сравнение с похожими объектами',
                    'about_app_capability4': 'Прогноз изменения цен',
                    'about_app_capability5': 'Рекомендации по инвестициям',
                    'about_app_capability6': 'Сохранение отчетов',
                    'about_app_capability7': 'Удобный мобильный интерфейс',
                    'about_app_how_works': 'Как это работает?',
                    'about_app_how_works_desc': 'Просто введите адрес недвижимости, укажите количество спален и примерную цену. Наша система проанализирует рынок и предоставит подробный отчет с рекомендациями.',
                    'about_app_why': 'Почему Aaadviser?',
                    'about_app_why_desc': 'Мы используем передовые технологии машинного обучения и большие данные для анализа рынка недвижимости, что позволяет получать точные и актуальные данные для принятия инвестиционных решений.',
                    'about_app_back': '← Назад',
                    'about_app_main_menu': 'В главное меню'
                },
                'profile': {
                    'title': 'Личный кабинет', 'personal_info': 'Личная информация',
                    'first_name': 'Имя', 'last_name': 'Фамилия', 'email': 'Email',
                    'phone': 'Телефон', 'telegram': 'Telegram', 'balance': 'Баланс',
                    'balance_amount': 'Баланс: $', 'top_up': 'Пополнить', 'withdraw': 'Вывести',
                    'transaction_history': 'История транзакций', 'referral_program': 'Реферальная программа',
                    'edit_profile': 'Редактировать профиль', 'language_settings': 'Настройки языка',
                    'notification_settings': 'Настройки уведомлений', 'security_settings': 'Настройки безопасности',
                    'account_info': 'Информация об аккаунте', 'user_id': 'ID пользователя',
                    'registration_date': 'Дата регистрации', 'last_login': 'Последний вход',
                    'status': 'Статус', 'admin': 'Администратор', 'user': 'Пользователь',
                    'premium': 'Премиум', 'free': 'Бесплатный', 'change_password': 'Изменить пароль',
                    'delete_account': 'Удалить аккаунт', 'save_changes': 'Сохранить изменения',
                    'changes_saved': 'Изменения сохранены', 'error_saving': 'Ошибка сохранения',
                    'profile_updated': 'Профиль обновлен', 'password_changed': 'Пароль изменен',
                    'account_deleted': 'Аккаунт удален'
                },
                'balance': {
                    'title': 'Баланс', 'current_balance': 'Текущий баланс',
                    'top_up_balance': 'Пополнить баланс', 'withdraw_funds': 'Вывести средства',
                    'transaction_history': 'История транзакций', 'amount': 'Сумма', 'date': 'Дата',
                    'type': 'Тип', 'status': 'Статус', 'description': 'Описание', 'income': 'Пополнение',
                    'expense': 'Списание', 'pending': 'В обработке', 'completed': 'Завершено',
                    'failed': 'Ошибка', 'payment_method': 'Способ оплаты', 'card': 'Карта',
                    'bank_transfer': 'Банковский перевод', 'crypto': 'Криптовалюта',
                    'min_amount': 'Минимальная сумма', 'max_amount': 'Максимальная сумма',
                    'fee': 'Комиссия', 'total': 'Итого'
                },
                'reports': {
                    'title': 'Отчеты', 'my_reports': 'Мои отчеты', 'create_report': 'Создать отчет',
                    'report_details': 'Детали отчета', 'report_type': 'Тип отчета',
                    'property_evaluation': 'Оценка недвижимости', 'market_analysis': 'Анализ рынка',
                    'investment_analysis': 'Инвестиционный анализ', 'region_analytics': 'Аналитика региона',
                    'full_report': 'Полный отчет', 'report_date': 'Дата отчета',
                    'property_address': 'Адрес объекта', 'property_type': 'Тип недвижимости',
                    'property_area': 'Площадь', 'property_price': 'Цена', 'market_value': 'Рыночная стоимость',
                    'investment_potential': 'Инвестиционный потенциал', 'risk_level': 'Уровень риска',
                    'recommendations': 'Рекомендации', 'download_report': 'Скачать отчет',
                    'share_report': 'Поделиться отчетом', 'delete_report': 'Удалить отчет',
                    'edit_report': 'Редактировать отчет', 'save_report': 'Сохранить отчет',
                    'report_saved': 'Отчет сохранен', 'report_deleted': 'Отчет удален',
                    'report_shared': 'Отчет отправлен', 'liquidity': 'Ликвидность',
                    'page_description': 'Получите детальный анализ рынка недвижимости в выбранном регионе',
                    'country_label': 'Страна:',
                    'city_label': 'Город:',
                    'county_label': 'Область/Регион:',
                    'district_label': 'Район:',
                    'country_placeholder': 'Выберите страну',
                    'city_placeholder': 'Сначала выберите страну',
                    'county_placeholder': 'Сначала выберите город',
                    'district_placeholder': 'Сначала выберите область',
                    'confirm_selection': 'Подтвердить выбор',
                    'back_to_main': '← Вернуться в главное меню',
                    'selected_location': 'Выбранная локация:',
                    'admin_ids': 'IDs для админов:',
                    'loading': 'Загрузка...',
                    'error_loading': 'Ошибка загрузки данных',
                    'data_section_title': 'Анализ региональных данных',
                    'general_data_title': 'Общие данные',
                    'house_type_data_title': 'Данные по количеству спален',
                    'floor_segment_data_title': 'Данные по этажам',
                    'age_data_title': 'Данные по возрасту',
                    'heating_data_title': 'Данные по типу отопления',
                    'loading_text': 'Загрузка данных...',
                    'error_text': 'Ошибка загрузки данных',
                    'total_properties': 'Всего объектов:',
                    'average_price': 'Средняя цена:',
                    'price_range': 'Диапазон цен:',
                    'no_data_available': 'Данные недоступны',
                    'key_metrics_title': 'Ключевые метрики',
                    'avg_sale_price_label': 'Средняя цена продажи за м²',
                    'avg_rent_price_label': 'Средняя цена аренды за м²',
                    'listing_period_sale_label': 'Период размещения (продажа)',
                    'listing_period_rent_label': 'Период размещения (аренда)',
                    'yield_label': 'Yield (Доходность)',
                    'insights_title': 'Саммари',
                    'insights_loading': 'Анализируем данные...',
                    'insights_error': 'Ошибка при анализе данных',
                    'object_evaluation_title': 'Оценка объекта',
                    'object_evaluation_description': 'Получите профессиональную оценку стоимости недвижимости в выбранном регионе',
                    'listing_type_title': 'Выберите тип недвижимости для анализа:',
                    'house_type_subtitle': 'Количество спален:',
                    'floor_segment_subtitle': 'Этаж:',
                    'age_data_subtitle': 'Возраст объекта:',
                    'heating_data_subtitle': 'Тип отопления:',
                    'price_object_subtitle': 'Цена объекта:',
                    'area_object_subtitle': 'Площадь объекта (м²):',
                    'select_bedrooms': 'количество спален',
                    'select_floor': 'этаж',
                    'select_age': 'возраст объекта',
                    'select_heating': 'тип отопления',
                    'property_types_title': 'Выбранные характеристики недвижимости:',
                    'bedrooms_label': 'Количество спален',
                    'floor_label': 'Этаж',
                    'age_label': 'Возраст объекта',
                    'heating_label': 'Тип отопления',
                    'market_indicators_title': 'Показатели рынка',
                    'market_trends_title': 'Тренды рынка',
                    'sale_header': 'Продажа',
                    'rent_header': 'Аренда',
                    'currency_title': 'Выберите валюту:',
                    'save_share_button_text': 'Сохранить и поделиться отчетом',
                    'modal_title': 'Отчет сохранен',
                    'modal_description': 'Ваш отчет успешно сохранен. Вы можете скопировать ссылку и поделиться ею с другими.',
                    'copy_button_text': 'Копировать ссылку',
                    'close_button_text': 'Закрыть',
                    'link_copied': 'Ссылка скопирована!',
                    'saving_report': 'Сохранение отчета...',
                    'error_saving': 'Ошибка сохранения отчета',
                    'price_placeholder': 'Введите цену',
                    'area_placeholder': 'Введите площадь',
                    'trends_filter_info': 'Показано ${filteredCount} из ${totalCount} трендов',
                    'market_comparison_title': 'Сравнение с рынком',
                    'price_per_m2_label': 'Цена за м²',
                    'area_label': 'Площадь',
                    'price_comparison_label': 'Цена за м²:',
                    'area_comparison_label': 'Площадь:',
                    'price_close_to_market': 'Ваш объект (${userPrice}) близок к рыночной (${marketMin} – ${marketMax}).',
                    'price_above_market': 'Ваш объект (${userPrice}) выше рынка на ${percent}%.',
                    'price_below_market': 'Ваш объект (${userPrice}) ниже рынка на ${percent}%.',
                    'area_matches_market': 'Ваш объект (${userArea} м²) соответствует рыночному спросу (${marketMin}–${marketMax} м²).',
                    'area_below_market': 'Ваш объект (${userArea} м²) меньше востребованной на рынке (${marketMin}–${marketMax} м²).',
                    'area_above_market': 'Ваш объект (${userArea} м²) больше востребованной на рынке (${marketMin}–${marketMax} м²).',
                    'consolidated_assessment_title': 'Консолидированная оценка',
                    'sale_price_title': 'Цена за м² (Unit Price For Sale):',
                    'rent_price_title': 'Цена аренды за м² (Unit Price For Rent):',
                    'yield_title': 'Доходность (Yield):',
                    'consolidated_average_label': 'Консолидированная средняя:',
                    'indicator_label': 'Показатель',
                    'min_value_label': 'Минимальное значение',
                    'max_value_label': 'Максимальное значение',
                    'avg_value_label': 'Среднее значение',
                    'count_label': 'Количество',
                    'percentage_label': 'Процент',
                    'my_reports_title': 'Мои отчеты',
                    'my_reports_subtitle': 'Управление вашими отчетами',
                    'my_reports_loading': 'Загрузка отчетов...',
                    'my_reports_empty_title': 'Отчеты не найдены',
                    'my_reports_empty_description': 'У вас пока нет сохраненных отчетов. Создайте первый отчет в главном меню.',
                    'my_reports_back_btn': 'Вернуться в главное меню',
                    'my_reports_view_report': 'Просмотреть',
                    'my_reports_delete_report': 'Удалить',
                    'my_reports_copy_link': 'Копировать ссылку',
                    'my_reports_delete_modal_title': 'Подтверждение удаления',
                    'my_reports_delete_modal_message': 'Вы уверены, что хотите удалить этот отчет? Это действие нельзя отменить.',
                    'my_reports_cancel_delete_btn': 'Отмена',
                    'my_reports_confirm_delete_btn': 'Удалить',
                    'my_reports_link_copied': 'Ссылка скопирована в буфер обмена',
                    'my_reports_report_deleted': 'Отчет успешно удален',
                    'my_reports_error_loading': 'Ошибка загрузки отчетов',
                    'my_reports_error_deleting': 'Ошибка при удалении отчета',
                    'my_reports_no_address': 'Адрес не указан',
                    'my_reports_no_price': 'Цена не указана',
                    'my_reports_no_area': 'Площадь не указана',
                    'my_reports_no_bedrooms': 'Количество комнат не указано',
                    'my_reports_property_evaluation': 'Оценка объекта',
                    'my_reports_property_analysis': 'Анализ объекта',
                    'my_reports_market_analysis': 'Анализ рынка'
                },
                'main': {
                    'title': 'Главное меню', 'welcome': 'Добро пожаловать',
                    'quick_actions': 'Быстрые действия', 'recent_reports': 'Последние отчеты',
                    'popular_services': 'Популярные услуги', 'news': 'Новости',
                    'notifications': 'Уведомления', 'menu': 'Меню', 'home': 'Главная',
                    'reports': 'Отчеты', 'analytics': 'Аналитика', 'profile': 'Профиль',
                    'help': 'Помощь', 'settings': 'Настройки'
                },
                'admin': {
                    'title': 'Админ панель', 'users': 'Пользователи', 'publications': 'Публикации',
                    'settings': 'Настройки', 'statistics': 'Статистика', 'user_management': 'Управление пользователями',
                    'content_management': 'Управление контентом', 'system_settings': 'Системные настройки',
                    'backup': 'Резервное копирование', 'logs': 'Логи', 'security': 'Безопасность'
                },
                'hero': {
                    'title': 'Закрывайте больше сделок с Aaadvisor',
                    'subtitle': 'Профессиональная аналитика недвижимости для риэлторов. Покажите клиенту точные цифры и прогнозы роста.',
                    'feature1': 'Аналитика рынка',
                    'feature2': 'Расчет доходности',
                    'feature3': 'Прогноз цен',
                    'cta': 'Получить отчет бесплатно',
                    'note': 'Бесплатно • Без регистрации • Мгновенно'
                },
                'preview': {
                    'price': 'Стоимость',
                    'growth': 'Рост за год',
                    'yield': 'Доходность'
                },
                'benefits': {
                    'title': 'Почему риэлторы выбирают Aaadvisor',
                    'subtitle': 'Инструмент, который помогает закрывать сделки быстрее и с большим доверием',
                    'card1': {
                        'title': 'Покажите клиенту цифры',
                        'desc': 'Точная аналитика рынка с конкретными цифрами вместо общих фраз'
                    },
                    'card2': {
                        'title': 'Убедите выгодой',
                        'desc': 'Обоснованные аргументы с расчетом доходности и прогнозом роста'
                    },
                    'card3': {
                        'title': 'Прогноз роста стоимости',
                        'desc': 'Покажите клиенту потенциал роста инвестиций в недвижимость'
                    },
                    'card4': {
                        'title': 'Доходность аренды',
                        'desc': 'Расчет рентабельности для инвесторов и арендодателей'
                    },
                    'card5': {
                        'title': 'Закрывайте сделки быстрее',
                        'desc': 'Профессиональные отчеты повышают доверие и ускоряют решения'
                    },
                    'card6': {
                        'title': 'Мгновенный результат',
                        'desc': 'Отчет готов за 1 минуту, без ожидания и сложных процедур'
                    }
                },
                'report': {
                    'title': 'Что увидит ваш клиент',
                    'subtitle': 'Профессиональный отчет с анализом рынка, прогнозом роста и расчетом доходности',
                    'feature1': 'Анализ рынка недвижимости',
                    'feature2': 'Прогноз роста цен на 1-3 года',
                    'feature3': 'Расчет доходности аренды',
                    'feature4': 'Сравнение с аналогичными объектами',
                    'feature5': 'Рекомендации по инвестициям',
                    'cta': 'Сделать такой же отчет'
                },
                'comparison': {
                    'title': 'До и После Aaadvisor',
                    'before': {
                        'title': 'До',
                        'item1': 'Объясняете устно, клиент сомневается',
                        'item2': 'Нет конкретных цифр и обоснований',
                        'item3': 'Сделка откладывается на неопределенный срок',
                        'item4': 'Клиент ищет альтернативы'
                    },
                    'after': {
                        'title': 'После',
                        'item1': 'Показываете профессиональный отчет с цифрами',
                        'item2': 'Клиент видит прогноз роста и доходность',
                        'item3': 'Решение принимается быстрее',
                        'item4': 'Повышается доверие к вам как к эксперту'
                    }
                },
                'social': {
                    'title': 'Нам доверяют риэлторы',
                    'stats': {
                        'objects': 'Объектов проанализировано',
                        'realtors': 'Риэлторов используют',
                        'faster': 'Быстрее закрываются сделки'
                    },
                    'testimonial1': {
                        'text': '"Теперь я показываю клиентам точные цифры и прогнозы. Сделки закрываются в 2 раза быстрее, а доверие клиентов выросло значительно."',
                        'name': 'Анна Петрова',
                        'position': 'Риэлтор, Барселона'
                    },
                    'testimonial2': {
                        'text': '"Aaadvisor помогает обосновать цену объективно. Клиенты видят, что мы не просто продаем, а даем профессиональную консультацию."',
                        'name': 'Сергей Иванов',
                        'position': 'Агентство недвижимости, Лиссабон'
                    }
                },
                'cta': {
                    'title': 'Покажите клиенту выгоду сделки уже сегодня',
                    'subtitle': 'Получите профессиональный отчет за 1 минуту',
                    'feature1': 'Бесплатно в тестовом режиме',
                    'feature2': 'Мгновенный результат',
                    'feature3': 'Работает в Telegram',
                    'button': 'Запустить в Telegram',
                    'note': 'Без регистрации • Без ограничений • Сразу в работе'
                },
                'faq': {
                    'title': 'Часто задаваемые вопросы',
                    'subtitle': 'Ответы на самые популярные вопросы о Aaadvisor',
                    'q1': 'Как работает Aaadvisor?',
                    'a1': 'Aaadvisor — это Telegram бот, который анализирует недвижимость в Турции, Испании и Португалии. Просто отправьте адрес объекта, и бот создаст профессиональный отчет с анализом рынка, прогнозом роста и расчетом доходности.',
                    'q2': 'Какие данные анализирует Aaadvisor?',
                    'a2': 'Бот анализирует текущие цены на недвижимость, историческую динамику цен, рыночные тренды, доходность от аренды, сравнение с аналогичными объектами и прогноз роста стоимости на 1-3 года.',
                    'q3': 'Сколько стоит использование?',
                    'a3': 'В настоящее время Aaadvisor доступен бесплатно в тестовом режиме. Вы можете получить неограниченное количество отчетов без регистрации и без ограничений.',
                    'q4': 'В каких странах работает Aaadvisor?',
                    'a4': 'Сейчас Aaadvisor работает с недвижимостью в Турции, Испании и Португалии. Мы постоянно расширяем географию и добавляем новые рынки.',
                    'q5': 'Насколько точны прогнозы?',
                    'a5': 'Прогнозы основаны на анализе исторических данных, экономических показателей и рыночных трендов. Точность составляет 85-90% для краткосрочных прогнозов (1 год) и 70-80% для долгосрочных (3 года).',
                    'q6': 'Могу ли я использовать отчеты для клиентов?',
                    'a6': 'Да! Отчеты Aaadvisor предназначены именно для работы с клиентами. Они содержат профессиональную аналитику, которую можно показывать покупателям для обоснования цены и потенциальной выгоды от инвестиций.',
                    'q7': 'Как часто обновляются данные?',
                    'a7': 'Данные обновляются еженедельно. Мы отслеживаем изменения цен, новые объявления и рыночные тренды, чтобы обеспечить актуальность информации в отчетах.',
                    'q8': 'Что делать, если бот не отвечает?',
                    'a8': 'Если возникли проблемы с ботом, обратитесь в нашу поддержку через Telegram канал @Aaadviser_support. Мы обычно отвечаем в течение 1-2 часов в рабочее время.',
                    'cta_text': 'Не нашли ответ на свой вопрос?',
                    'cta_button': 'Спросить в Telegram'
                },
                'footer': {
                    'description': 'Aaadvisor — профессиональный инструмент для анализа недвижимости. Помогаем риэлторам закрывать больше сделок с помощью точной аналитики и прогнозов.',
                    'info': {
                        'title': 'Информация',
                        'privacy': 'Политика конфиденциальности',
                        'terms': 'Условия использования',
                        'legal': 'Юридическая информация'
                    },
                    'support': {
                        'title': 'Поддержка',
                        'telegram': 'Telegram канал',
                        'feedback': 'Отзывы и предложения',
                        'help': 'Помощь'
                    }
                }
            },
            'en': {
                'common': {
                    'loading': 'Loading...', 'error': 'Error', 'success': 'Success',
                    'cancel': 'Cancel', 'confirm': 'Confirm', 'back': 'Back',
                    'next': 'Next', 'save': 'Save', 'edit': 'Edit', 'delete': 'Delete',
                    'search': 'Search', 'filter': 'Filter', 'sort': 'Sort', 'refresh': 'Refresh',
                    'close': 'Close', 'yes': 'Yes', 'no': 'No', 'ok': 'OK', 'copy': 'Copy',
                    'download': 'Download', 'share': 'Share', 'print': 'Print',
                    'export': 'Export', 'import': 'Import', 'settings': 'Settings',
                    'profile': 'Profile', 'logout': 'Logout', 'login': 'Login',
                    'register': 'Register', 'help': 'Help', 'support': 'Support',
                    'about': 'About', 'contact': 'Contact', 'privacy': 'Privacy',
                    'terms': 'Terms', 'language': 'Language', 'currency': 'Currency',
                    'timezone': 'Timezone', 'notifications': 'Notifications',
                    'dark_mode': 'Dark Mode', 'light_mode': 'Light Mode',
                    'about_app': 'About App',
                    'instruction': 'Instruction',
                    'our_geography': 'Our Geography',
                    'technical_support': 'Technical Support',
                    'about_app_title': 'About App',
                    'about_app_what_is': 'What is Aaadviser?',
                    'about_app_description': 'Aaadviser is an intelligent real estate market analysis platform that helps investors and buyers make informed decisions.',
                    'about_app_capabilities': 'Our capabilities:',
                    'about_app_capability1': 'Detailed price analysis in the area',
                    'about_app_capability2': 'Real estate market statistics',
                    'about_app_capability3': 'Comparison with similar properties',
                    'about_app_capability4': 'Price change forecast',
                    'about_app_capability5': 'Investment recommendations',
                    'about_app_capability6': 'Report saving',
                    'about_app_capability7': 'Convenient mobile interface',
                    'about_app_how_works': 'How does it work?',
                    'about_app_how_works_desc': 'Simply enter the property address, specify the number of bedrooms and approximate price. Our system will analyze the market and provide a detailed report with recommendations.',
                    'about_app_why': 'Why Aaadviser?',
                    'about_app_why_desc': 'We use advanced machine learning technologies and big data for real estate market analysis, which allows us to obtain accurate and up-to-date data for making investment decisions.',
                    'about_app_back': '← Back',
                    'about_app_main_menu': 'To main menu'
                },
                'profile': {
                    'title': 'Profile', 'personal_info': 'Personal Information',
                    'first_name': 'First Name', 'last_name': 'Last Name', 'email': 'Email',
                    'phone': 'Phone', 'telegram': 'Telegram', 'balance': 'Balance',
                    'balance_amount': 'Balance: $', 'top_up': 'Top Up', 'withdraw': 'Withdraw',
                    'transaction_history': 'Transaction History', 'referral_program': 'Referral Program',
                    'edit_profile': 'Edit Profile', 'language_settings': 'Language Settings',
                    'notification_settings': 'Notification Settings', 'security_settings': 'Security Settings',
                    'account_info': 'Account Information', 'user_id': 'User ID',
                    'registration_date': 'Registration Date', 'last_login': 'Last Login',
                    'status': 'Status', 'admin': 'Administrator', 'user': 'User',
                    'premium': 'Premium', 'free': 'Free', 'change_password': 'Change Password',
                    'delete_account': 'Delete Account', 'save_changes': 'Save Changes',
                    'changes_saved': 'Changes Saved', 'error_saving': 'Error Saving',
                    'profile_updated': 'Profile Updated', 'password_changed': 'Password Changed',
                    'account_deleted': 'Account Deleted'
                },
                'balance': {
                    'title': 'Balance', 'current_balance': 'Current Balance',
                    'top_up_balance': 'Top Up Balance', 'withdraw_funds': 'Withdraw Funds',
                    'transaction_history': 'Transaction History', 'amount': 'Amount', 'date': 'Date',
                    'type': 'Type', 'status': 'Status', 'description': 'Description', 'income': 'Income',
                    'expense': 'Expense', 'pending': 'Pending', 'completed': 'Completed',
                    'failed': 'Failed', 'payment_method': 'Payment Method', 'card': 'Card',
                    'bank_transfer': 'Bank Transfer', 'crypto': 'Cryptocurrency',
                    'min_amount': 'Minimum Amount', 'max_amount': 'Maximum Amount',
                    'fee': 'Fee', 'total': 'Total'
                },
                'reports': {
                    'title': 'Reports', 'my_reports': 'My Reports', 'create_report': 'Create Report',
                    'report_details': 'Report Details', 'report_type': 'Report Type',
                    'property_evaluation': 'Property Evaluation', 'market_analysis': 'Market Analysis',
                    'investment_analysis': 'Investment Analysis', 'region_analytics': 'Region Analytics',
                    'full_report': 'Full Report', 'report_date': 'Report Date',
                    'property_address': 'Property Address', 'property_type': 'Property Type',
                    'property_area': 'Area', 'property_price': 'Price', 'market_value': 'Market Value',
                    'investment_potential': 'Investment Potential', 'risk_level': 'Risk Level',
                    'recommendations': 'Recommendations', 'download_report': 'Download Report',
                    'share_report': 'Share Report', 'delete_report': 'Delete Report',
                    'edit_report': 'Edit Report', 'save_report': 'Save Report',
                    'report_saved': 'Report Saved', 'report_deleted': 'Report Deleted',
                    'report_shared': 'Report Shared', 'liquidity': 'Liquidity',
                    'page_description': 'Get a detailed analysis of the real estate market in the selected region',
                    'country_label': 'Country:',
                    'city_label': 'City:',
                    'county_label': 'Region/Area:',
                    'district_label': 'District:',
                    'country_placeholder': 'Select country',
                    'city_placeholder': 'First select country',
                    'county_placeholder': 'First select city',
                    'district_placeholder': 'First select region',
                    'confirm_selection': 'Confirm selection',
                    'back_to_main': '← Back to main menu',
                    'selected_location': 'Selected location:',
                    'admin_ids': 'IDs for admins:',
                    'loading': 'Loading...',
                    'error_loading': 'Error loading data',
                    'data_section_title': 'Regional Data Analysis',
                    'general_data_title': 'General Data',
                    'house_type_data_title': 'Bedroom Count Data',
                    'floor_segment_data_title': 'Floor Data',
                    'age_data_title': 'Age Data',
                    'heating_data_title': 'Heating Type Data',
                    'loading_text': 'Loading data...',
                    'error_text': 'Error loading data',
                    'total_properties': 'Total properties:',
                    'average_price': 'Average price:',
                    'price_range': 'Price range:',
                    'no_data_available': 'Data not available',
                    'key_metrics_title': 'Key Metrics',
                    'avg_sale_price_label': 'Average Sale Price per m²',
                    'avg_rent_price_label': 'Average Rent Price per m²',
                    'listing_period_sale_label': 'Listing Period (Sale)',
                    'listing_period_rent_label': 'Listing Period (Rent)',
                    'yield_label': 'Yield (Return)',
                    'insights_title': 'Summary',
                    'insights_loading': 'Analyzing data...',
                    'insights_error': 'Error analyzing data',
                    'object_evaluation_title': 'Object Evaluation',
                    'object_evaluation_description': 'Get a professional evaluation of real estate value in the selected region',
                    'listing_type_title': 'Select property type for analysis:',
                    'house_type_subtitle': 'Number of bedrooms:',
                    'floor_segment_subtitle': 'Floor:',
                    'age_data_subtitle': 'Object age:',
                    'heating_data_subtitle': 'Heating type:',
                    'price_object_subtitle': 'Object price:',
                    'area_object_subtitle': 'Object area (m²):',
                    'select_bedrooms': 'number of bedrooms',
                    'select_floor': 'floor',
                    'select_age': 'object age',
                    'select_heating': 'heating type',
                    'property_types_title': 'Selected property characteristics:',
                    'bedrooms_label': 'Number of bedrooms',
                    'floor_label': 'Floor',
                    'age_label': 'Object age',
                    'heating_label': 'Heating type',
                    'market_indicators_title': 'Market indicators',
                    'market_trends_title': 'Market trends',
                    'sale_header': 'Sale',
                    'rent_header': 'Rent',
                    'currency_title': 'Select currency:',
                    'save_share_button_text': 'Save and share report',
                    'modal_title': 'Report saved',
                    'modal_description': 'Your report has been successfully saved. You can copy the link and share it with others.',
                    'copy_button_text': 'Copy link',
                    'close_button_text': 'Close',
                    'link_copied': 'Link copied!',
                    'saving_report': 'Saving report...',
                    'error_saving': 'Error saving report',
                    'price_placeholder': 'Enter price',
                    'area_placeholder': 'Enter area',
                    'trends_filter_info': 'Showing ${filteredCount} of ${totalCount} trends',
                    'market_comparison_title': 'Market comparison',
                    'price_per_m2_label': 'Price per m²',
                    'area_label': 'Area',
                    'price_comparison_label': 'Price per m²:',
                    'area_comparison_label': 'Area:',
                    'price_close_to_market': 'Your object (${userPrice}) is close to market (${marketMin} – ${marketMax}).',
                    'price_above_market': 'Your object (${userPrice}) is ${percent}% above market.',
                    'price_below_market': 'Your object (${userPrice}) is ${percent}% below market.',
                    'area_matches_market': 'Your object (${userArea} m²) matches market demand (${marketMin}–${marketMax} m²).',
                    'area_below_market': 'Your object (${userArea} m²) is smaller than market demand (${marketMin}–${marketMax} m²).',
                    'area_above_market': 'Your object (${userArea} m²) is larger than market demand (${marketMin}–${marketMax} m²).',
                    'consolidated_assessment_title': 'Consolidated assessment',
                    'sale_price_title': 'Price per m² (Unit Price For Sale):',
                    'rent_price_title': 'Rent price per m² (Unit Price For Rent):',
                    'yield_title': 'Yield:',
                    'consolidated_average_label': 'Consolidated average:',
                    'indicator_label': 'Indicator',
                    'min_value_label': 'Minimum value',
                    'max_value_label': 'Maximum value',
                    'avg_value_label': 'Average value',
                    'count_label': 'Count',
                    'percentage_label': 'Percentage',
                    'my_reports_title': 'My Reports',
                    'my_reports_subtitle': 'Manage your reports',
                    'my_reports_loading': 'Loading reports...',
                    'my_reports_empty_title': 'No reports found',
                    'my_reports_empty_description': 'You don\'t have any saved reports yet. Create your first report in the main menu.',
                    'my_reports_back_btn': 'Back to main menu',
                    'my_reports_view_report': 'View',
                    'my_reports_delete_report': 'Delete',
                    'my_reports_copy_link': 'Copy link',
                    'my_reports_delete_modal_title': 'Confirm deletion',
                    'my_reports_delete_modal_message': 'Are you sure you want to delete this report? This action cannot be undone.',
                    'my_reports_cancel_delete_btn': 'Cancel',
                    'my_reports_confirm_delete_btn': 'Delete',
                    'my_reports_link_copied': 'Link copied to clipboard',
                    'my_reports_report_deleted': 'Report successfully deleted',
                    'my_reports_error_loading': 'Error loading reports',
                    'my_reports_error_deleting': 'Error deleting report',
                    'my_reports_no_address': 'Address not specified',
                    'my_reports_no_price': 'Price not specified',
                    'my_reports_no_area': 'Area not specified',
                    'my_reports_no_bedrooms': 'Bedrooms not specified',
                    'my_reports_property_evaluation': 'Object Evaluation',
                    'my_reports_property_analysis': 'Object Analysis',
                    'my_reports_market_analysis': 'Market Analysis'
                },
                'main': {
                    'title': 'Main Menu', 'welcome': 'Welcome',
                    'quick_actions': 'Quick Actions', 'recent_reports': 'Recent Reports',
                    'popular_services': 'Popular Services', 'news': 'News',
                    'notifications': 'Notifications', 'menu': 'Menu', 'home': 'Home',
                    'reports': 'Reports', 'analytics': 'Analytics', 'profile': 'Profile',
                    'help': 'Help', 'settings': 'Settings'
                },
                'admin': {
                    'title': 'Admin Panel', 'users': 'Users', 'publications': 'Publications',
                    'settings': 'Settings', 'statistics': 'Statistics', 'user_management': 'User Management',
                    'content_management': 'Content Management', 'system_settings': 'System Settings',
                    'backup': 'Backup', 'logs': 'Logs', 'security': 'Security'
                },
                'hero': {
                    'title': 'Close More Deals with Aaadvisor',
                    'subtitle': 'Professional real estate analytics for realtors. Show your client exact numbers and growth forecasts.',
                    'feature1': 'Market Analytics',
                    'feature2': 'Yield Calculation',
                    'feature3': 'Price Forecast',
                    'cta': 'Get Free Report',
                    'note': 'Free • No Registration • Instant'
                },
                'preview': {
                    'price': 'Price',
                    'growth': 'Annual Growth',
                    'yield': 'Yield'
                },
                'benefits': {
                    'title': 'Why Realtors Choose Aaadvisor',
                    'subtitle': 'A tool that helps close deals faster and with greater trust',
                    'card1': {
                        'title': 'Show Your Client Numbers',
                        'desc': 'Accurate market analytics with specific numbers instead of general phrases'
                    },
                    'card2': {
                        'title': 'Convince with Benefits',
                        'desc': 'Justified arguments with yield calculation and growth forecast'
                    },
                    'card3': {
                        'title': 'Growth Forecast',
                        'desc': 'Show your client the potential for real estate investment growth'
                    },
                    'card4': {
                        'title': 'Rental Yield',
                        'desc': 'Profitability calculation for investors and landlords'
                    },
                    'card5': {
                        'title': 'Close Deals Faster',
                        'desc': 'Professional reports increase trust and speed up decisions'
                    },
                    'card6': {
                        'title': 'Instant Results',
                        'desc': 'Report ready in 1 minute, no waiting or complex procedures'
                    }
                },
                'report': {
                    'title': 'What Your Client Will See',
                    'subtitle': 'Professional report with market analysis, growth forecast and yield calculation',
                    'feature1': 'Real Estate Market Analysis',
                    'feature2': 'Price Growth Forecast for 1-3 Years',
                    'feature3': 'Rental Yield Calculation',
                    'feature4': 'Comparison with Similar Properties',
                    'feature5': 'Investment Recommendations',
                    'cta': 'Create Same Report'
                },
                'comparison': {
                    'title': 'Before and After Aaadvisor',
                    'before': {
                        'title': 'Before',
                        'item1': 'You explain verbally, client doubts',
                        'item2': 'No specific numbers and justifications',
                        'item3': 'Deal is postponed indefinitely',
                        'item4': 'Client looks for alternatives'
                    },
                    'after': {
                        'title': 'After',
                        'item1': 'You show professional report with numbers',
                        'item2': 'Client sees growth forecast and yield',
                        'item3': 'Decision is made faster',
                        'item4': 'Trust in you as an expert increases'
                    }
                },
                'social': {
                    'title': 'Realtors Trust Us',
                    'stats': {
                        'objects': 'Properties Analyzed',
                        'realtors': 'Realtors Using',
                        'faster': 'Faster Deal Closing'
                    },
                    'testimonial1': {
                        'text': '"Now I show clients exact numbers and forecasts. Deals close 2 times faster, and client trust has grown significantly."',
                        'name': 'Anna Petrova',
                        'position': 'Realtor, Barcelona'
                    },
                    'testimonial2': {
                        'text': '"Aaadvisor helps justify the price objectively. Clients see that we don\'t just sell, but provide professional consultation."',
                        'name': 'Sergey Ivanov',
                        'position': 'Real Estate Agency, Lisbon'
                    }
                },
                'cta': {
                    'title': 'Show Your Client the Deal Benefits Today',
                    'subtitle': 'Get a professional report in 1 minute',
                    'feature1': 'Free in test mode',
                    'feature2': 'Instant results',
                    'feature3': 'Works in Telegram',
                    'button': 'Launch in Telegram',
                    'note': 'No Registration • No Limits • Ready to Use'
                },
                'faq': {
                    'title': 'Frequently Asked Questions',
                    'subtitle': 'Answers to the most popular questions about Aaadvisor',
                    'q1': 'How does Aaadvisor work?',
                    'a1': 'Aaadvisor is a Telegram bot that analyzes real estate in Turkey, Spain and Portugal. Simply send the property address, and the bot will create a professional report with market analysis, growth forecast and yield calculation.',
                    'q2': 'What data does Aaadvisor analyze?',
                    'a2': 'The bot analyzes current real estate prices, historical price dynamics, market trends, rental yield, comparison with similar properties and growth forecast for 1-3 years.',
                    'q3': 'How much does it cost to use?',
                    'a3': 'Currently Aaadvisor is available for free in test mode. You can get unlimited reports without registration and without restrictions.',
                    'q4': 'In which countries does Aaadvisor work?',
                    'a4': 'Currently Aaadvisor works with real estate in Turkey, Spain and Portugal. We are constantly expanding geography and adding new markets.',
                    'q5': 'How accurate are the forecasts?',
                    'a5': 'Forecasts are based on analysis of historical data, economic indicators and market trends. Accuracy is 85-90% for short-term forecasts (1 year) and 70-80% for long-term (3 years).',
                    'q6': 'Can I use reports for clients?',
                    'a6': 'Yes! Aaadvisor reports are designed specifically for working with clients. They contain professional analytics that can be shown to buyers to justify price and potential investment benefits.',
                    'q7': 'How often is data updated?',
                    'a7': 'Data is updated weekly. We track price changes, new listings and market trends to ensure information relevance in reports.',
                    'q8': 'What to do if the bot doesn\'t respond?',
                    'a8': 'If you have problems with the bot, contact our support through Telegram channel @Aaadviser_support. We usually respond within 1-2 hours during business hours.',
                    'cta_text': 'Didn\'t find an answer to your question?',
                    'cta_button': 'Ask in Telegram'
                },
                'footer': {
                    'description': 'Aaadvisor is a professional real estate analysis tool. We help realtors close more deals with accurate analytics and forecasts.',
                    'info': {
                        'title': 'Information',
                        'privacy': 'Privacy Policy',
                        'terms': 'Terms of Use',
                        'legal': 'Legal Information'
                    },
                    'support': {
                        'title': 'Support',
                        'telegram': 'Telegram Channel',
                        'feedback': 'Feedback and Suggestions',
                        'help': 'Help'
                    }
                }
            },
            'de': {
                'common': {
                    'loading': 'Laden...', 'error': 'Fehler', 'success': 'Erfolg',
                    'cancel': 'Abbrechen', 'confirm': 'Bestätigen', 'back': 'Zurück',
                    'next': 'Weiter', 'save': 'Speichern', 'edit': 'Bearbeiten',
                    'delete': 'Löschen', 'search': 'Suchen', 'filter': 'Filter',
                    'sort': 'Sortieren', 'refresh': 'Aktualisieren', 'close': 'Schließen',
                    'yes': 'Ja', 'no': 'Nein', 'ok': 'OK', 'copy': 'Kopieren',
                    'download': 'Herunterladen', 'share': 'Teilen', 'print': 'Drucken',
                    'export': 'Exportieren', 'import': 'Importieren', 'settings': 'Einstellungen',
                    'profile': 'Profil', 'logout': 'Abmelden', 'login': 'Anmelden',
                    'register': 'Registrieren', 'help': 'Hilfe', 'support': 'Support',
                    'about': 'Über uns', 'contact': 'Kontakt', 'privacy': 'Datenschutz',
                    'terms': 'Bedingungen', 'language': 'Sprache', 'currency': 'Währung',
                    'timezone': 'Zeitzone', 'notifications': 'Benachrichtigungen',
                    'dark_mode': 'Dunkler Modus', 'light_mode': 'Heller Modus',
                    'about_app': 'Über die App',
                    'instruction': 'Anleitung',
                    'our_geography': 'Unsere Geographie',
                    'technical_support': 'Technischer Support',
                    'about_app_title': 'Über die App',
                    'about_app_what_is': 'Was ist Aaadviser?',
                    'about_app_description': 'Aaadviser ist eine intelligente Plattform zur Analyse des Immobilienmarkts, die Investoren und Käufern hilft, fundierte Entscheidungen zu treffen.',
                    'about_app_capabilities': 'Unsere Fähigkeiten:',
                    'about_app_capability1': 'Detaillierte Preisanalyse in der Gegend',
                    'about_app_capability2': 'Immobilienmarktstatistiken',
                    'about_app_capability3': 'Vergleich mit ähnlichen Immobilien',
                    'about_app_capability4': 'Preisänderungsprognose',
                    'about_app_capability5': 'Anlageempfehlungen',
                    'about_app_capability6': 'Berichtsspeicherung',
                    'about_app_capability7': 'Bequeme mobile Oberfläche',
                    'about_app_how_works': 'Wie funktioniert es?',
                    'about_app_how_works_desc': 'Geben Sie einfach die Immobilienadresse ein, geben Sie die Anzahl der Schlafzimmer und den ungefähren Preis an. Unser System analysiert den Markt und erstellt einen detaillierten Bericht mit Empfehlungen.',
                    'about_app_why': 'Warum Aaadviser?',
                    'about_app_why_desc': 'Wir verwenden fortschrittliche Machine-Learning-Technologien und Big Data für die Immobilienmarktanalyse, was es uns ermöglicht, genaue und aktuelle Daten für Anlageentscheidungen zu erhalten.',
                    'about_app_back': '← Zurück',
                    'about_app_main_menu': 'Zum Hauptmenü'
                },
                'profile': {
                    'title': 'Profil', 'personal_info': 'Persönliche Informationen',
                    'first_name': 'Vorname', 'last_name': 'Nachname', 'email': 'E-Mail',
                    'phone': 'Telefon', 'telegram': 'Telegram', 'balance': 'Kontostand',
                    'balance_amount': 'Kontostand: $', 'top_up': 'Aufladen', 'withdraw': 'Abheben',
                    'transaction_history': 'Transaktionsverlauf', 'referral_program': 'Empfehlungsprogramm',
                    'edit_profile': 'Profil bearbeiten', 'language_settings': 'Spracheinstellungen',
                    'notification_settings': 'Benachrichtigungseinstellungen', 'security_settings': 'Sicherheitseinstellungen',
                    'account_info': 'Kontoinformationen', 'user_id': 'Benutzer-ID',
                    'registration_date': 'Registrierungsdatum', 'last_login': 'Letzter Login',
                    'status': 'Status', 'admin': 'Administrator', 'user': 'Benutzer',
                    'premium': 'Premium', 'free': 'Kostenlos', 'change_password': 'Passwort ändern',
                    'delete_account': 'Konto löschen', 'save_changes': 'Änderungen speichern',
                    'changes_saved': 'Änderungen gespeichert', 'error_saving': 'Fehler beim Speichern',
                    'profile_updated': 'Profil aktualisiert', 'password_changed': 'Passwort geändert',
                    'account_deleted': 'Konto gelöscht'
                },
                'balance': {
                    'title': 'Kontostand', 'current_balance': 'Aktueller Kontostand',
                    'top_up_balance': 'Kontostand aufladen', 'withdraw_funds': 'Geld abheben',
                    'transaction_history': 'Transaktionsverlauf', 'amount': 'Betrag', 'date': 'Datum',
                    'type': 'Typ', 'status': 'Status', 'description': 'Beschreibung', 'income': 'Einnahmen',
                    'expense': 'Ausgaben', 'pending': 'Ausstehend', 'completed': 'Abgeschlossen',
                    'failed': 'Fehlgeschlagen', 'payment_method': 'Zahlungsmethode', 'card': 'Karte',
                    'bank_transfer': 'Banküberweisung', 'crypto': 'Kryptowährung',
                    'min_amount': 'Mindestbetrag', 'max_amount': 'Höchstbetrag',
                    'fee': 'Gebühr', 'total': 'Gesamt'
                },
                'reports': {
                    'title': 'Berichte', 'my_reports': 'Meine Berichte', 'create_report': 'Bericht erstellen',
                    'report_details': 'Berichtsdetails', 'report_type': 'Berichtstyp',
                    'property_evaluation': 'Immobilienbewertung', 'market_analysis': 'Marktanalyse',
                    'investment_analysis': 'Investitionsanalyse', 'region_analytics': 'Regionsanalytik',
                    'full_report': 'Vollständiger Bericht', 'report_date': 'Berichtsdatum',
                    'property_address': 'Immobilienadresse', 'property_type': 'Immobilientyp',
                    'property_area': 'Fläche', 'property_price': 'Preis', 'market_value': 'Marktwert',
                    'investment_potential': 'Investitionspotenzial', 'risk_level': 'Risikolevel',
                    'recommendations': 'Empfehlungen', 'download_report': 'Bericht herunterladen',
                    'share_report': 'Bericht teilen', 'delete_report': 'Bericht löschen',
                    'edit_report': 'Bericht bearbeiten', 'save_report': 'Bericht speichern',
                    'report_saved': 'Bericht gespeichert', 'report_deleted': 'Bericht gelöscht',
                    'report_shared': 'Bericht geteilt', 'liquidity': 'Liquidität',
                    'page_description': 'Erhalten Sie eine detaillierte Analyse des Immobilienmarkts in der ausgewählten Region',
                    'country_label': 'Land:',
                    'city_label': 'Stadt:',
                    'county_label': 'Region/Bereich:',
                    'district_label': 'Bezirk:',
                    'country_placeholder': 'Land auswählen',
                    'city_placeholder': 'Zuerst Land auswählen',
                    'county_placeholder': 'Zuerst Stadt auswählen',
                    'district_placeholder': 'Zuerst Region auswählen',
                    'confirm_selection': 'Auswahl bestätigen',
                    'back_to_main': '← Zurück zum Hauptmenü',
                    'selected_location': 'Ausgewählte Lage:',
                    'admin_ids': 'IDs für Administratoren:',
                    'loading': 'Laden...',
                    'error_loading': 'Fehler beim Laden der Daten',
                    'data_section_title': 'Regionale Datenanalyse',
                    'general_data_title': 'Allgemeine Daten',
                    'house_type_data_title': 'Schlafzimmer-Anzahl-Daten',
                    'floor_segment_data_title': 'Etagen-Daten',
                    'age_data_title': 'Altersdaten',
                    'heating_data_title': 'Heizungstyp-Daten',
                    'loading_text': 'Daten werden geladen...',
                    'error_text': 'Fehler beim Laden der Daten',
                    'total_properties': 'Gesamtobjekte:',
                    'average_price': 'Durchschnittspreis:',
                    'price_range': 'Preisbereich:',
                    'no_data_available': 'Daten nicht verfügbar',
                    'key_metrics_title': 'Wichtige Kennzahlen',
                    'avg_sale_price_label': 'Durchschnittlicher Verkaufspreis pro m²',
                    'avg_rent_price_label': 'Durchschnittlicher Mietpreis pro m²',
                    'listing_period_sale_label': 'Angebotsdauer (Verkauf)',
                    'listing_period_rent_label': 'Angebotsdauer (Vermietung)',
                    'yield_label': 'Yield (Rendite)',
                    'insights_title': 'Zusammenfassung',
                    'insights_loading': 'Daten werden analysiert...',
                    'insights_error': 'Fehler bei der Datenanalyse',
                    'object_evaluation_title': 'Objektbewertung',
                    'object_evaluation_description': 'Erhalten Sie eine professionelle Bewertung des Immobilienwerts in der ausgewählten Region',
                    'listing_type_title': 'Wählen Sie den Immobilientyp für die Analyse:',
                    'house_type_subtitle': 'Anzahl der Schlafzimmer:',
                    'floor_segment_subtitle': 'Etage:',
                    'age_data_subtitle': 'Objektalter:',
                    'heating_data_subtitle': 'Heizungstyp:',
                    'price_object_subtitle': 'Objektpreis:',
                    'area_object_subtitle': 'Objektfläche (m²):',
                    'select_bedrooms': 'Anzahl der Schlafzimmer',
                    'select_floor': 'Etage',
                    'select_age': 'Objektalter',
                    'select_heating': 'Heizungstyp',
                    'property_types_title': 'Ausgewählte Immobilienmerkmale:',
                    'bedrooms_label': 'Anzahl der Schlafzimmer',
                    'floor_label': 'Etage',
                    'age_label': 'Objektalter',
                    'heating_label': 'Heizungstyp',
                    'market_indicators_title': 'Marktindikatoren',
                    'market_trends_title': 'Markttrends',
                    'sale_header': 'Verkauf',
                    'rent_header': 'Vermietung',
                    'currency_title': 'Währung auswählen:',
                    'save_share_button_text': 'Bericht speichern und teilen',
                    'modal_title': 'Bericht gespeichert',
                    'modal_description': 'Ihr Bericht wurde erfolgreich gespeichert. Sie können den Link kopieren und mit anderen teilen.',
                    'copy_button_text': 'Link kopieren',
                    'close_button_text': 'Schließen',
                    'link_copied': 'Link kopiert!',
                    'saving_report': 'Bericht wird gespeichert...',
                    'error_saving': 'Fehler beim Speichern des Berichts',
                    'price_placeholder': 'Preis eingeben',
                    'area_placeholder': 'Fläche eingeben',
                    'trends_filter_info': 'Zeige ${filteredCount} von ${totalCount} Trends',
                    'market_comparison_title': 'Marktvergleich',
                    'price_per_m2_label': 'Preis pro m²',
                    'area_label': 'Fläche',
                    'price_comparison_label': 'Preis pro m²:',
                    'area_comparison_label': 'Fläche:',
                    'price_close_to_market': 'Ihr Objekt (${userPrice}) liegt nahe am Markt (${marketMin} – ${marketMax}).',
                    'price_above_market': 'Ihr Objekt (${userPrice}) liegt ${percent}% über dem Markt.',
                    'price_below_market': 'Ihr Objekt (${userPrice}) liegt ${percent}% unter dem Markt.',
                    'area_matches_market': 'Ihr Objekt (${userArea} m²) entspricht der Marktnachfrage (${marketMin}–${marketMax} m²).',
                    'area_below_market': 'Ihr Objekt (${userArea} m²) ist kleiner als die Marktnachfrage (${marketMin}–${marketMax} m²).',
                    'area_above_market': 'Ihr Objekt (${userArea} m²) ist größer als die Marktnachfrage (${marketMin}–${marketMax} m²).',
                    'consolidated_assessment_title': 'Konsolidierte Bewertung',
                    'sale_price_title': 'Preis pro m² (Unit Price For Sale):',
                    'rent_price_title': 'Mietpreis pro m² (Unit Price For Rent):',
                    'yield_title': 'Rendite:',
                    'consolidated_average_label': 'Konsolidierter Durchschnitt:',
                    'indicator_label': 'Indikator',
                    'min_value_label': 'Mindestwert',
                    'max_value_label': 'Maximalwert',
                    'avg_value_label': 'Durchschnittswert',
                    'count_label': 'Anzahl',
                    'percentage_label': 'Prozentsatz',
                    'my_reports_title': 'Meine Berichte',
                    'my_reports_subtitle': 'Verwalten Sie Ihre Berichte',
                    'my_reports_loading': 'Berichte werden geladen...',
                    'my_reports_empty_title': 'Keine Berichte gefunden',
                    'my_reports_empty_description': 'Sie haben noch keine gespeicherten Berichte. Erstellen Sie Ihren ersten Bericht im Hauptmenü.',
                    'my_reports_back_btn': 'Zurück zum Hauptmenü',
                    'my_reports_view_report': 'Anzeigen',
                    'my_reports_delete_report': 'Löschen',
                    'my_reports_copy_link': 'Link kopieren',
                    'my_reports_delete_modal_title': 'Löschung bestätigen',
                    'my_reports_delete_modal_message': 'Sind Sie sicher, dass Sie diesen Bericht löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.',
                    'my_reports_cancel_delete_btn': 'Abbrechen',
                    'my_reports_confirm_delete_btn': 'Löschen',
                    'my_reports_link_copied': 'Link in die Zwischenablage kopiert',
                    'my_reports_report_deleted': 'Bericht erfolgreich gelöscht',
                    'my_reports_error_loading': 'Fehler beim Laden der Berichte',
                    'my_reports_error_deleting': 'Fehler beim Löschen des Berichts',
                    'my_reports_no_address': 'Adresse nicht angegeben',
                    'my_reports_no_price': 'Preis nicht angegeben',
                    'my_reports_no_area': 'Fläche nicht angegeben',
                    'my_reports_no_bedrooms': 'Schlafzimmer nicht angegeben',
                    'my_reports_property_evaluation': 'Objektbewertung',
                    'my_reports_property_analysis': 'Objektanalyse',
                    'my_reports_market_analysis': 'Marktanalyse'
                },
                'main': {
                    'title': 'Hauptmenü', 'welcome': 'Willkommen',
                    'quick_actions': 'Schnellaktionen', 'recent_reports': 'Letzte Berichte',
                    'popular_services': 'Beliebte Dienste', 'news': 'Nachrichten',
                    'notifications': 'Benachrichtigungen', 'menu': 'Menü', 'home': 'Startseite',
                    'reports': 'Berichte', 'analytics': 'Analytik', 'profile': 'Profil',
                    'help': 'Hilfe', 'settings': 'Einstellungen'
                },
                'admin': {
                    'title': 'Admin-Panel', 'users': 'Benutzer', 'publications': 'Veröffentlichungen',
                    'settings': 'Einstellungen', 'statistics': 'Statistiken', 'user_management': 'Benutzerverwaltung',
                    'content_management': 'Inhaltsverwaltung', 'system_settings': 'Systemeinstellungen',
                    'backup': 'Backup', 'logs': 'Protokolle', 'security': 'Sicherheit'
                }
            },
            'fr': {
                'common': {
                    'loading': 'Chargement...', 'error': 'Erreur', 'success': 'Succès',
                    'cancel': 'Annuler', 'confirm': 'Confirmer', 'back': 'Retour',
                    'next': 'Suivant', 'save': 'Enregistrer', 'edit': 'Modifier',
                    'delete': 'Supprimer', 'search': 'Rechercher', 'filter': 'Filtrer',
                    'sort': 'Trier', 'refresh': 'Actualiser', 'close': 'Fermer',
                    'yes': 'Oui', 'no': 'Non', 'ok': 'OK', 'copy': 'Copier',
                    'download': 'Télécharger', 'share': 'Partager', 'print': 'Imprimer',
                    'export': 'Exporter', 'import': 'Importer', 'settings': 'Paramètres',
                    'profile': 'Profil', 'logout': 'Déconnexion', 'login': 'Connexion',
                    'register': 'S\'inscrire', 'help': 'Aide', 'support': 'Support',
                    'about': 'À propos', 'contact': 'Contact', 'privacy': 'Confidentialité',
                    'terms': 'Conditions', 'language': 'Langue', 'currency': 'Devise',
                    'timezone': 'Fuseau horaire', 'notifications': 'Notifications',
                    'dark_mode': 'Mode sombre', 'light_mode': 'Mode clair',
                    'about_app': 'À propos de l\'app',
                    'instruction': 'Instruction',
                    'our_geography': 'Notre géographie',
                    'technical_support': 'Support technique',
                    'about_app_title': 'À propos de l\'app',
                    'about_app_what_is': 'Qu\'est-ce qu\'Aaadviser?',
                    'about_app_description': 'Aaadviser est une plateforme intelligente d\'analyse du marché immobilier qui aide les investisseurs et les acheteurs à prendre des décisions éclairées.',
                    'about_app_capabilities': 'Nos capacités:',
                    'about_app_capability1': 'Analyse détaillée des prix dans la zone',
                    'about_app_capability2': 'Statistiques du marché immobilier',
                    'about_app_capability3': 'Comparaison avec des propriétés similaires',
                    'about_app_capability4': 'Prévision des changements de prix',
                    'about_app_capability5': 'Recommandations d\'investissement',
                    'about_app_capability6': 'Sauvegarde des rapports',
                    'about_app_capability7': 'Interface mobile pratique',
                    'about_app_how_works': 'Comment ça marche?',
                    'about_app_how_works_desc': 'Entrez simplement l\'adresse de la propriété, spécifiez le nombre de chambres et le prix approximatif. Notre système analysera le marché et fournira un rapport détaillé avec des recommandations.',
                    'about_app_why': 'Pourquoi Aaadviser?',
                    'about_app_why_desc': 'Nous utilisons des technologies avancées d\'apprentissage automatique et du big data pour l\'analyse du marché immobilier, ce qui nous permet d\'obtenir des données précises et à jour pour prendre des décisions d\'investissement.',
                    'about_app_back': '← Retour',
                    'about_app_main_menu': 'Au menu principal'
                },
                'profile': {
                    'title': 'Profil', 'personal_info': 'Informations personnelles',
                    'first_name': 'Prénom', 'last_name': 'Nom', 'email': 'E-mail',
                    'phone': 'Téléphone', 'telegram': 'Telegram', 'balance': 'Solde',
                    'balance_amount': 'Solde: $', 'top_up': 'Recharger', 'withdraw': 'Retirer',
                    'transaction_history': 'Historique des transactions', 'referral_program': 'Programme de parrainage',
                    'edit_profile': 'Modifier le profil', 'language_settings': 'Paramètres de langue',
                    'notification_settings': 'Paramètres de notification', 'security_settings': 'Paramètres de sécurité',
                    'account_info': 'Informations du compte', 'user_id': 'ID utilisateur',
                    'registration_date': 'Date d\'inscription', 'last_login': 'Dernière connexion',
                    'status': 'Statut', 'admin': 'Administrateur', 'user': 'Utilisateur',
                    'premium': 'Premium', 'free': 'Gratuit', 'change_password': 'Changer le mot de passe',
                    'delete_account': 'Supprimer le compte', 'save_changes': 'Enregistrer les modifications',
                    'changes_saved': 'Modifications enregistrées', 'error_saving': 'Erreur lors de l\'enregistrement',
                    'profile_updated': 'Profil mis à jour', 'password_changed': 'Mot de passe changé',
                    'account_deleted': 'Compte supprimé'
                },
                'balance': {
                    'title': 'Solde', 'current_balance': 'Solde actuel',
                    'top_up_balance': 'Recharger le solde', 'withdraw_funds': 'Retirer des fonds',
                    'transaction_history': 'Historique des transactions', 'amount': 'Montant', 'date': 'Date',
                    'type': 'Type', 'status': 'Statut', 'description': 'Description', 'income': 'Revenus',
                    'expense': 'Dépenses', 'pending': 'En attente', 'completed': 'Terminé',
                    'failed': 'Échoué', 'payment_method': 'Méthode de paiement', 'card': 'Carte',
                    'bank_transfer': 'Virement bancaire', 'crypto': 'Cryptomonnaie',
                    'min_amount': 'Montant minimum', 'max_amount': 'Montant maximum',
                    'fee': 'Frais', 'total': 'Total'
                },
                'reports': {
                    'title': 'Rapports', 'my_reports': 'Mes rapports', 'create_report': 'Créer un rapport',
                    'report_details': 'Détails du rapport', 'report_type': 'Type de rapport',
                    'property_evaluation': 'Évaluation immobilière', 'market_analysis': 'Analyse de marché',
                    'investment_analysis': 'Analyse d\'investissement', 'region_analytics': 'Analytique de région',
                    'full_report': 'Rapport complet', 'report_date': 'Date du rapport',
                    'property_address': 'Adresse de la propriété', 'property_type': 'Type de propriété',
                    'property_area': 'Surface', 'property_price': 'Prix', 'market_value': 'Valeur marchande',
                    'investment_potential': 'Potentiel d\'investissement', 'risk_level': 'Niveau de risque',
                    'recommendations': 'Recommandations', 'download_report': 'Télécharger le rapport',
                    'share_report': 'Partager le rapport', 'delete_report': 'Supprimer le rapport',
                    'edit_report': 'Modifier le rapport', 'save_report': 'Enregistrer le rapport',
                    'report_saved': 'Rapport enregistré', 'report_deleted': 'Rapport supprimé',
                    'report_shared': 'Rapport partagé', 'liquidity': 'Liquidité',
                    'page_description': 'Obtenez une analyse détaillée du marché immobilier dans la région sélectionnée',
                    'country_label': 'Pays :',
                    'city_label': 'Ville :',
                    'county_label': 'Région/Zone :',
                    'district_label': 'District :',
                    'country_placeholder': 'Sélectionner un pays',
                    'city_placeholder': 'D\'abord sélectionner un pays',
                    'county_placeholder': 'D\'abord sélectionner une ville',
                    'district_placeholder': 'D\'abord sélectionner une région',
                    'confirm_selection': 'Confirmer la sélection',
                    'back_to_main': '← Retour au menu principal',
                    'selected_location': 'Emplacement sélectionné :',
                    'admin_ids': 'IDs pour les administrateurs :',
                    'loading': 'Chargement...',
                    'error_loading': 'Erreur lors du chargement des données',
                    'data_section_title': 'Analyse des données régionales',
                    'general_data_title': 'Données générales',
                    'house_type_data_title': 'Données du nombre de chambres',
                    'floor_segment_data_title': 'Données des étages',
                    'age_data_title': 'Données d\'âge',
                    'heating_data_title': 'Données du type de chauffage',
                    'loading_text': 'Chargement des données...',
                    'error_text': 'Erreur lors du chargement des données',
                    'total_properties': 'Total des propriétés :',
                    'average_price': 'Prix moyen :',
                    'price_range': 'Fourchette de prix :',
                    'no_data_available': 'Données non disponibles',
                    'key_metrics_title': 'Métriques clés',
                    'avg_sale_price_label': 'Prix de vente moyen par m²',
                    'avg_rent_price_label': 'Prix de location moyen par m²',
                    'listing_period_sale_label': 'Période d\'annonce (Vente)',
                    'listing_period_rent_label': 'Période d\'annonce (Location)',
                    'yield_label': 'Rendement (Retour)',
                    'insights_title': 'Résumé',
                    'insights_loading': 'Analyse des données...',
                    'insights_error': 'Erreur lors de l\'analyse des données',
                    'object_evaluation_title': 'Évaluation d\'objet',
                    'object_evaluation_description': 'Obtenez une évaluation professionnelle de la valeur immobilière dans la région sélectionnée',
                    'listing_type_title': 'Sélectionnez le type de propriété pour l\'analyse:',
                    'house_type_subtitle': 'Nombre de chambres:',
                    'floor_segment_subtitle': 'Étage:',
                    'age_data_subtitle': 'Âge de l\'objet:',
                    'heating_data_subtitle': 'Type de chauffage:',
                    'price_object_subtitle': 'Prix de l\'objet:',
                    'area_object_subtitle': 'Surface de l\'objet (m²):',
                    'select_bedrooms': 'nombre de chambres',
                    'select_floor': 'étage',
                    'select_age': 'âge de l\'objet',
                    'select_heating': 'type de chauffage',
                    'property_types_title': 'Caractéristiques de propriété sélectionnées:',
                    'bedrooms_label': 'Nombre de chambres',
                    'floor_label': 'Étage',
                    'age_label': 'Âge de l\'objet',
                    'heating_label': 'Type de chauffage',
                    'market_indicators_title': 'Indicateurs du marché',
                    'market_trends_title': 'Tendances du marché',
                    'sale_header': 'Vente',
                    'rent_header': 'Location',
                    'currency_title': 'Sélectionner la devise:',
                    'save_share_button_text': 'Sauvegarder et partager le rapport',
                    'modal_title': 'Rapport sauvegardé',
                    'modal_description': 'Votre rapport a été sauvegardé avec succès. Vous pouvez copier le lien et le partager avec d\'autres.',
                    'copy_button_text': 'Copier le lien',
                    'close_button_text': 'Fermer',
                    'link_copied': 'Lien copié!',
                    'saving_report': 'Sauvegarde du rapport...',
                    'error_saving': 'Erreur lors de la sauvegarde du rapport',
                    'price_placeholder': 'Entrer le prix',
                    'area_placeholder': 'Entrer la surface',
                    'trends_filter_info': 'Affichage de ${filteredCount} sur ${totalCount} tendances',
                    'market_comparison_title': 'Comparaison avec le marché',
                    'price_per_m2_label': 'Prix par m²',
                    'area_label': 'Surface',
                    'price_comparison_label': 'Prix par m²:',
                    'area_comparison_label': 'Surface:',
                    'price_close_to_market': 'Votre objet (${userPrice}) est proche du marché (${marketMin} – ${marketMax}).',
                    'price_above_market': 'Votre objet (${userPrice}) est ${percent}% au-dessus du marché.',
                    'price_below_market': 'Votre objet (${userPrice}) est ${percent}% en dessous du marché.',
                    'area_matches_market': 'Votre objet (${userArea} m²) correspond à la demande du marché (${marketMin}–${marketMax} m²).',
                    'area_below_market': 'Votre objet (${userArea} m²) est plus petit que la demande du marché (${marketMin}–${marketMax} m²).',
                    'area_above_market': 'Votre objet (${userArea} m²) est plus grand que la demande du marché (${marketMin}–${marketMax} m²).',
                    'consolidated_assessment_title': 'Évaluation consolidée',
                    'sale_price_title': 'Prix par m² (Prix unitaire pour la vente):',
                    'rent_price_title': 'Prix de location par m² (Prix unitaire pour la location):',
                    'yield_title': 'Rendement:',
                    'consolidated_average_label': 'Moyenne consolidée:',
                    'indicator_label': 'Indicateur',
                    'min_value_label': 'Valeur minimale',
                    'max_value_label': 'Valeur maximale',
                    'avg_value_label': 'Valeur moyenne',
                    'count_label': 'Nombre',
                    'percentage_label': 'Pourcentage',
                    'my_reports_title': 'Mes Rapports',
                    'my_reports_subtitle': 'Gérer vos rapports',
                    'my_reports_loading': 'Chargement des rapports...',
                    'my_reports_empty_title': 'Aucun rapport trouvé',
                    'my_reports_empty_description': 'Vous n\'avez pas encore de rapports sauvegardés. Créez votre premier rapport dans le menu principal.',
                    'my_reports_back_btn': 'Retour au menu principal',
                    'my_reports_view_report': 'Voir',
                    'my_reports_delete_report': 'Supprimer',
                    'my_reports_copy_link': 'Copier le lien',
                    'my_reports_delete_modal_title': 'Confirmer la suppression',
                    'my_reports_delete_modal_message': 'Êtes-vous sûr de vouloir supprimer ce rapport ? Cette action ne peut pas être annulée.',
                    'my_reports_cancel_delete_btn': 'Annuler',
                    'my_reports_confirm_delete_btn': 'Supprimer',
                    'my_reports_link_copied': 'Lien copié dans le presse-papiers',
                    'my_reports_report_deleted': 'Rapport supprimé avec succès',
                    'my_reports_error_loading': 'Erreur de chargement des rapports',
                    'my_reports_error_deleting': 'Erreur lors de la suppression du rapport',
                    'my_reports_no_address': 'Adresse non spécifiée',
                    'my_reports_no_price': 'Prix non spécifié',
                    'my_reports_no_area': 'Surface non spécifiée',
                    'my_reports_no_bedrooms': 'Chambres non spécifiées',
                    'my_reports_property_evaluation': 'Évaluation d\'objet',
                    'my_reports_property_analysis': 'Analyse d\'objet',
                    'my_reports_market_analysis': 'Analyse de marché'
                },
                'main': {
                    'title': 'Menu principal', 'welcome': 'Bienvenue',
                    'quick_actions': 'Actions rapides', 'recent_reports': 'Rapports récents',
                    'popular_services': 'Services populaires', 'news': 'Actualités',
                    'notifications': 'Notifications', 'menu': 'Menu', 'home': 'Accueil',
                    'reports': 'Rapports', 'analytics': 'Analytique', 'profile': 'Profil',
                    'help': 'Aide', 'settings': 'Paramètres'
                },
                'admin': {
                    'title': 'Panneau d\'administration', 'users': 'Utilisateurs', 'publications': 'Publications',
                    'settings': 'Paramètres', 'statistics': 'Statistiques', 'user_management': 'Gestion des utilisateurs',
                    'content_management': 'Gestion du contenu', 'system_settings': 'Paramètres système',
                    'backup': 'Sauvegarde', 'logs': 'Journaux', 'security': 'Sécurité'
                }
            },
            'tr': {
                'common': {
                    'loading': 'Yükleniyor...', 'error': 'Hata', 'success': 'Başarılı',
                    'cancel': 'İptal', 'confirm': 'Onayla', 'back': 'Geri',
                    'next': 'İleri', 'save': 'Kaydet', 'edit': 'Düzenle',
                    'delete': 'Sil', 'search': 'Ara', 'filter': 'Filtre',
                    'sort': 'Sırala', 'refresh': 'Yenile', 'close': 'Kapat',
                    'yes': 'Evet', 'no': 'Hayır', 'ok': 'Tamam', 'copy': 'Kopyala',
                    'download': 'İndir', 'share': 'Paylaş', 'print': 'Yazdır',
                    'export': 'Dışa aktar', 'import': 'İçe aktar', 'settings': 'Ayarlar',
                    'profile': 'Profil', 'logout': 'Çıkış', 'login': 'Giriş',
                    'register': 'Kayıt ol', 'help': 'Yardım', 'support': 'Destek',
                    'about': 'Hakkında', 'contact': 'İletişim', 'privacy': 'Gizlilik',
                    'terms': 'Şartlar', 'language': 'Dil', 'currency': 'Para birimi',
                    'timezone': 'Saat dilimi', 'notifications': 'Bildirimler',
                    'dark_mode': 'Karanlık mod', 'light_mode': 'Aydınlık mod',
                    'about_app': 'Uygulama Hakkında',
                    'instruction': 'Talimat',
                    'our_geography': 'Coğrafyamız',
                    'technical_support': 'Teknik Destek',
                    'about_app_title': 'Uygulama Hakkında',
                    'about_app_what_is': 'Aaadviser nedir?',
                    'about_app_description': 'Aaadviser, yatırımcıların ve alıcıların bilinçli kararlar almasına yardımcı olan akıllı bir emlak piyasası analiz platformudur.',
                    'about_app_capabilities': 'Yeteneklerimiz:',
                    'about_app_capability1': 'Bölgedeki detaylı fiyat analizi',
                    'about_app_capability2': 'Emlak piyasası istatistikleri',
                    'about_app_capability3': 'Benzer mülklerle karşılaştırma',
                    'about_app_capability4': 'Fiyat değişimi tahmini',
                    'about_app_capability5': 'Yatırım önerileri',
                    'about_app_capability6': 'Rapor kaydetme',
                    'about_app_capability7': 'Kullanışlı mobil arayüz',
                    'about_app_how_works': 'Nasıl çalışır?',
                    'about_app_how_works_desc': 'Sadece mülk adresini girin, yatak odası sayısını ve yaklaşık fiyatı belirtin. Sistemimiz piyasayı analiz edecek ve önerilerle birlikte detaylı bir rapor sağlayacaktır.',
                    'about_app_why': 'Neden Aaadviser?',
                    'about_app_why_desc': 'Emlak piyasası analizi için gelişmiş makine öğrenimi teknolojileri ve büyük veri kullanıyoruz, bu da yatırım kararları için doğru ve güncel veriler elde etmemizi sağlıyor.',
                    'about_app_back': '← Geri',
                    'about_app_main_menu': 'Ana menüye'
                },
                'profile': {
                    'title': 'Profil', 'personal_info': 'Kişisel bilgiler',
                    'first_name': 'Ad', 'last_name': 'Soyad', 'email': 'E-posta',
                    'phone': 'Telefon', 'telegram': 'Telegram', 'balance': 'Bakiye',
                    'balance_amount': 'Bakiye: $', 'top_up': 'Yükle', 'withdraw': 'Çek',
                    'transaction_history': 'İşlem geçmişi', 'referral_program': 'Referans programı',
                    'edit_profile': 'Profili düzenle', 'language_settings': 'Dil ayarları',
                    'notification_settings': 'Bildirim ayarları', 'security_settings': 'Güvenlik ayarları',
                    'account_info': 'Hesap bilgileri', 'user_id': 'Kullanıcı ID',
                    'registration_date': 'Kayıt tarihi', 'last_login': 'Son giriş',
                    'status': 'Durum', 'admin': 'Yönetici', 'user': 'Kullanıcı',
                    'premium': 'Premium', 'free': 'Ücretsiz', 'change_password': 'Şifre değiştir',
                    'delete_account': 'Hesabı sil', 'save_changes': 'Değişiklikleri kaydet',
                    'changes_saved': 'Değişiklikler kaydedildi', 'error_saving': 'Kaydetme hatası',
                    'profile_updated': 'Profil güncellendi', 'password_changed': 'Şifre değiştirildi',
                    'account_deleted': 'Hesap silindi'
                },
                'balance': {
                    'title': 'Bakiye', 'current_balance': 'Mevcut bakiye',
                    'top_up_balance': 'Bakiyeyi yükle', 'withdraw_funds': 'Para çek',
                    'transaction_history': 'İşlem geçmişi', 'amount': 'Tutar', 'date': 'Tarih',
                    'type': 'Tür', 'status': 'Durum', 'description': 'Açıklama', 'income': 'Gelir',
                    'expense': 'Gider', 'pending': 'Beklemede', 'completed': 'Tamamlandı',
                    'failed': 'Başarısız', 'payment_method': 'Ödeme yöntemi', 'card': 'Kart',
                    'bank_transfer': 'Banka transferi', 'crypto': 'Kripto para',
                    'min_amount': 'Minimum tutar', 'max_amount': 'Maksimum tutar',
                    'fee': 'Ücret', 'total': 'Toplam'
                },
                'reports': {
                    'title': 'Raporlar', 'my_reports': 'Raporlarım', 'create_report': 'Rapor oluştur',
                    'report_details': 'Rapor detayları', 'report_type': 'Rapor türü',
                    'property_evaluation': 'Emlak değerlendirmesi', 'market_analysis': 'Pazar analizi',
                    'investment_analysis': 'Yatırım analizi', 'region_analytics': 'Bölge analitiği',
                    'full_report': 'Tam rapor', 'report_date': 'Rapor tarihi',
                    'property_address': 'Emlak adresi', 'property_type': 'Emlak türü',
                    'property_area': 'Alan', 'property_price': 'Fiyat', 'market_value': 'Piyasa değeri',
                    'investment_potential': 'Yatırım potansiyeli', 'risk_level': 'Risk seviyesi',
                    'recommendations': 'Öneriler', 'download_report': 'Raporu indir',
                    'share_report': 'Raporu paylaş', 'delete_report': 'Raporu sil',
                    'edit_report': 'Raporu düzenle', 'save_report': 'Raporu kaydet',
                    'report_saved': 'Rapor kaydedildi', 'report_deleted': 'Rapor silindi',
                    'report_shared': 'Rapor paylaşıldı', 'liquidity': 'Likidite',
                    'page_description': 'Seçilen bölgedeki emlak pazarının detaylı analizini alın',
                    'country_label': 'Ülke:',
                    'city_label': 'Şehir:',
                    'county_label': 'Bölge/Alan:',
                    'district_label': 'İlçe:',
                    'country_placeholder': 'Ülke seçin',
                    'city_placeholder': 'Önce ülke seçin',
                    'county_placeholder': 'Önce şehir seçin',
                    'district_placeholder': 'Önce bölge seçin',
                    'confirm_selection': 'Seçimi onayla',
                    'back_to_main': '← Ana menüye dön',
                    'selected_location': 'Seçilen konum:',
                    'admin_ids': 'Yöneticiler için ID\'ler:',
                    'loading': 'Yükleniyor...',
                    'error_loading': 'Veri yükleme hatası',
                    'data_section_title': 'Bölgesel veri analizi',
                    'general_data_title': 'Genel veriler',
                    'house_type_data_title': 'Yatak odası sayısı verileri',
                    'floor_segment_data_title': 'Kat verileri',
                    'age_data_title': 'Yaş verileri',
                    'heating_data_title': 'Isıtma türü verileri',
                    'loading_text': 'Veriler yükleniyor...',
                    'error_text': 'Veri yükleme hatası',
                    'total_properties': 'Toplam mülk:',
                    'average_price': 'Ortalama fiyat:',
                    'price_range': 'Fiyat aralığı:',
                    'no_data_available': 'Veri mevcut değil',
                    'key_metrics_title': 'Ana metrikler',
                    'avg_sale_price_label': 'm² başına ortalama satış fiyatı',
                    'avg_rent_price_label': 'm² başına ortalama kira fiyatı',
                    'listing_period_sale_label': 'İlan süresi (Satış)',
                    'listing_period_rent_label': 'İlan süresi (Kiralama)',
                    'yield_label': 'Getiri (Kazanç)',
                    'insights_title': 'Özet',
                    'insights_loading': 'Veriler analiz ediliyor...',
                    'insights_error': 'Veri analizi hatası',
                    'object_evaluation_title': 'Nesne Değerlendirmesi',
                    'object_evaluation_description': 'Seçilen bölgedeki emlak değerinin profesyonel değerlendirmesini alın',
                    'listing_type_title': 'Analiz için emlak türünü seçin:',
                    'house_type_subtitle': 'Yatak odası sayısı:',
                    'floor_segment_subtitle': 'Kat:',
                    'age_data_subtitle': 'Nesne yaşı:',
                    'heating_data_subtitle': 'Isıtma türü:',
                    'price_object_subtitle': 'Nesne fiyatı:',
                    'area_object_subtitle': 'Nesne alanı (m²):',
                    'select_bedrooms': 'yatak odası sayısı',
                    'select_floor': 'kat',
                    'select_age': 'nesne yaşı',
                    'select_heating': 'ısıtma türü',
                    'property_types_title': 'Seçilen emlak özellikleri:',
                    'bedrooms_label': 'Yatak odası sayısı',
                    'floor_label': 'Kat',
                    'age_label': 'Nesne yaşı',
                    'heating_label': 'Isıtma türü',
                    'market_indicators_title': 'Pazar göstergeleri',
                    'market_trends_title': 'Pazar trendleri',
                    'sale_header': 'Satış',
                    'rent_header': 'Kiralama',
                    'currency_title': 'Para birimi seçin:',
                    'save_share_button_text': 'Raporu kaydet ve paylaş',
                    'modal_title': 'Rapor kaydedildi',
                    'modal_description': 'Raporunuz başarıyla kaydedildi. Linki kopyalayıp başkalarıyla paylaşabilirsiniz.',
                    'copy_button_text': 'Linki kopyala',
                    'close_button_text': 'Kapat',
                    'link_copied': 'Link kopyalandı!',
                    'saving_report': 'Rapor kaydediliyor...',
                    'error_saving': 'Rapor kaydetme hatası',
                    'price_placeholder': 'Fiyat girin',
                    'area_placeholder': 'Alan girin',
                    'trends_filter_info': '${totalCount} trendden ${filteredCount} tanesi gösteriliyor',
                    'market_comparison_title': 'Pazar karşılaştırması',
                    'price_per_m2_label': 'm² başına fiyat',
                    'area_label': 'Alan',
                    'price_comparison_label': 'm² başına fiyat:',
                    'area_comparison_label': 'Alan:',
                    'price_close_to_market': 'Nesneniz (${userPrice}) pazara yakın (${marketMin} – ${marketMax}).',
                    'price_above_market': 'Nesneniz (${userPrice}) pazardan ${percent}% yüksek.',
                    'price_below_market': 'Nesneniz (${userPrice}) pazardan ${percent}% düşük.',
                    'area_matches_market': 'Nesneniz (${userArea} m²) pazar talebine uygun (${marketMin}–${marketMax} m²).',
                    'area_below_market': 'Nesneniz (${userArea} m²) pazar talebinden küçük (${marketMin}–${marketMax} m²).',
                    'area_above_market': 'Nesneniz (${userArea} m²) pazar talebinden büyük (${marketMin}–${marketMax} m²).',
                    'consolidated_assessment_title': 'Konsolide değerlendirme',
                    'sale_price_title': 'm² başına fiyat (Satış için birim fiyat):',
                    'rent_price_title': 'm² başına kira fiyatı (Kiralama için birim fiyat):',
                    'yield_title': 'Getiri:',
                    'consolidated_average_label': 'Konsolide ortalama:',
                    'indicator_label': 'Gösterge',
                    'min_value_label': 'Minimum değer',
                    'max_value_label': 'Maksimum değer',
                    'avg_value_label': 'Ortalama değer',
                    'count_label': 'Sayı',
                    'percentage_label': 'Yüzde',
                    'my_reports_title': 'Raporlarım',
                    'my_reports_subtitle': 'Raporlarınızı yönetin',
                    'my_reports_loading': 'Raporlar yükleniyor...',
                    'my_reports_empty_title': 'Rapor bulunamadı',
                    'my_reports_empty_description': 'Henüz kayıtlı raporunuz yok. Ana menüde ilk raporunuzu oluşturun.',
                    'my_reports_back_btn': 'Ana menüye dön',
                    'my_reports_view_report': 'Görüntüle',
                    'my_reports_delete_report': 'Sil',
                    'my_reports_copy_link': 'Bağlantıyı kopyala',
                    'my_reports_delete_modal_title': 'Silme onayı',
                    'my_reports_delete_modal_message': 'Bu raporu silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.',
                    'my_reports_cancel_delete_btn': 'İptal',
                    'my_reports_confirm_delete_btn': 'Sil',
                    'my_reports_link_copied': 'Bağlantı panoya kopyalandı',
                    'my_reports_report_deleted': 'Rapor başarıyla silindi',
                    'my_reports_error_loading': 'Raporlar yüklenirken hata',
                    'my_reports_error_deleting': 'Rapor silinirken hata',
                    'my_reports_no_address': 'Adres belirtilmemiş',
                    'my_reports_no_price': 'Fiyat belirtilmemiş',
                    'my_reports_no_area': 'Alan belirtilmemiş',
                    'my_reports_no_bedrooms': 'Yatak odası sayısı belirtilmemiş',
                    'my_reports_property_evaluation': 'Nesne Değerlendirmesi',
                    'my_reports_property_analysis': 'Nesne Analizi',
                    'my_reports_market_analysis': 'Pazar Analizi'
                },
                'main': {
                    'title': 'Ana menü', 'welcome': 'Hoş geldiniz',
                    'quick_actions': 'Hızlı işlemler', 'recent_reports': 'Son raporlar',
                    'popular_services': 'Popüler hizmetler', 'news': 'Haberler',
                    'notifications': 'Bildirimler', 'menu': 'Menü', 'home': 'Ana sayfa',
                    'reports': 'Raporlar', 'analytics': 'Analitik', 'profile': 'Profil',
                    'help': 'Yardım', 'settings': 'Ayarlar'
                },
                'admin': {
                    'title': 'Yönetici paneli', 'users': 'Kullanıcılar', 'publications': 'Yayınlar',
                    'settings': 'Ayarlar', 'statistics': 'İstatistikler', 'user_management': 'Kullanıcı yönetimi',
                    'content_management': 'İçerik yönetimi', 'system_settings': 'Sistem ayarları',
                    'backup': 'Yedekleme', 'logs': 'Günlükler', 'security': 'Güvenlik'
                }
            }
        };
    }

    applyTranslations() {
        console.log('🔄 Применение переводов к странице...');
        
        // Применяем переводы к элементам с data-i18n
        const i18nElements = document.querySelectorAll('[data-i18n]');
        console.log(`📝 Найдено ${i18nElements.length} элементов с data-i18n`);
        
        i18nElements.forEach((element, index) => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key);
            
            console.log(`  ${index + 1}. Обработка элемента с ключом: ${key} → ${translation}`);
            
            if (translation && translation !== key) {
                element.textContent = translation;
                console.log(`    ✅ Элемент обновлен: ${translation}`);
            } else {
                console.warn(`    ⚠️ Перевод не найден или равен ключу: ${key}`);
            }
        });

        // Применяем переводы к заголовкам страниц
        const titleElements = document.querySelectorAll('[data-i18n-title]');
        console.log(`📝 Найдено ${titleElements.length} элементов с data-i18n-title`);
        
        titleElements.forEach((element, index) => {
            const key = element.getAttribute('data-i18n-title');
            const translation = this.getTranslation(key);
            
            console.log(`  ${index + 1}. Обработка заголовка с ключом: ${key} → ${translation}`);
            
            if (translation && translation !== key) {
                element.textContent = translation;
                console.log(`    ✅ Заголовок обновлен: ${translation}`);
            } else {
                console.warn(`    ⚠️ Перевод заголовка не найден: ${key}`);
            }
        });

        // Применяем переводы к placeholder
        const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
        console.log(`📝 Найдено ${placeholderElements.length} элементов с data-i18n-placeholder`);
        
        placeholderElements.forEach((element, index) => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.getTranslation(key);
            
            console.log(`  ${index + 1}. Обработка placeholder с ключом: ${key} → ${translation}`);
            
            if (translation && translation !== key) {
                element.placeholder = translation;
                console.log(`    ✅ Placeholder обновлен: ${translation}`);
            } else {
                console.warn(`    ⚠️ Перевод placeholder не найден: ${key}`);
            }
        });

        // Обновляем атрибут lang у html
        document.documentElement.lang = this.currentLanguage;
        console.log(`🌐 Установлен атрибут lang: ${this.currentLanguage}`);
        
        console.log('✅ Применение переводов завершено');
    }

    getTranslation(key) {
        const keys = key.split('.');
        let current = this.translations[this.currentLanguage];
        
        // Отладочная информация
        console.log(`🔍 Поиск перевода для ключа: ${key}`);
        console.log(`🌐 Текущий язык: ${this.currentLanguage}`);
        console.log(`📚 Доступные переводы:`, this.translations[this.currentLanguage]);
        
        for (const k of keys) {
            if (current && current[k]) {
                current = current[k];
                console.log(`✅ Найден уровень: ${k} = ${current}`);
            } else {
                console.warn(`❌ Не найден перевод для ключа: ${key}, уровень: ${k}`);
                return key; // Возвращаем ключ, если перевод не найден
            }
        }
        
        const result = typeof current === 'string' ? current : key;
        console.log(`🎯 Результат перевода: ${key} → ${result}`);
        return result;
    }

    addLanguageSelector() {
        // Добавляем переключатель языка, если его еще нет
        if (!document.getElementById('language-selector')) {
            const selector = document.createElement('div');
            selector.id = 'language-selector';
            selector.className = 'language-selector';
            selector.innerHTML = `
                <button class="lang-btn" onclick="i18nManager.showLanguageModal()">
                    ${this.getLanguageFlag(this.currentLanguage)} ${this.getLanguageName(this.currentLanguage)}
                </button>
            `;
            
            // Добавляем в начало body или в определенное место
            const container = document.querySelector('.container') || document.body;
            container.insertBefore(selector, container.firstChild);
        }
    }

    getLanguageFlag(lang) {
        const flags = {
            'ru': '🇷🇺',
            'en': '🇺🇸',
            'de': '🇩🇪',
            'fr': '🇫🇷',
            'tr': '🇹🇷'
        };
        return flags[lang] || '🌐';
    }

    getLanguageName(lang) {
        const names = {
            'ru': 'Русский',
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'tr': 'Türkçe'
        };
        return names[lang] || lang;
    }

    showLanguageModal() {
        // Создаем модальное окно для выбора языка
        const modal = document.createElement('div');
        modal.id = 'language-modal';
        modal.className = 'language-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>${this.getTranslation('common.language')}</h3>
                <div class="language-options">
                    <button onclick="i18nManager.setLanguage('ru')" class="lang-option ${this.currentLanguage === 'ru' ? 'active' : ''}">
                        🇷🇺 Русский
                    </button>
                    <button onclick="i18nManager.setLanguage('en')" class="lang-option ${this.currentLanguage === 'en' ? 'active' : ''}">
                        🇺🇸 English
                    </button>
                    <button onclick="i18nManager.setLanguage('de')" class="lang-option ${this.currentLanguage === 'de' ? 'active' : ''}">
                        🇩🇪 Deutsch
                    </button>
                    <button onclick="i18nManager.setLanguage('fr')" class="lang-option ${this.currentLanguage === 'fr' ? 'active' : ''}">
                        🇫🇷 Français
                    </button>
                    <button onclick="i18nManager.setLanguage('tr')" class="lang-option ${this.currentLanguage === 'tr' ? 'active' : ''}">
                        🇹🇷 Türkçe
                    </button>
                </div>
                <button onclick="i18nManager.closeLanguageModal()" class="close-btn">
                    ${this.getTranslation('common.close')}
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    closeLanguageModal() {
        const modal = document.getElementById('language-modal');
        if (modal) {
            modal.remove();
        }
    }

    async setLanguage(language) {
        if (['ru', 'en', 'de', 'fr', 'tr'].includes(language)) {
            this.currentLanguage = language;
            localStorage.setItem('aaadviser_language', language);
            
            // Сохраняем в базу данных, если есть пользователь
            await this.saveLanguagePreference(language);
            
            // Перезагружаем переводы и применяем их
            await this.loadTranslations();
            this.applyTranslations();
            this.updateLanguageSelector();
            
            this.closeLanguageModal();
        }
    }

    updateLanguageSelector() {
        const selector = document.getElementById('language-selector');
        if (selector) {
            selector.innerHTML = `
                <button class="lang-btn" onclick="i18nManager.showLanguageModal()">
                    ${this.getLanguageFlag(this.currentLanguage)} ${this.getLanguageName(this.currentLanguage)}
                </button>
            `;
        }
    }

    async saveLanguagePreference(language) {
        try {
            const userData = this.getUserData();
            if (userData) {
                await fetch('/api/set_language', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        telegram_id: userData.id,
                        language: language
                    })
                });
            }
        } catch (error) {
            console.warn('Failed to save language preference:', error);
        }
    }

    getUserData() {
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                return tg.initDataUnsafe.user;
            }
        }
        return null;
    }

    // Утилиты для перевода
    translate(key) {
        return this.getTranslation(key);
    }

    translateWithParams(key, params) {
        let translation = this.getTranslation(key);
        for (const [param, value] of Object.entries(params)) {
            translation = translation.replace(`{${param}}`, value);
        }
        return translation;
    }
}

// Создаем глобальный экземпляр
const i18nManager = new I18nManager();
window.i18nManager = i18nManager;

// Добавляем стили для переключателя языка
const style = document.createElement('style');
style.textContent = `
    .language-selector {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
    }
    
    .lang-btn {
        background: #007bff;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .lang-btn:hover {
        background: #0056b3;
    }
    
    .language-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2000;
    }
    
    .modal-content {
        background: white;
        padding: 20px;
        border-radius: 10px;
        max-width: 300px;
        width: 90%;
    }
    
    .language-options {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 20px 0;
    }
    
    .lang-option {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background: white;
        cursor: pointer;
        text-align: left;
        font-size: 16px;
    }
    
    .lang-option:hover {
        background: #f5f5f5;
    }
    
    .lang-option.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .close-btn {
        width: 100%;
        padding: 10px;
        background: #6c757d;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .close-btn:hover {
        background: #545b62;
    }
`;
document.head.appendChild(style);
