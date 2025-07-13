import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from supabase import create_client, Client
from dotenv import load_dotenv
import threading
import asyncio
from locales import translations

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

LANGUAGE, MENU = range(2)

SUPPORTED_LANGS = ['en', 'de', 'fr', 'tr', 'ru']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    if not user or not update.message:
        return
    user_lang = getattr(user, 'language_code', 'en')
    if user_lang not in SUPPORTED_LANGS:
        user_lang = 'en'
    try:
        result = supabase.table('users').select('*').eq('telegram_id', user.id).execute()
        user_data = result.data[0] if result.data else None
        if user_data and user_data.get('language'):
            lang = user_data['language']
            welcome_message = translations[lang]['welcome_back']
            await show_menu(update, context, lang)
        else:
            # Новый пользователь или не выбран язык
            welcome_message = translations[user_lang]['welcome_new']
            await update.message.reply_text(welcome_message)
            await ask_language(update, context, user_lang)
            # Сохраняем пользователя, если новый
            if not user_data:
                supabase.table('users').insert({
                    'telegram_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'language': None
                }).execute()
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        await update.message.reply_text(translations[user_lang]['welcome_new'])
        await ask_language(update, context, user_lang)

async def ask_language(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang: str):
    if not update.message:
        return
    lang_buttons = [[translations[user_lang]['language_names'][code]] for code in SUPPORTED_LANGS if code != user_lang]
    lang_buttons.insert(0, [translations[user_lang]['language_names'][user_lang]])
    reply_markup = ReplyKeyboardMarkup(lang_buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(translations[user_lang]['choose_language'], reply_markup=reply_markup)
    context.user_data['awaiting_language'] = True

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get('awaiting_language') or not update.message or not update.effective_user:
        return  # Не обрабатываем, если не ждем выбора языка
    user = update.effective_user
    text = update.message.text
    # Определяем выбранный язык
    lang = None
    for code in SUPPORTED_LANGS:
        if text.lower() == translations[code]['language_names'][code].lower():
            lang = code
            break
        # Проверяем на всех языках
        for name in translations[code]['language_names'].values():
            if text.lower() == name.lower():
                lang = code
                break
    if not lang:
        # Повторно просим выбрать язык
        user_lang = getattr(user, 'language_code', 'en')
        if user_lang not in SUPPORTED_LANGS:
            user_lang = 'en'
        await ask_language(update, context, user_lang)
        return
    # Сохраняем язык в базе
    supabase.table('users').update({'language': lang}).eq('telegram_id', user.id).execute()
    await update.message.reply_text(translations[lang]['welcome_new'], reply_markup=ReplyKeyboardRemove())
    await show_menu(update, context, lang)
    context.user_data['awaiting_language'] = False

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    if not update.message:
        return
    menu_items = translations[lang]['menu_items']
    reply_markup = ReplyKeyboardMarkup([[item] for item in menu_items], resize_keyboard=True)
    await update.message.reply_text(translations[lang]['menu'], reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_language') or not update.message or not update.effective_user:
        return  # Не обрабатываем меню, если ждем выбора языка
    user = update.effective_user
    # Получаем язык пользователя из базы
    result = supabase.table('users').select('language').eq('telegram_id', user.id).execute()
    lang = 'en'
    if result.data and result.data[0].get('language') in SUPPORTED_LANGS:
        lang = result.data[0]['language']
    # Здесь можно реализовать обработку каждого пункта меню
    await update.message.reply_text(f"Вы выбрали: {update.message.text}", reply_markup=ReplyKeyboardMarkup([[item] for item in translations[lang]['menu_items']], resize_keyboard=True))

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик данных от WebApp"""
    data = update.effective_message.web_app_data.data
    user = update.effective_user
    
    await update.message.reply_text(
        f"Получены данные от WebApp: {data}\n"
        f"Пользователь: {user.first_name}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Используйте кнопку WebApp для тестирования."
    )

def main() -> None:
    """Запуск бота"""
    logger.info("Запуск Telegram-бота...")
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, language_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram WebApp Test</h1>
            <div class="user-info" id="userInfo">
                <p>Загрузка информации о пользователе...</p>
            </div>
            <button class="btn" onclick="sendData()">📤 Отправить данные</button>
            <button class="btn btn-success" onclick="closeWebApp()">✅ Закрыть WebApp</button>
        </div>

        <script>
            // Инициализация Telegram WebApp
            let tg = window.Telegram.WebApp;
            tg.expand();
            tg.ready();

            // Отображаем информацию о пользователе
            const userInfo = document.getElementById('userInfo');
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const user = tg.initDataUnsafe.user;
                userInfo.innerHTML = `
                    <h3>👤 Информация о пользователе</h3>
                    <p><strong>ID:</strong> ${user.id}</p>
                    <p><strong>Имя:</strong> ${user.first_name}</p>
                    <p><strong>Фамилия:</strong> ${user.last_name || 'Не указана'}</p>
                    <p><strong>Username:</strong> ${user.username || 'Не указан'}</p>
                    <p><strong>Язык:</strong> ${user.language_code || 'Не указан'}</p>
                `;
            } else {
                userInfo.innerHTML = '<p>Информация о пользователе недоступна</p>';
            }

            function sendData() {
                const data = {
                    action: 'test',
                    timestamp: new Date().toISOString(),
                    user: tg.initDataUnsafe.user
                };
                
                tg.sendData(JSON.stringify(data));
                alert('✅ Данные отправлены в бот!');
            }

            function closeWebApp() {
                tg.close();
            }

            // Обработка события отправки данных
            tg.onEvent('mainButtonClicked', function() {
                sendData();
            });
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({"status": "ok", "message": "Telegram WebApp Bot is running"})

import threading

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Запускаем Flask-сервер в отдельном потоке-демоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем Telegram-бота в главном потоке
    main() 