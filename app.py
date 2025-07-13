import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import threading
import asyncio
from locales import locales

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# URL вашего WebApp (замените на ваш домен после деплоя)
WEBAPP_URL = "https://aaadvisor-zaicevn.amvera.io/webapp"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    if not user or not hasattr(user, 'id'):
        await update.message.reply_text("Ошибка: не удалось определить пользователя.")
        return
    
    # Проверяем, есть ли пользователь в базе данных
    try:
        result = supabase.table('users').select('*').eq('telegram_id', user.id).execute()
        
        if result.data:
            # Пользователь уже существует
            welcome_message = f"С возвращением, {getattr(user, 'first_name', 'Пользователь')}! 👋"
        else:
            # Новый пользователь
            welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
            
            # Сохраняем пользователя в базу данных
            supabase.table('users').insert({
                'telegram_id': user.id,
                'username': getattr(user, 'username', None),
                'first_name': getattr(user, 'first_name', None),
                'last_name': getattr(user, 'last_name', None)
            }).execute()
            
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
    
    # Создаем кнопку для запуска WebApp
    keyboard = [
        [KeyboardButton("🚀 Запустить WebApp", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик данных от WebApp"""
    data = getattr(update.effective_message.web_app_data, 'data', None)
    user = update.effective_user
    
    await update.message.reply_text(
        f"Получены данные от WebApp: {data}\n"
        f"Пользователь: {getattr(user, 'first_name', 'Пользователь')}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Используйте кнопку WebApp для тестирования."
    )

def main() -> None:
    """Запуск бота"""
    logger.info("Запуск Telegram-бота...")
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# Flask маршруты для WebApp
@app.route('/webapp')
def webapp():
    """Страница WebApp"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram WebApp Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            .user-info {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .btn {
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #0056b3;
            }
            .btn-success {
                background: #28a745;
            }
            .btn-success:hover {
                background: #1e7e34;
            }
            .lang-btn {
                background: #f1f1f1;
                color: #333;
                border: 1px solid #ccc;
                margin: 5px;
                padding: 10px 18px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 15px;
            }
            .lang-btn.selected {
                background: #007bff;
                color: #fff;
                border: none;
            }
            .menu-btn {
                background: #764ba2;
                color: #fff;
                border: none;
                margin: 8px 0;
                padding: 14px 0;
                width: 100%;
                border-radius: 8px;
                font-size: 17px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .menu-btn:hover {
                background: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="user-info" id="userInfo">
                <p>Загрузка информации о пользователе...</p>
            </div>
            <div id="langSelect" style="display:none;"></div>
            <div id="menuBlock" style="display:none;"></div>
        </div>
        <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        const userInfo = document.getElementById('userInfo');
        const langSelect = document.getElementById('langSelect');
        const menuBlock = document.getElementById('menuBlock');
        let telegramUser = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : null;
        let telegramId = telegramUser ? telegramUser.id : null;
        let languageCode = telegramUser ? telegramUser.language_code : 'en';
        let currentLanguage = null;

        async function fetchUser() {
            if (!telegramId) {
                userInfo.innerHTML = '<p>Ошибка: не удалось получить данные пользователя Telegram.</p>';
                return;
            }
            const res = await fetch('/api/user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    telegram_id: telegramId,
                    username: telegramUser.username,
                    first_name: telegramUser.first_name,
                    last_name: telegramUser.last_name,
                    language_code: languageCode
                })
            });
            const data = await res.json();
            if (data.exists) {
                currentLanguage = data.language;
                showWelcome(data.welcome);
                showMenu(data.menu);
            } else {
                currentLanguage = data.language;
                showWelcome(data.welcome);
                showLanguageSelect(data.choose_language, data.languages);
            }
        }

        function showWelcome(text) {
            userInfo.innerHTML = `<p>${text}</p>`;
        }

        function showLanguageSelect(title, languages) {
            langSelect.style.display = '';
            menuBlock.style.display = 'none';
            let html = `<p style="margin-bottom:10px;">${title}</p>`;
            for (const [code, name] of Object.entries(languages)) {
                html += `<button class="lang-btn" onclick="selectLanguage('${code}')">${name}</button>`;
            }
            langSelect.innerHTML = html;
        }

        window.selectLanguage = async function(lang) {
            // Отправляем выбранный язык на сервер
            await fetch('/api/set_language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ telegram_id: telegramId, language: lang })
            });
            currentLanguage = lang;
            // Получаем меню на выбранном языке
            const res = await fetch('/api/menu', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: lang })
            });
            const data = await res.json();
            langSelect.style.display = 'none';
            showMenu(data.menu);
        }

        function showMenu(menu) {
            menuBlock.style.display = '';
            let html = '';
            for (const item of menu) {
                html += `<button class="menu-btn">${item}</button>`;
            }
            menuBlock.innerHTML = html;
        }

        fetchUser();
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({"status": "ok", "message": "Telegram WebApp Bot is running"})

@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    language_code = data.get('language_code', 'en')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400

    # Проверяем пользователя в базе
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data if hasattr(user_result, 'data') else user_result
    if user:
        user = user[0]
        lang = user.get('language') or (language_code[:2] if language_code[:2] in locales else 'en')
        return jsonify({
            'exists': True,
            'language': lang,
            'welcome': locales[lang]['welcome_back'],
            'menu': locales[lang]['menu']
        })
    else:
        # Новый пользователь
        supabase.table('users').insert({
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language': None
        }).execute()
        # Приветствие на языке Telegram
        lang = language_code[:2] if language_code[:2] in locales else 'en'
        return jsonify({
            'exists': False,
            'language': lang,
            'welcome': locales[lang]['welcome_new'],
            'choose_language': locales[lang]['choose_language'],
            'languages': locales[lang]['language_names']
        })

@app.route('/api/set_language', methods=['POST'])
def api_set_language():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    language = data.get('language')
    if not telegram_id or not language:
        return jsonify({'error': 'telegram_id and language required'}), 400
    # Обновляем язык пользователя
    supabase.table('users').update({'language': language}).eq('telegram_id', telegram_id).execute()
    return jsonify({'ok': True})

@app.route('/api/menu', methods=['POST'])
def api_menu():
    data = request.json or {}
    language = data.get('language', 'en')
    if language not in locales:
        language = 'en'
    return jsonify({'menu': locales[language]['menu']})

import threading

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Запускаем Flask-сервер в отдельном потоке-демоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем Telegram-бота в главном потоке
    main() 