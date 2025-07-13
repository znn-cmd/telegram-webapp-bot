import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv

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
WEBAPP_URL = "https://your-domain.amvera.io/webapp"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем, есть ли пользователь в базе данных
    try:
        result = supabase.table('users').select('*').eq('telegram_id', user.id).execute()
        
        if result.data:
            # Пользователь уже существует
            welcome_message = f"С возвращением, {user.first_name}! 👋"
        else:
            # Новый пользователь
            welcome_message = f"Привет, {user.first_name}! Добро пожаловать! 🎉"
            
            # Сохраняем пользователя в базу данных
            supabase.table('users').insert({
                'telegram_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }).execute()
            
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        welcome_message = f"Привет, {user.first_name}! Добро пожаловать! 🎉"
    
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

if __name__ == '__main__':
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=8080, debug=False) 