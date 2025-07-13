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
import requests

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

# Google Maps API ключ
GOOGLE_MAPS_API_KEY = "AIzaSyBrDkDpNKNAIyY147MQ78hchBkeyCAxhEw"

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
            .btn-danger {
                background: #dc3545;
            }
            .btn-danger:hover {
                background: #c82333;
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
            .input-field {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                margin: 10px 0;
                box-sizing: border-box;
            }
            .map-container {
                width: 100%;
                height: 200px;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin: 10px 0;
                background: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .navigation-buttons {
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }
            .step {
                display: none;
            }
            .step.active {
                display: block;
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
            
            <!-- Шаги создания отчета -->
            <div id="reportSteps" style="display:none;">
                <div class="step active" id="stepAddress">
                    <h3 id="addressTitle">Введите адрес объекта</h3>
                    <input type="text" id="addressInput" class="input-field" placeholder="Введите адрес...">
                    <button class="btn" onclick="geocodeAddress()">Найти адрес</button>
                    <div class="navigation-buttons">
                        <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
                
                <div class="step" id="stepConfirm">
                    <h3>Подтвердите адрес</h3>
                    <div class="map-container" id="mapContainer">
                        <p>Карта загружается...</p>
                    </div>
                    <p id="formattedAddress"></p>
                    <button class="btn btn-success" onclick="confirmAddress()">Да, адрес верный</button>
                    <button class="btn btn-danger" onclick="rejectAddress()">Нет, ввести другой</button>
                    <div class="navigation-buttons">
                        <button class="btn" onclick="goBack()">Назад</button>
                        <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
                
                <div class="step" id="stepBedrooms">
                    <h3 id="bedroomsTitle">Количество спален</h3>
                    <input type="number" id="bedroomsInput" class="input-field" placeholder="Введите количество спален (1-10)">
                    <button class="btn" onclick="validateBedrooms()">Продолжить</button>
                    <div class="navigation-buttons">
                        <button class="btn" onclick="goBack()">Назад</button>
                        <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
                
                <div class="step" id="stepPrice">
                    <h3 id="priceTitle">Цена покупки</h3>
                    <input type="number" id="priceInput" class="input-field" placeholder="Введите цену в евро">
                    <button class="btn" onclick="validatePrice()">Продолжить</button>
                    <div class="navigation-buttons">
                        <button class="btn" onclick="goBack()">Назад</button>
                        <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
                
                <div class="step" id="stepReport">
                    <h3>Генерация отчета</h3>
                    <p id="reportMessage">Ваш отчет формируется...</p>
                    <div class="navigation-buttons">
                        <button class="btn" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
            </div>
        </div>
        <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        const userInfo = document.getElementById('userInfo');
        const langSelect = document.getElementById('langSelect');
        const menuBlock = document.getElementById('menuBlock');
        const reportSteps = document.getElementById('reportSteps');
        let telegramUser = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : null;
        let telegramId = telegramUser ? telegramUser.id : null;
        let languageCode = telegramUser ? telegramUser.language_code : 'en';
        let currentLanguage = null;
        let currentStep = 'address';
        let reportData = {};

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
            reportSteps.style.display = 'none';
            let html = `<p style="margin-bottom:10px;">${title}</p>`;
            for (const [code, name] of Object.entries(languages)) {
                html += `<button class="lang-btn" onclick="selectLanguage('${code}')">${name}</button>`;
            }
            langSelect.innerHTML = html;
        }

        window.selectLanguage = async function(lang) {
            await fetch('/api/set_language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ telegram_id: telegramId, language: lang })
            });
            currentLanguage = lang;
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
            reportSteps.style.display = 'none';
            let html = '';
            for (let i = 0; i < menu.length; i++) {
                const item = menu[i];
                if (i === 0) {
                    html += `<button class="menu-btn" onclick="startNewReport()">${item}</button>`;
                } else {
                    html += `<button class="menu-btn">${item}</button>`;
                }
            }
            menuBlock.innerHTML = html;
        }

        function startNewReport() {
            menuBlock.style.display = 'none';
            reportSteps.style.display = '';
            currentStep = 'address';
            showStep('address');
            updateStepTitles();
        }

        function showStep(step) {
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            document.getElementById('step' + step.charAt(0).toUpperCase() + step.slice(1)).classList.add('active');
        }

        function updateStepTitles() {
            const texts = getLocalizedTexts();
            document.getElementById('addressTitle').textContent = texts.enter_address;
            document.getElementById('bedroomsTitle').textContent = texts.enter_bedrooms;
            document.getElementById('priceTitle').textContent = texts.enter_price;
        }

        function getLocalizedTexts() {
            // В реальном приложении эти тексты должны приходить с сервера
            const texts = {
                'ru': {
                    enter_address: 'Введите адрес объекта',
                    enter_bedrooms: 'Количество спален',
                    enter_price: 'Цена покупки в евро',
                    address_not_found: 'Адрес не распознан, попробуйте ввести его еще раз.',
                    address_correct: 'Этот адрес корректный?',
                    yes: 'Да',
                    no: 'Нет',
                    invalid_bedrooms: 'Количество спален должно быть числом от 1 до 10.',
                    invalid_price: 'Цена должна быть положительным числом.',
                    generating_report: 'Ваш отчет формируется...',
                    back: 'Назад',
                    main_menu: 'В главное меню'
                },
                'en': {
                    enter_address: 'Enter property address',
                    enter_bedrooms: 'Number of bedrooms',
                    enter_price: 'Purchase price in euros',
                    address_not_found: 'Address not recognized, please try entering it again.',
                    address_correct: 'Is this address correct?',
                    yes: 'Yes',
                    no: 'No',
                    invalid_bedrooms: 'Number of bedrooms must be between 1 and 10.',
                    invalid_price: 'Price must be a positive number.',
                    generating_report: 'Your report is being generated...',
                    back: 'Back',
                    main_menu: 'Main menu'
                }
            };
            return texts[currentLanguage] || texts['en'];
        }

        async function geocodeAddress() {
            const address = document.getElementById('addressInput').value.trim();
            if (!address) return;

            const res = await fetch('/api/geocode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address: address })
            });
            const data = await res.json();

            if (data.success) {
                reportData.address = data.formatted_address;
                reportData.lat = data.lat;
                reportData.lng = data.lng;
                document.getElementById('formattedAddress').textContent = data.formatted_address;
                showStep('confirm');
                currentStep = 'confirm';
            } else {
                const texts = getLocalizedTexts();
                alert(texts.address_not_found);
            }
        }

        function confirmAddress() {
            showStep('bedrooms');
            currentStep = 'bedrooms';
        }

        function rejectAddress() {
            document.getElementById('addressInput').value = '';
            showStep('address');
            currentStep = 'address';
        }

        async function validateBedrooms() {
            const bedrooms = document.getElementById('bedroomsInput').value;
            const res = await fetch('/api/validate_bedrooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bedrooms: bedrooms })
            });
            const data = await res.json();

            if (data.valid) {
                reportData.bedrooms = parseInt(bedrooms);
                showStep('price');
                currentStep = 'price';
            } else {
                const texts = getLocalizedTexts();
                alert(texts.invalid_bedrooms);
            }
        }

        async function validatePrice() {
            const price = document.getElementById('priceInput').value;
            const res = await fetch('/api/validate_price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ price: price })
            });
            const data = await res.json();

            if (data.valid) {
                reportData.price = parseFloat(price);
                showStep('report');
                currentStep = 'report';
                generateReport();
            } else {
                const texts = getLocalizedTexts();
                alert(texts.invalid_price);
            }
        }

        async function generateReport() {
            const res = await fetch('/api/generate_report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    address: reportData.address,
                    bedrooms: reportData.bedrooms,
                    price: reportData.price,
                    language: currentLanguage
                })
            });
            const data = await res.json();
            document.getElementById('reportMessage').textContent = data.message;
        }

        function goBack() {
            switch(currentStep) {
                case 'confirm':
                    showStep('address');
                    currentStep = 'address';
                    break;
                case 'bedrooms':
                    showStep('confirm');
                    currentStep = 'confirm';
                    break;
                case 'price':
                    showStep('bedrooms');
                    currentStep = 'bedrooms';
                    break;
            }
        }

        function goToMainMenu() {
            reportSteps.style.display = 'none';
            reportData = {};
            currentStep = 'address';
            document.getElementById('addressInput').value = '';
            document.getElementById('bedroomsInput').value = '';
            document.getElementById('priceInput').value = '';
            showMenu([]);
            fetchUser();
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

@app.route('/api/geocode', methods=['POST'])
def api_geocode():
    """Геокодинг адреса через Google Maps API"""
    data = request.json or {}
    address = data.get('address')
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    try:
        # Запрос к Google Maps Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['status'] == 'OK' and result['results']:
            location = result['results'][0]['geometry']['location']
            formatted_address = result['results'][0]['formatted_address']
            return jsonify({
                'success': True,
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': formatted_address
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Address not found'
            })
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return jsonify({'error': 'Geocoding service error'}), 500

@app.route('/api/validate_bedrooms', methods=['POST'])
def api_validate_bedrooms():
    """Валидация количества спален"""
    data = request.json or {}
    bedrooms = data.get('bedrooms')
    
    try:
        bedrooms_int = int(bedrooms)
        if 1 <= bedrooms_int <= 10:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': 'Bedrooms must be between 1 and 10'})
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'error': 'Bedrooms must be a number'})

@app.route('/api/validate_price', methods=['POST'])
def api_validate_price():
    """Валидация цены"""
    data = request.json or {}
    price = data.get('price')
    
    try:
        price_float = float(price)
        if price_float > 0:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': 'Price must be positive'})
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'error': 'Price must be a number'})

@app.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """Генерация отчета (заглушка)"""
    data = request.json or {}
    address = data.get('address')
    bedrooms = data.get('bedrooms')
    price = data.get('price')
    language = data.get('language', 'en')
    
    if not all([address, bedrooms, price]):
        return jsonify({'error': 'Missing required data'}), 400
    
    # Заглушка - в будущем здесь будет реальная генерация отчета
    return jsonify({
        'success': True,
        'message': locales[language]['new_report']['generating_report']
    })

import threading

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Запускаем Flask-сервер в отдельном потоке-демоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем Telegram-бота в главном потоке
    main() 