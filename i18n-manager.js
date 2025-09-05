// Универсальная система мультиязычности для всех страниц приложения
class I18nManager {
    constructor() {
        this.currentLanguage = 'ru';
        this.translations = {};
        this.init();
    }

    async init() {
        this.currentLanguage = this.getInitialLanguage();
        await this.loadTranslations();
        this.applyTranslations();
        this.addLanguageSelector();
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
        try {
            const response = await fetch('/api/translations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: this.currentLanguage })
            });

            if (response.ok) {
                this.translations = await response.json();
            } else {
                this.loadFallbackTranslations();
            }
        } catch (error) {
            console.warn('Failed to load translations from server, using fallback:', error);
            this.loadFallbackTranslations();
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
                    'dark_mode': 'Темная тема', 'light_mode': 'Светлая тема'
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
                    'report_shared': 'Отчет отправлен'
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
                    'dark_mode': 'Dark Mode', 'light_mode': 'Light Mode'
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
                    'report_shared': 'Report Shared'
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
                    'dark_mode': 'Dunkler Modus', 'light_mode': 'Heller Modus'
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
                    'report_shared': 'Bericht geteilt'
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
                    'dark_mode': 'Mode sombre', 'light_mode': 'Mode clair'
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
                    'report_shared': 'Rapport partagé'
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
                    'dark_mode': 'Karanlık mod', 'light_mode': 'Aydınlık mod'
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
                    'report_shared': 'Rapor paylaşıldı'
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
        // Применяем переводы к элементам с data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key);
            if (translation) {
                element.textContent = translation;
            }
        });

        // Применяем переводы к заголовкам страниц
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            const translation = this.getTranslation(key);
            if (translation) {
                element.textContent = translation;
            }
        });

        // Применяем переводы к placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.getTranslation(key);
            if (translation) {
                element.placeholder = translation;
            }
        });

        // Обновляем атрибут lang у html
        document.documentElement.lang = this.currentLanguage;
    }

    getTranslation(key) {
        const keys = key.split('.');
        let current = this.translations[this.currentLanguage];
        
        for (const k of keys) {
            if (current && current[k]) {
                current = current[k];
            } else {
                return key; // Возвращаем ключ, если перевод не найден
            }
        }
        
        return typeof current === 'string' ? current : key;
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
