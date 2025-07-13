import os
import logging
from flask import Flask, request, jsonify, send_file
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import threading
import asyncio
from locales import locales
import requests
import datetime
from fpdf import FPDF
import tempfile
import os
import yfinance as yf
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional

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

# API ключи для внешних данных
TRADING_ECONOMICS_API_KEY = os.getenv("TRADING_ECONOMICS_API_KEY", "")
WORLD_BANK_API_KEY = os.getenv("WORLD_BANK_API_KEY", "")

# Функции для получения макроэкономических данных
def get_turkey_macroeconomic_data():
    """Получение макроэкономических данных для Турции"""
    try:
        # Инфляция (CPI)
        inflation_url = f"https://api.tradingeconomics.com/indicators/turkey/inflation"
        if TRADING_ECONOMICS_API_KEY:
            inflation_url += f"?c={TRADING_ECONOMICS_API_KEY}"
        
        inflation_response = requests.get(inflation_url, timeout=10)
        inflation_data = inflation_response.json() if inflation_response.status_code == 200 else []
        
        # Курс валюты (USD/TRY)
        currency_url = f"https://api.tradingeconomics.com/indicators/turkey/currency"
        if TRADING_ECONOMICS_API_KEY:
            currency_url += f"?c={TRADING_ECONOMICS_API_KEY}"
        
        currency_response = requests.get(currency_url, timeout=10)
        currency_data = currency_response.json() if currency_response.status_code == 200 else []
        
        # Ставка ЦБ
        interest_rate_url = f"https://api.tradingeconomics.com/indicators/turkey/interestrate"
        if TRADING_ECONOMICS_API_KEY:
            interest_rate_url += f"?c={TRADING_ECONOMICS_API_KEY}"
        
        interest_rate_response = requests.get(interest_rate_url, timeout=10)
        interest_rate_data = interest_rate_response.json() if interest_rate_response.status_code == 200 else []
        
        # GDP
        gdp_url = f"https://api.tradingeconomics.com/indicators/turkey/gdp"
        if TRADING_ECONOMICS_API_KEY:
            gdp_url += f"?c={TRADING_ECONOMICS_API_KEY}"
        
        gdp_response = requests.get(gdp_url, timeout=10)
        gdp_data = gdp_response.json() if gdp_response.status_code == 200 else []
        
        return {
            'inflation': inflation_data[0]['LatestValue'] if inflation_data else 64.86,
            'currency_rate': currency_data[0]['LatestValue'] if currency_data else 31.5,
            'interest_rate': interest_rate_data[0]['LatestValue'] if interest_rate_data else 45.0,
            'gdp_growth': gdp_data[0]['LatestValue'] if gdp_data else 4.5
        }
    except Exception as e:
        logger.error(f"Ошибка получения макроэкономических данных: {e}")
        # Возвращаем дефолтные значения
        return {
            'inflation': 64.86,
            'currency_rate': 31.5,
            'interest_rate': 45.0,
            'gdp_growth': 4.5
        }

def get_financial_market_data():
    """Получение данных финансовых рынков"""
    try:
        # Турецкие банковские депозиты (симуляция)
        deposit_rates = {
            'TRY': 45.0,  # Ставка по депозитам в лирах
            'USD': 3.5,   # Ставка по депозитам в долларах
            'EUR': 2.8    # Ставка по депозитам в евро
        }
        
        # Государственные облигации Турции
        bond_yields = {
            '2_year': 42.5,
            '5_year': 41.8,
            '10_year': 40.2
        }
        
        # Акции турецких компаний
        stock_data = {}
        turkish_stocks = ['THYAO.IS', 'GARAN.IS', 'AKBNK.IS', 'KRDMD.IS']
        
        for stock in turkish_stocks:
            try:
                ticker = yf.Ticker(stock)
                info = ticker.info
                stock_data[stock] = {
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0)
                }
            except:
                stock_data[stock] = {'price': 0, 'change': 0, 'volume': 0}
        
        # Недвижимость фонды (симуляция)
        real_estate_funds = {
            'TURKISH_REIT_INDEX': 1250.5,
            'PROPERTY_FUND_YIELD': 8.5,
            'REAL_ESTATE_GROWTH': 12.3
        }
        
        return {
            'deposit_rates': deposit_rates,
            'bond_yields': bond_yields,
            'stock_data': stock_data,
            'real_estate_funds': real_estate_funds
        }
    except Exception as e:
        logger.error(f"Ошибка получения финансовых данных: {e}")
        return {
            'deposit_rates': {'TRY': 45.0, 'USD': 3.5, 'EUR': 2.8},
            'bond_yields': {'2_year': 42.5, '5_year': 41.8, '10_year': 40.2},
            'stock_data': {},
            'real_estate_funds': {'TURKISH_REIT_INDEX': 1250.5, 'PROPERTY_FUND_YIELD': 8.5, 'REAL_ESTATE_GROWTH': 12.3}
        }

def get_regional_indicators():
    """Получение региональных показателей для Анталии"""
    try:
        # Данные по Анталии (симуляция на основе реальных данных)
        return {
            'antalya_population': 2.5,  # млн человек
            'antalya_gdp_growth': 6.2,  # %
            'antalya_unemployment': 8.1,  # %
            'antalya_tourism_growth': 15.3,  # %
            'antalya_infrastructure_investment': 2.8,  # млрд USD
            'antalya_property_price_growth': 18.5,  # %
            'antalya_rental_yield': 6.8,  # %
            'antalya_construction_activity': 12.4  # %
        }
    except Exception as e:
        logger.error(f"Ошибка получения региональных данных: {e}")
        return {
            'antalya_population': 2.5,
            'antalya_gdp_growth': 6.2,
            'antalya_unemployment': 8.1,
            'antalya_tourism_growth': 15.3,
            'antalya_infrastructure_investment': 2.8,
            'antalya_property_price_growth': 18.5,
            'antalya_rental_yield': 6.8,
            'antalya_construction_activity': 12.4
        }

def get_tax_information():
    """Получение налоговой информации для недвижимости в Турции"""
    return {
        'property_tax_rate': 0.1,  # % от стоимости недвижимости
        'income_tax_rate': 15.0,   # % для резидентов
        'capital_gains_tax': 0.0,  # % для недвижимости (освобождение)
        'stamp_duty': 4.0,         # % при покупке
        'notary_fee': 0.5,         # % от стоимости
        'title_deed_fee': 0.5,     # % от стоимости
        'annual_property_tax': 0.1, # % от стоимости
        'rental_income_tax': 20.0   # % для арендного дохода
    }

def get_risk_assessment():
    """Оценка рисков для инвестиций в недвижимость"""
    return {
        'currency_risk': 'Высокий',  # Волатильность лиры
        'political_risk': 'Средний', # Политическая стабильность
        'economic_risk': 'Средний',  # Экономические показатели
        'market_risk': 'Низкий',     # Стабильность рынка недвижимости
        'liquidity_risk': 'Низкий',  # Ликвидность недвижимости
        'regulatory_risk': 'Низкий', # Регуляторная среда
        'overall_risk_score': 6.5    # По шкале 1-10
    }

def generate_comprehensive_report(property_data, user_id):
    """Генерация полного отчета с макроэкономическими данными"""
    try:
        # Получаем все необходимые данные
        macro_data = get_turkey_macroeconomic_data()
        financial_data = get_financial_market_data()
        regional_data = get_regional_indicators()
        tax_data = get_tax_information()
        risk_data = get_risk_assessment()
        
        # Анализ недвижимости
        property_analysis = {
            'address': property_data.get('address', 'Не указан'),
            'bedrooms': property_data.get('bedrooms', 0),
            'price_usd': property_data.get('price_usd', 0),
            'price_try': property_data.get('price_try', 0),
            'area_sqm': property_data.get('area_sqm', 0),
            'price_per_sqm': property_data.get('price_per_sqm', 0),
            'rental_yield': property_data.get('rental_yield', 0),
            'roi_potential': property_data.get('roi_potential', 0)
        }
        
        # Расчеты
        monthly_rent_estimate = property_analysis['price_usd'] * 0.006  # 0.6% от стоимости
        annual_rent_income = monthly_rent_estimate * 12
        rental_yield_percentage = (annual_rent_income / property_analysis['price_usd']) * 100
        
        # Налоговые расчеты
        property_tax_annual = property_analysis['price_usd'] * (tax_data['property_tax_rate'] / 100)
        rental_income_tax = annual_rent_income * (tax_data['rental_income_tax'] / 100)
        total_tax_burden = property_tax_annual + rental_income_tax
        
        # Инвестиционный анализ
        investment_analysis = {
            'total_investment': property_analysis['price_usd'],
            'monthly_rent_estimate': monthly_rent_estimate,
            'annual_rent_income': annual_rent_income,
            'rental_yield_percentage': rental_yield_percentage,
            'annual_property_tax': property_tax_annual,
            'annual_rental_tax': rental_income_tax,
            'net_annual_income': annual_rent_income - total_tax_burden,
            'net_yield_percentage': ((annual_rent_income - total_tax_burden) / property_analysis['price_usd']) * 100
        }
        
        # Сравнение с альтернативными инвестициями
        alternative_investments = {
            'bank_deposit_try': property_analysis['price_usd'] * (financial_data['deposit_rates']['TRY'] / 100),
            'bank_deposit_usd': property_analysis['price_usd'] * (financial_data['deposit_rates']['USD'] / 100),
            'government_bonds': property_analysis['price_usd'] * (financial_data['bond_yields']['5_year'] / 100),
            'real_estate_funds': property_analysis['price_usd'] * (financial_data['real_estate_funds']['PROPERTY_FUND_YIELD'] / 100)
        }
        
        # Рекомендации
        recommendations = []
        if investment_analysis['net_yield_percentage'] > financial_data['deposit_rates']['USD']:
            recommendations.append("Недвижимость показывает лучшую доходность по сравнению с банковскими депозитами")
        else:
            recommendations.append("Рассмотрите банковские депозиты как альтернативу")
            
        if macro_data['inflation'] > 50:
            recommendations.append("Высокая инфляция делает недвижимость привлекательной для сохранения капитала")
            
        if regional_data['antalya_property_price_growth'] > 10:
            recommendations.append("Рост цен в Анталии указывает на потенциал прироста капитала")
            
        if risk_data['overall_risk_score'] > 7:
            recommendations.append("Учитывайте валютные риски при инвестировании")
        
        return {
            'property_analysis': property_analysis,
            'macroeconomic_data': macro_data,
            'financial_market_data': financial_data,
            'regional_indicators': regional_data,
            'tax_information': tax_data,
            'risk_assessment': risk_data,
            'investment_analysis': investment_analysis,
            'alternative_investments': alternative_investments,
            'recommendations': recommendations,
            'report_generated_at': datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка генерации полного отчета: {e}")
        return None

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
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBrDkDpNKNAIyY147MQ78hchBkeyCAxhEw&libraries=places"></script>
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
                    <div id="marketAnalysis" style="display:none;">
                        <h4>Анализ рынка в радиусе 5 км:</h4>
                        <div id="analysisResults"></div>
                    </div>
                    <div class="navigation-buttons">
                        <button class="btn" onclick="goToMainMenu()">В главное меню</button>
                    </div>
                </div>
            </div>
            
            <!-- Поиск недвижимости -->
            <div id="searchProperties" style="display:none;">
                <h3>Поиск недвижимости</h3>
                <div class="search-filters">
                    <select id="propertyType" class="input-field">
                        <option value="short_term">Краткосрочная аренда</option>
                        <option value="long_term">Долгосрочная аренда</option>
                        <option value="sale">Продажа</option>
                    </select>
                    <input type="number" id="searchBedrooms" class="input-field" placeholder="Количество спален">
                    <input type="number" id="searchPriceMin" class="input-field" placeholder="Минимальная цена">
                    <input type="number" id="searchPriceMax" class="input-field" placeholder="Максимальная цена">
                    <input type="text" id="searchCity" class="input-field" placeholder="Город">
                    <input type="text" id="searchDistrict" class="input-field" placeholder="Район">
                    <button class="btn" onclick="searchProperties()">Найти недвижимость</button>
                </div>
                <div id="searchResults"></div>
                <div class="navigation-buttons">
                    <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                </div>
            </div>
            
            <!-- Анализ ROI -->
            <div id="roiCalculator" style="display:none;">
                <h3>Калькулятор ROI</h3>
                <div class="roi-inputs">
                    <select id="roiPropertyType" class="input-field">
                        <option value="short_term">Краткосрочная аренда</option>
                        <option value="long_term">Долгосрочная аренда</option>
                    </select>
                    <input type="number" id="purchasePrice" class="input-field" placeholder="Цена покупки">
                    <input type="number" id="monthlyExpenses" class="input-field" placeholder="Месячные расходы">
                    <div id="shortTermInputs" style="display:none;">
                        <input type="number" id="avgNightlyRate" class="input-field" placeholder="Средняя цена за ночь">
                        <input type="number" id="occupancyRate" class="input-field" placeholder="Процент занятости (%)" value="75">
                    </div>
                    <div id="longTermInputs" style="display:none;">
                        <input type="number" id="monthlyRent" class="input-field" placeholder="Месячная аренда">
                    </div>
                    <button class="btn" onclick="calculateROI()">Рассчитать ROI</button>
                </div>
                <div id="roiResult"></div>
                <div class="navigation-buttons">
                    <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
                </div>
            </div>
            
            <!-- Статистика рынка -->
            <div id="marketStats" style="display:none;">
                <h3>Статистика рынка</h3>
                <div class="stats-inputs">
                    <input type="text" id="statsCity" class="input-field" placeholder="Город">
                    <input type="text" id="statsDistrict" class="input-field" placeholder="Район">
                    <button class="btn" onclick="getMarketStatistics()">Получить статистику</button>
                </div>
                <div id="statsResults"></div>
                <div class="navigation-buttons">
                    <button class="btn btn-danger" onclick="goToMainMenu()">В главное меню</button>
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
            document.getElementById('searchProperties').style.display = 'none';
            document.getElementById('roiCalculator').style.display = 'none';
            document.getElementById('marketStats').style.display = 'none';
            
            let html = '';
            for (let i = 0; i < menu.length; i++) {
                const item = menu[i];
                if (i === 0) {
                    html += `<button class="menu-btn" onclick="startNewReport()">${item}</button>`;
                } else if (i === 1) {
                    html += `<button class="menu-btn" onclick="showMarketStats()">Статистика рынка</button>`;
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
                // Загружаем карту
                loadMap(data.lat, data.lng, data.formatted_address);
            } else {
                const texts = getLocalizedTexts();
                alert(texts.address_not_found);
            }
        }

        function loadMap(lat, lng, address) {
            const mapContainer = document.getElementById('mapContainer');
            mapContainer.innerHTML = '<div id="map" style="width:100%;height:100%;border-radius:8px;"></div>';
            
            const map = new google.maps.Map(document.getElementById('map'), {
                center: { lat: parseFloat(lat), lng: parseFloat(lng) },
                zoom: 15,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: false
            });

            new google.maps.Marker({
                position: { lat: parseFloat(lat), lng: parseFloat(lng) },
                map: map,
                title: address
            });
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
            document.getElementById('searchProperties').style.display = 'none';
            document.getElementById('roiCalculator').style.display = 'none';
            document.getElementById('marketStats').style.display = 'none';
            reportData = {};
            currentStep = 'address';
            document.getElementById('addressInput').value = '';
            document.getElementById('bedroomsInput').value = '';
            document.getElementById('priceInput').value = '';
            showMenu([]);
            fetchUser();
        }

        // Новые функции для работы с недвижимостью
        function showSearchProperties() {
            menuBlock.style.display = 'none';
            document.getElementById('searchProperties').style.display = '';
        }

        function showROICalculator() {
            menuBlock.style.display = 'none';
            document.getElementById('roiCalculator').style.display = '';
            setupROICalculator();
        }

        function showMarketStats() {
            menuBlock.style.display = 'none';
            document.getElementById('marketStats').style.display = '';
        }

        function setupROICalculator() {
            const propertyType = document.getElementById('roiPropertyType');
            const shortTermInputs = document.getElementById('shortTermInputs');
            const longTermInputs = document.getElementById('longTermInputs');
            
            propertyType.addEventListener('change', function() {
                if (this.value === 'short_term') {
                    shortTermInputs.style.display = '';
                    longTermInputs.style.display = 'none';
                } else {
                    shortTermInputs.style.display = 'none';
                    longTermInputs.style.display = '';
                }
            });
        }

        async function searchProperties() {
            const propertyType = document.getElementById('propertyType').value;
            const bedrooms = document.getElementById('searchBedrooms').value;
            const priceMin = document.getElementById('searchPriceMin').value;
            const priceMax = document.getElementById('searchPriceMax').value;
            const city = document.getElementById('searchCity').value;
            const district = document.getElementById('searchDistrict').value;
            
            const searchData = {
                property_type: propertyType
            };
            
            if (bedrooms) searchData.bedrooms = parseInt(bedrooms);
            if (priceMin) searchData.price_min = parseFloat(priceMin);
            if (priceMax) searchData.price_max = parseFloat(priceMax);
            if (city) searchData.city = city;
            if (district) searchData.district = district;
            
            try {
                const res = await fetch('/api/search_properties', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(searchData)
                });
                const data = await res.json();
                
                if (data.success) {
                    displaySearchResults(data.properties, propertyType);
                } else {
                    document.getElementById('searchResults').innerHTML = '<p>Ошибка поиска</p>';
                }
            } catch (error) {
                document.getElementById('searchResults').innerHTML = '<p>Ошибка соединения</p>';
            }
        }

        function displaySearchResults(properties, propertyType) {
            const resultsDiv = document.getElementById('searchResults');
            
            if (properties.length === 0) {
                resultsDiv.innerHTML = '<p>Недвижимость не найдена</p>';
                return;
            }
            
            let html = `<h4>Найдено ${properties.length} объектов:</h4>`;
            
            properties.forEach(property => {
                const priceLabel = propertyType === 'short_term' ? 'Цена за ночь' : 
                                 propertyType === 'long_term' ? 'Месячная аренда' : 'Цена продажи';
                
                html += `
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                        <h5>${property.address}</h5>
                        <p><strong>${priceLabel}:</strong> €${property.price}</p>
                        <p><strong>Спальни:</strong> ${property.bedrooms}</p>
                        <p><strong>Ванные:</strong> ${property.bathrooms}</p>
                        <p><strong>Источник:</strong> ${property.source}</p>
                        <a href="${property.source_url}" target="_blank" class="btn">Открыть</a>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }

        async function calculateROI() {
            const propertyType = document.getElementById('roiPropertyType').value;
            const purchasePrice = document.getElementById('purchasePrice').value;
            const monthlyExpenses = document.getElementById('monthlyExpenses').value;
            
            if (!purchasePrice) {
                alert('Введите цену покупки');
                return;
            }
            
            const roiData = {
                property_type: propertyType,
                purchase_price: parseFloat(purchasePrice),
                monthly_expenses: parseFloat(monthlyExpenses) || 0
            };
            
            if (propertyType === 'short_term') {
                roiData.avg_nightly_rate = parseFloat(document.getElementById('avgNightlyRate').value) || 0;
                roiData.occupancy_rate = parseFloat(document.getElementById('occupancyRate').value) || 75;
            } else {
                roiData.monthly_rent = parseFloat(document.getElementById('monthlyRent').value) || 0;
            }
            
            try {
                const res = await fetch('/api/calculate_roi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(roiData)
                });
                const data = await res.json();
                
                if (data.success) {
                    document.getElementById('roiResult').innerHTML = `
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <h4>Результат расчета ROI:</h4>
                            <p><strong>ROI:</strong> ${data.roi}</p>
                            <p><strong>Тип недвижимости:</strong> ${propertyType === 'short_term' ? 'Краткосрочная аренда' : 'Долгосрочная аренда'}</p>
                        </div>
                    `;
                } else {
                    document.getElementById('roiResult').innerHTML = '<p>Ошибка расчета ROI</p>';
                }
            } catch (error) {
                document.getElementById('roiResult').innerHTML = '<p>Ошибка соединения</p>';
            }
        }

        async function getMarketStatistics() {
            const city = document.getElementById('statsCity').value;
            const district = document.getElementById('statsDistrict').value;
            
            if (!city || !district) {
                alert('Введите город и район');
                return;
            }
            
            try {
                const res = await fetch('/api/market_statistics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ city: city, district: district })
                });
                const data = await res.json();
                
                if (data.success) {
                    displayMarketStatistics(data.statistics);
                } else {
                    document.getElementById('statsResults').innerHTML = '<p>Ошибка получения статистики</p>';
                }
            } catch (error) {
                document.getElementById('statsResults').innerHTML = '<p>Ошибка соединения</p>';
            }
        }

        function displayMarketStatistics(statistics) {
            const resultsDiv = document.getElementById('statsResults');
            
            if (statistics.length === 0) {
                resultsDiv.innerHTML = '<p>Статистика не найдена</p>';
                return;
            }
            
            let html = '<h4>Статистика рынка:</h4>';
            
            statistics.forEach(stat => {
                const typeLabel = stat.property_type === 'short_term' ? 'Краткосрочная аренда' :
                                stat.property_type === 'long_term' ? 'Долгосрочная аренда' : 'Продажи';
                
                html += `
                    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">
                        <h5>${typeLabel}</h5>
                        <p><strong>Средняя цена:</strong> €${stat.avg_price || 0}</p>
                        <p><strong>Медианная цена:</strong> €${stat.median_price || 0}</p>
                        <p><strong>Минимальная цена:</strong> €${stat.min_price || 0}</p>
                        <p><strong>Максимальная цена:</strong> €${stat.max_price || 0}</p>
                        <p><strong>Количество объявлений:</strong> ${stat.listings_count || 0}</p>
                        ${stat.avg_rating ? `<p><strong>Средний рейтинг:</strong> ${stat.avg_rating}</p>` : ''}
                        <p><strong>Среднее количество спален:</strong> ${stat.avg_bedrooms || 0}</p>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }

        // Обновляем функцию generateReport для отображения анализа рынка
        async function generateReport() {
            const res = await fetch('/api/generate_report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    address: reportData.address,
                    bedrooms: reportData.bedrooms,
                    price: reportData.price,
                    lat: reportData.lat,
                    lng: reportData.lng,
                    language: currentLanguage,
                    telegram_id: telegramId
                })
            });
            const data = await res.json();
            document.getElementById('reportMessage').textContent = data.message;
            
            // Отображаем анализ рынка если есть данные
            if (data.analysis) {
                displayMarketAnalysis(data.analysis);
            }
        }

        function displayMarketAnalysis(analysis) {
            const analysisDiv = document.getElementById('marketAnalysis');
            const resultsDiv = document.getElementById('analysisResults');
            
            analysisDiv.style.display = '';
            
            let html = '';
            
            if (analysis.short_term_rental && analysis.short_term_rental.count > 0) {
                html += `
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                        <h5>Краткосрочная аренда (${analysis.short_term_rental.count} объектов)</h5>
                        <p>Средняя цена за ночь: €${analysis.short_term_rental.avg_price || 0}</p>
                        <p>Диапазон цен: €${analysis.short_term_rental.min_price || 0} - €${analysis.short_term_rental.max_price || 0}</p>
                        ${analysis.short_term_rental.avg_rating ? `<p>Средний рейтинг: ${analysis.short_term_rental.avg_rating}</p>` : ''}
                    </div>
                `;
            }
            
            if (analysis.long_term_rental && analysis.long_term_rental.count > 0) {
                html += `
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                        <h5>Долгосрочная аренда (${analysis.long_term_rental.count} объектов)</h5>
                        <p>Средняя месячная аренда: €${analysis.long_term_rental.avg_price || 0}</p>
                        <p>Диапазон цен: €${analysis.long_term_rental.min_price || 0} - €${analysis.long_term_rental.max_price || 0}</p>
                    </div>
                `;
            }
            
            if (analysis.property_sales && analysis.property_sales.count > 0) {
                html += `
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                        <h5>Продажи недвижимости (${analysis.property_sales.count} объектов)</h5>
                        <p>Средняя цена продажи: €${analysis.property_sales.avg_price || 0}</p>
                        <p>Диапазон цен: €${analysis.property_sales.min_price || 0} - €${analysis.property_sales.max_price || 0}</p>
                        <p>Средняя цена за кв.м: €${analysis.property_sales.avg_price_per_sqm || 0}</p>
                    </div>
                `;
            }
            
            if (html === '') {
                html = '<p>В радиусе 5 км не найдено объектов недвижимости для сравнения</p>';
            }
            
            resultsDiv.innerHTML = html;
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

@app.route('/api/user_profile', methods=['POST'])
def api_user_profile():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        result = supabase.table('users').select('first_name, last_name, photo_url, phone, email, website, company, position, about_me').eq('telegram_id', telegram_id).execute()
        if result.data and len(result.data) > 0:
            return jsonify({'success': True, 'profile': result.data[0]})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return jsonify({'error': 'Internal error'}), 500

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
    """Генерация отчета с анализом недвижимости"""
    data = request.json or {}
    address = data.get('address')
    bedrooms = data.get('bedrooms')
    price = data.get('price_usd')
    language = data.get('language', 'en')
    lat = data.get('lat')
    lng = data.get('lng')
    telegram_id = data.get('telegram_id')
    
    if not all([address, bedrooms, price]):
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Сохраняем отчет в базу данных
        report_data = {
            'user_id': telegram_id,
            'report_type': 'market_analysis',
            'title': f'Анализ недвижимости: {address}',
            'description': f'Отчет по адресу {address}, {bedrooms} спален, цена {price}',
            'parameters': {
                'address': address,
                'bedrooms': bedrooms,
                'price': price,
                'lat': lat,
                'lng': lng
            },
            'address': address,
            'latitude': lat,
            'longitude': lng,
            'bedrooms': bedrooms,
            'price_range_min': float(price) * 0.8,
            'price_range_max': float(price) * 1.2
        }
        
        # Получаем user_id из telegram_id
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        if user_result.data:
            report_data['user_id'] = user_result.data[0]['id']
            
            # Сохраняем отчет
            supabase.table('user_reports').insert(report_data).execute()
        
        # Анализируем рынок в радиусе 5 км
        market_analysis = analyze_market_around_location(lat, lng, bedrooms, float(price))
        
        # Возвращаем данные о недвижимости для отображения в WebApp
        property_info = {
            'address': address,
            'bedrooms': bedrooms,
            'price': price,
            'lat': lat,
            'lng': lng
        }
        
        return jsonify({
            'success': True,
            'message': 'Отчет сгенерирован успешно',
            'property_info': property_info,
            'analysis': market_analysis
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({
            'success': True,
            'message': 'Отчет сгенерирован успешно',
            'property_info': {
                'address': address,
                'bedrooms': bedrooms,
                'price': price
            }
        })

def analyze_market_around_location(lat, lng, bedrooms, target_price):
    """Анализ рынка недвижимости вокруг указанной локации"""
    import logging
    try:
        radius_km = 5.0
        # Поиск краткосрочной аренды
        short_term_props = find_properties_in_radius(lat, lng, radius_km, 'short_term')
        short_term_props = [p for p in short_term_props if str(p.get('bedrooms')) == str(bedrooms)]
        logging.info(f"Short-term found: {len(short_term_props)}")
        for p in short_term_props:
            logging.info(f"Short-term: {p.get('address')} ({p.get('latitude')}, {p.get('longitude')}) dist={p.get('distance_km')}")
        
        # Поиск долгосрочной аренды
        long_term_props = find_properties_in_radius(lat, lng, radius_km, 'long_term')
        long_term_props = [p for p in long_term_props if str(p.get('bedrooms')) == str(bedrooms)]
        logging.info(f"Long-term found: {len(long_term_props)}")
        for p in long_term_props:
            logging.info(f"Long-term: {p.get('address')} ({p.get('latitude')}, {p.get('longitude')}) dist={p.get('distance_km')}")
        
        # Поиск продаж
        sales_props = find_properties_in_radius(lat, lng, radius_km, 'sale')
        sales_props = [p for p in sales_props if str(p.get('bedrooms')) == str(bedrooms)]
        logging.info(f"Sales found: {len(sales_props)}")
        for p in sales_props:
            logging.info(f"Sale: {p.get('address')} ({p.get('latitude')}, {p.get('longitude')}) dist={p.get('distance_km')}")
        
        def summarize(props, price_key):
            if not props:
                return {}
            prices = [float(p.get(price_key, 0)) for p in props if p.get(price_key) is not None]
            return {
                'count': len(props),
                'avg_price': sum(prices)/len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
            }
        
        return {
            'short_term_rental': summarize(short_term_props, 'price'),
            'long_term_rental': summarize(long_term_props, 'price'),
            'property_sales': summarize(sales_props, 'price'),
            'target_price': target_price,
            'radius_km': radius_km
        }
    except Exception as e:
        logging.error(f"Error analyzing market: {e}")
        return {}

@app.route('/api/search_properties', methods=['POST'])
def api_search_properties():
    """Поиск недвижимости по параметрам"""
    data = request.json or {}
    property_type = data.get('property_type', 'short_term')  # short_term, long_term, sale
    bedrooms = data.get('bedrooms')
    price_min = data.get('price_min')
    price_max = data.get('price_max')
    city = data.get('city')
    district = data.get('district')
    lat = data.get('lat')
    lng = data.get('lng')
    radius_km = data.get('radius_km', 5.0)
    
    try:
        if lat and lng:
            # Поиск по радиусу
            properties = find_properties_in_radius(lat, lng, radius_km, property_type)
        else:
            # Поиск по параметрам
            properties = find_properties_by_params(property_type, bedrooms, price_min, price_max, city, district)
        
        return jsonify({
            'success': True,
            'properties': properties,
            'count': len(properties)
        })
        
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return jsonify({'error': 'Search error'}), 500

def find_properties_in_radius(lat, lng, radius_km, property_type):
    """Поиск недвижимости в радиусе"""
    try:
        # Прямой SQL запрос вместо RPC
        table_name = {
            'short_term': 'short_term_rentals',
            'long_term': 'long_term_rentals',
            'sale': 'property_sales'
        }.get(property_type, 'short_term_rentals')
        
        price_column = {
            'short_term': 'price_per_night',
            'long_term': 'monthly_rent',
            'sale': 'asking_price'
        }.get(property_type, 'price_per_night')
        
        # Получаем все активные записи с координатами
        result = supabase.table(table_name).select('*').eq('is_active', True).execute()
        
        # Фильтруем результаты по расстоянию на стороне Python
        filtered_results = []
        for item in result.data:
            if item.get('latitude') and item.get('longitude'):
                # Рассчитываем расстояние
                import math
                lat1, lon1 = float(lat), float(lng)
                lat2, lon2 = float(item['latitude']), float(item['longitude'])
                
                # Формула гаверсинуса
                R = 6371  # Радиус Земли в км
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                     math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                     math.sin(dlon/2) * math.sin(dlon/2))
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c
                
                if distance <= radius_km:
                    item['distance_km'] = round(distance, 2)
                    item['property_type'] = property_type
                    item['price'] = item.get(price_column, 0)
                    filtered_results.append(item)
        
        # Сортируем по расстоянию
        filtered_results.sort(key=lambda x: x['distance_km'])
        return filtered_results[:50]  # Ограничиваем 50 результатами
        
    except Exception as e:
        logger.error(f"Error in radius search: {e}")
        return []

def find_properties_by_params(property_type, bedrooms, price_min, price_max, city, district):
    """Поиск недвижимости по параметрам"""
    try:
        table_name = {
            'short_term': 'short_term_rentals',
            'long_term': 'long_term_rentals',
            'sale': 'property_sales'
        }.get(property_type, 'short_term_rentals')
        
        price_column = {
            'short_term': 'price_per_night',
            'long_term': 'monthly_rent',
            'sale': 'asking_price'
        }.get(property_type, 'price_per_night')
        
        # Начинаем с базового запроса
        query = supabase.table(table_name).select('*').eq('is_active', True)
        
        # Добавляем фильтры
        if bedrooms:
            query = query.eq('bedrooms', bedrooms)
        if price_min:
            query = query.gte(price_column, price_min)
        if price_max:
            query = query.lte(price_column, price_max)
        if city:
            query = query.ilike('city', f'%{city}%')
        if district:
            query = query.ilike('district', f'%{district}%')
        
        # Выполняем запрос
        result = query.execute()
        
        # Преобразуем результаты
        properties = []
        for item in result.data:
            properties.append({
                'property_id': item.get('property_id'),
                'address': item.get('address'),
                'latitude': item.get('latitude'),
                'longitude': item.get('longitude'),
                'price': item.get(price_column, 0),
                'bedrooms': item.get('bedrooms'),
                'bathrooms': item.get('bathrooms'),
                'source': item.get('source'),
                'source_url': item.get('source_url'),
                'updated_at': item.get('updated_at')
            })
        
        # Сортируем по цене
        properties.sort(key=lambda x: x['price'])
        return properties[:50]  # Ограничиваем 50 результатами
        
    except Exception as e:
        logger.error(f"Error in params search: {e}")
        return []

@app.route('/api/market_statistics', methods=['POST'])
def api_market_statistics():
    """Получение статистики рынка"""
    data = request.json or {}
    district = data.get('district')
    city = data.get('city')
    
    if not district or not city:
        return jsonify({'error': 'District and city required'}), 400
    
    try:
        statistics = []
        
        # Статистика по краткосрочной аренде
        short_term_result = supabase.table('short_term_rentals').select('price_per_night, bedrooms, avg_rating').eq('is_active', True).eq('district', district).eq('city', city).execute()
        if short_term_result.data:
            prices = [float(item['price_per_night']) for item in short_term_result.data if item.get('price_per_night')]
            bedrooms_list = [item['bedrooms'] for item in short_term_result.data if item.get('bedrooms')]
            ratings = [float(item['avg_rating']) for item in short_term_result.data if item.get('avg_rating')]
            
            if prices:
                statistics.append({
                    'property_type': 'short_term',
                    'avg_price': sum(prices) / len(prices),
                    'median_price': sorted(prices)[len(prices)//2] if prices else 0,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(short_term_result.data),
                    'avg_rating': sum(ratings) / len(ratings) if ratings else None,
                    'avg_bedrooms': sum(bedrooms_list) / len(bedrooms_list) if bedrooms_list else 0
                })
        
        # Статистика по долгосрочной аренде
        long_term_result = supabase.table('long_term_rentals').select('monthly_rent, bedrooms').eq('is_active', True).eq('district', district).eq('city', city).execute()
        if long_term_result.data:
            prices = [float(item['monthly_rent']) for item in long_term_result.data if item.get('monthly_rent')]
            bedrooms_list = [item['bedrooms'] for item in long_term_result.data if item.get('bedrooms')]
            
            if prices:
                statistics.append({
                    'property_type': 'long_term',
                    'avg_price': sum(prices) / len(prices),
                    'median_price': sorted(prices)[len(prices)//2] if prices else 0,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(long_term_result.data),
                    'avg_rating': None,
                    'avg_bedrooms': sum(bedrooms_list) / len(bedrooms_list) if bedrooms_list else 0
                })
        
        # Статистика по продажам
        sales_result = supabase.table('property_sales').select('asking_price, bedrooms, price_per_sqm').eq('is_active', True).eq('district', district).eq('city', city).execute()
        if sales_result.data:
            prices = [float(item['asking_price']) for item in sales_result.data if item.get('asking_price')]
            bedrooms_list = [item['bedrooms'] for item in sales_result.data if item.get('bedrooms')]
            
            if prices:
                statistics.append({
                    'property_type': 'sale',
                    'avg_price': sum(prices) / len(prices),
                    'median_price': sorted(prices)[len(prices)//2] if prices else 0,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'listings_count': len(sales_result.data),
                    'avg_rating': None,
                    'avg_bedrooms': sum(bedrooms_list) / len(bedrooms_list) if bedrooms_list else 0
                })
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': 'Statistics error'}), 500

@app.route('/api/calculate_roi', methods=['POST'])
def api_calculate_roi():
    """Расчет ROI для инвестиций"""
    data = request.json or {}
    property_type = data.get('property_type', 'short_term')
    purchase_price = data.get('purchase_price')
    monthly_expenses = data.get('monthly_expenses', 0)
    
    if not purchase_price:
        return jsonify({'error': 'Purchase price required'}), 400
    
    try:
        if property_type == 'short_term':
            avg_nightly_rate = data.get('avg_nightly_rate', 0)
            occupancy_rate = data.get('occupancy_rate', 75)
            
            # Используем функцию ROI из базы данных
            result = supabase.rpc('calculate_short_term_roi', {
                'purchase_price': purchase_price,
                'monthly_expenses': monthly_expenses,
                'avg_nightly_rate': avg_nightly_rate,
                'occupancy_rate': occupancy_rate
            }).execute()
        else:
            monthly_rent = data.get('monthly_rent', 0)
            
            result = supabase.rpc('calculate_long_term_roi', {
                'purchase_price': purchase_price,
                'monthly_expenses': monthly_expenses,
                'monthly_rent': monthly_rent
            }).execute()
        
        roi = result.data[0]['roi'] if result.data else 0
        
        return jsonify({
            'success': True,
            'roi': roi,
            'roi_percentage': f"{roi:.2f}%"
        })
        
    except Exception as e:
        logger.error(f"Error calculating ROI: {e}")
        return jsonify({'error': 'ROI calculation error'}), 500

@app.route('/api/similar_properties', methods=['POST'])
def api_similar_properties():
    """Поиск похожих объектов"""
    data = request.json or {}
    bedrooms = data.get('bedrooms')
    price_min = data.get('price_min')
    price_max = data.get('price_max')
    city = data.get('city')
    district = data.get('district')
    property_type = data.get('property_type', 'short_term')
    
    if not all([bedrooms, price_min, price_max, city]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Используем функцию поиска похожих объектов
        result = supabase.rpc('find_similar_properties', {
            'p_bedrooms': bedrooms,
            'p_price_min': price_min,
            'p_price_max': price_max,
            'p_city': city,
            'p_district': district,
            'p_property_type': property_type
        }).execute()
        
        return jsonify({
            'success': True,
            'properties': result.data if result.data else []
        })
        
    except Exception as e:
        logger.error(f"Error finding similar properties: {e}")
        return jsonify({'error': 'Similar properties search error'}), 500

@app.route('/api/full_report', methods=['POST'])
def api_full_report():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    property_data = data.get('property_data', {})

    if not telegram_id or not property_data:
        return jsonify({'error': 'telegram_id and property_data required'}), 400

    # Проверка баланса
    try:
        bal_result = supabase.table('user_balance').select('balance_usd').eq('telegram_id', telegram_id).execute()
        balance = float(bal_result.data[0]['balance_usd']) if bal_result.data and len(bal_result.data) > 0 else 0.0
        if balance < 1.0:
            return jsonify({'success': False, 'insufficient_balance': True, 'message': 'Недостаточно средств на балансе'}), 200
        
        # Списываем $1
        new_balance = balance - 1.0
        if bal_result.data and len(bal_result.data) > 0:
            supabase.table('user_balance').update({'balance_usd': new_balance}).eq('telegram_id', telegram_id).execute()
        else:
            supabase.table('user_balance').insert({'telegram_id': telegram_id, 'balance_usd': new_balance}).execute()
    except Exception as e:
        logger.error(f"Error checking/updating balance: {e}")
        return jsonify({'error': 'Internal error'}), 500

    # Генерируем полный отчет с макроэкономическими данными
    report = generate_comprehensive_report(property_data, telegram_id)
    
    if not report:
        return jsonify({'error': 'Failed to generate report'}), 500

    return jsonify({'success': True, 'report': report})

@app.route('/api/save_object', methods=['POST'])
def api_save_object():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    object_data = data.get('object_data', {})
    if not telegram_id or not object_data:
        return jsonify({'error': 'telegram_id and object_data required'}), 400
    try:
        # Сохраняем объект в таблицу user_objects (создать если нет)
        result = supabase.table('user_objects').insert({
            'telegram_id': telegram_id,
            'object_data': object_data,
            'created_at': datetime.datetime.utcnow().isoformat()
        }).execute()
        return jsonify({'success': True, 'object_id': result.data[0]['id'] if result.data else None})
    except Exception as e:
        logger.error(f"Error saving object: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/generate_pdf_report', methods=['POST'])
def api_generate_pdf_report():
    data = request.json or {}
    property_data = data.get('property_data', {})
    full_report = data.get('full_report', {})
    client_name = data.get('client_name', '')
    client_telegram = data.get('client_telegram', '')
    include_macro = data.get('include_macro', True)
    include_financial = data.get('include_financial', True)
    include_regional = data.get('include_regional', True)
    include_tax = data.get('include_tax', True)
    include_risk = data.get('include_risk', True)
    telegram_id = data.get('telegram_id')

    if not property_data:
        return jsonify({'error': 'property_data required'}), 400

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Полный отчет по недвижимости', ln=1)
        pdf.ln(5)

        # Информация о недвижимости
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Информация об объекте', ln=1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Адрес: {property_data.get('address', 'Не указан')}", ln=1)
        pdf.cell(0, 8, f"Спальни: {property_data.get('bedrooms', 0)}", ln=1)
        pdf.cell(0, 8, f"Цена: ${property_data.get('price', 0):,.0f}", ln=1)
        pdf.ln(5)

        if full_report:
            # Макроэкономические данные
            if include_macro and full_report.get('macroeconomic_data'):
                macro = full_report['macroeconomic_data']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Макроэкономические показатели', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Инфляция: {macro.get('inflation', 0)}%", ln=1)
                pdf.cell(0, 8, f"Курс USD/TRY: {macro.get('currency_rate', 0)}", ln=1)
                pdf.cell(0, 8, f"Ставка ЦБ: {macro.get('interest_rate', 0)}%", ln=1)
                pdf.cell(0, 8, f"Рост ВВП: {macro.get('gdp_growth', 0)}%", ln=1)
                pdf.ln(5)

            # Финансовые данные
            if include_financial and full_report.get('financial_market_data'):
                financial = full_report['financial_market_data']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Финансовые показатели', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Депозиты TRY: {financial.get('deposit_rates', {}).get('TRY', 0)}%", ln=1)
                pdf.cell(0, 8, f"Депозиты USD: {financial.get('deposit_rates', {}).get('USD', 0)}%", ln=1)
                pdf.cell(0, 8, f"Облигации 5 лет: {financial.get('bond_yields', {}).get('5_year', 0)}%", ln=1)
                pdf.cell(0, 8, f"Фонды недвижимости: {financial.get('real_estate_funds', {}).get('PROPERTY_FUND_YIELD', 0)}%", ln=1)
                pdf.ln(5)

            # Региональные показатели
            if include_regional and full_report.get('regional_indicators'):
                regional = full_report['regional_indicators']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Региональные показатели Анталии', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Рост цен недвижимости: {regional.get('antalya_property_price_growth', 0)}%", ln=1)
                pdf.cell(0, 8, f"Доходность аренды: {regional.get('antalya_rental_yield', 0)}%", ln=1)
                pdf.cell(0, 8, f"Рост туризма: {regional.get('antalya_tourism_growth', 0)}%", ln=1)
                pdf.cell(0, 8, f"Рост ВВП региона: {regional.get('antalya_gdp_growth', 0)}%", ln=1)
                pdf.ln(5)

            # Инвестиционный анализ
            if full_report.get('investment_analysis'):
                investment = full_report['investment_analysis']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Инвестиционный анализ', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Доходность аренды: {investment.get('rental_yield_percentage', 0):.1f}%", ln=1)
                pdf.cell(0, 8, f"Чистая доходность: {investment.get('net_yield_percentage', 0):.1f}%", ln=1)
                pdf.cell(0, 8, f"Месячная аренда: ${investment.get('monthly_rent_estimate', 0):.0f}", ln=1)
                pdf.cell(0, 8, f"Годовой доход: ${investment.get('net_annual_income', 0):.0f}", ln=1)
                pdf.ln(5)

            # Налоговая информация
            if include_tax and full_report.get('tax_information'):
                tax = full_report['tax_information']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Налоговая информация', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Налог на недвижимость: {tax.get('property_tax_rate', 0)}%", ln=1)
                pdf.cell(0, 8, f"Налог на арендный доход: {tax.get('rental_income_tax', 0)}%", ln=1)
                pdf.cell(0, 8, f"Пошлина при покупке: {tax.get('stamp_duty', 0)}%", ln=1)
                pdf.cell(0, 8, f"Нотариальные услуги: {tax.get('notary_fee', 0)}%", ln=1)
                pdf.ln(5)

            # Оценка рисков
            if include_risk and full_report.get('risk_assessment'):
                risk = full_report['risk_assessment']
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Оценка рисков', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 8, f"Валютный риск: {risk.get('currency_risk', 'Неизвестно')}", ln=1)
                pdf.cell(0, 8, f"Политический риск: {risk.get('political_risk', 'Неизвестно')}", ln=1)
                pdf.cell(0, 8, f"Экономический риск: {risk.get('economic_risk', 'Неизвестно')}", ln=1)
                pdf.cell(0, 8, f"Общий риск: {risk.get('overall_risk_score', 0)}/10", ln=1)
                pdf.ln(5)

            # Рекомендации
            if full_report.get('recommendations'):
                pdf.set_font('Arial', 'B', 13)
                pdf.cell(0, 10, 'Рекомендации', ln=1)
                pdf.set_font('Arial', '', 12)
                for rec in full_report['recommendations']:
                    pdf.cell(0, 8, f"• {rec}", ln=1)
                pdf.ln(5)

        # Информация о клиенте
        if client_name or client_telegram:
            pdf.set_font('Arial', 'B', 13)
            pdf.cell(0, 10, 'Информация о клиенте', ln=1)
            pdf.set_font('Arial', '', 12)
            if client_name:
                pdf.cell(0, 8, f"Имя: {client_name}", ln=1)
            if client_telegram:
                pdf.cell(0, 8, f"Telegram: {client_telegram}", ln=1)
            pdf.ln(5)

        # Дата генерации
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Отчет сгенерирован: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=1)

        # Сохраняем PDF
        pdf_filename = f"report_{telegram_id}_{int(datetime.datetime.now().timestamp())}.pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf.output(tmp_pdf.name)
            pdf_path = tmp_pdf.name

        return jsonify({'success': True, 'pdf_filename': pdf_filename, 'pdf_path': pdf_path})

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/download_pdf', methods=['POST'])
def api_download_pdf():
    data = request.json or {}
    pdf_filename = data.get('pdf_filename')
    telegram_id = data.get('telegram_id')
    
    if not pdf_filename or not telegram_id:
        return jsonify({'error': 'pdf_filename and telegram_id required'}), 400
    
    # Создаем путь к PDF файлу
    pdf_path = f"/tmp/{pdf_filename}"
    
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF not found'}), 404
    
    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

import threading

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

@app.route('/api/user_balance', methods=['POST'])
def api_user_balance():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        result = supabase.table('user_balance').select('balance_usd').eq('telegram_id', telegram_id).execute()
        if result.data and len(result.data) > 0:
            return jsonify({'success': True, 'balance': float(result.data[0]['balance_usd'])})
        else:
            return jsonify({'success': True, 'balance': 0.0})
    except Exception as e:
        logger.error(f"Error fetching user balance: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/send_pdf_to_client', methods=['POST'])
def api_send_pdf_to_client():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    client_name = data.get('client_name', '')
    client_telegram = data.get('client_telegram', '')
    property_data = data.get('property_data', {})

    if not telegram_id or not client_telegram:
        return jsonify({'error': 'telegram_id and client_telegram required'}), 400

    try:
        # Сохраняем контакт клиента
        supabase.table('client_contacts').insert({
            'realtor_telegram_id': telegram_id,
            'client_name': client_name,
            'client_telegram': client_telegram,
            'property_data': property_data,
            'created_at': datetime.datetime.utcnow().isoformat()
        }).execute()

        # Отправляем сообщение клиенту через Telegram Bot
        try:
            bot = Bot(token=TOKEN)
            
            # Формируем сообщение
            message = f"🏠 Отчет по недвижимости\n\n"
            if client_name:
                message += f"Клиент: {client_name}\n"
            message += f"Адрес: {property_data.get('address', 'Не указан')}\n"
            message += f"Спальни: {property_data.get('bedrooms', 0)}\n"
            message += f"Цена: ${property_data.get('price', 0):,.0f}\n\n"
            message += "Полный отчет будет отправлен в следующем сообщении."

            # Отправляем текстовое сообщение
            bot.send_message(chat_id=client_telegram, text=message)
            
            return jsonify({'success': True, 'message': 'Сообщение отправлено клиенту'})
            
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            return jsonify({'success': False, 'error': 'Не удалось отправить сообщение клиенту'})

    except Exception as e:
        logger.error(f"Error sending PDF to client: {e}")
        return jsonify({'error': 'Internal error'}), 500

if __name__ == '__main__':
    # Запускаем Flask-сервер в отдельном потоке-демоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем Telegram-бота в главном потоке
    main() 