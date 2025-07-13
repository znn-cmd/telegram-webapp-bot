from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from api_functions import (
    generate_basic_report,
    get_user_balance,
    charge_user_for_report,
    update_user_balance
)

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для WebApp

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Генерация базового отчета по координатам"""
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        telegram_id = data.get('telegram_id')
        
        if not lat or not lon:
            return jsonify({'error': True, 'message': 'Координаты не указаны'}), 400
        
        # Генерируем отчет
        report = generate_basic_report(lat, lon)
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

@app.route('/api/user-balance', methods=['POST'])
def user_balance():
    """Получение баланса пользователя"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'error': True, 'message': 'ID пользователя не указан'}), 400
        
        balance = get_user_balance(telegram_id)
        
        return jsonify({'balance': balance})
        
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

@app.route('/api/full-report', methods=['POST'])
def full_report():
    """Получение полного отчета (платный)"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        report_data = data.get('report_data')
        
        if not telegram_id:
            return jsonify({'error': True, 'message': 'ID пользователя не указан'}), 400
        
        # Проверяем баланс пользователя
        balance = get_user_balance(telegram_id)
        report_cost = 15.0
        
        if balance < report_cost:
            return jsonify({
                'success': False,
                'insufficient_balance': True,
                'message': 'Недостаточно средств на балансе',
                'required': report_cost,
                'current': balance
            })
        
        # Списываем средства
        if charge_user_for_report(telegram_id, report_cost):
            # Генерируем полный отчет
            full_report_data = generate_full_report(report_data)
            
            return jsonify({
                'success': True,
                'report': full_report_data,
                'balance_after': balance - report_cost
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка списания средств'
            }), 500
        
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

@app.route('/api/top-up-balance', methods=['POST'])
def top_up_balance():
    """Пополнение баланса пользователя"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        amount = data.get('amount', 0)
        
        if not telegram_id:
            return jsonify({'error': True, 'message': 'ID пользователя не указан'}), 400
        
        if amount <= 0:
            return jsonify({'error': True, 'message': 'Сумма должна быть больше 0'}), 400
        
        # Пополняем баланс
        if update_user_balance(telegram_id, amount):
            new_balance = get_user_balance(telegram_id)
            return jsonify({
                'success': True,
                'balance': new_balance,
                'message': f'Баланс пополнен на ${amount}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка пополнения баланса'
            }), 500
        
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

def generate_full_report(basic_report_data):
    """Генерация полного отчета на основе базового"""
    
    # Здесь можно добавить более сложную логику анализа
    # Пока используем базовые данные с дополнительной информацией
    
    district = basic_report_data.get('district', 'Неизвестный район')
    property_type = basic_report_data.get('property_type', 'недвижимость')
    metrics = basic_report_data.get('metrics', {})
    
    # Прогноз цен на основе текущих метрик
    current_price = metrics.get('avg_price_per_sqm', 2500)
    price_growth = 0.08  # 8% рост
    forecast_price = current_price * (1 + price_growth)
    
    # Анализ конкурентов (заглушка)
    competitor_analysis = {
        'total_analyzed': 25,
        'price_range': f"${current_price * 0.8:.0f} - ${current_price * 1.2:.0f}",
        'market_share': '15%',
        'top_competitors': [
            'Lara Beach Properties',
            'Kaleiçi Real Estate',
            'Antalya Premium Homes'
        ]
    }
    
    # Кастомные рекомендации
    recommendations = [
        f"Инвестируйте в {district} - ожидается рост цен на {price_growth * 100:.0f}%",
        "Фокус на объекты с паркингом - спрос выше на 30%",
        "Оптимальное время для покупки - Q2 2025",
        f"Рассмотрите {property_type} в соседних районах для диверсификации"
    ]
    
    return {
        'title': f'Полный анализ рынка недвижимости: {district}',
        'basic_metrics': metrics,
        'price_forecast': {
            'current_price': current_price,
            'forecast_price': forecast_price,
            'growth_percentage': price_growth * 100,
            'year': 2025
        },
        'competitor_analysis': competitor_analysis,
        'recommendations': recommendations,
        'market_trends': {
            'demand_trend': 'Растущий',
            'supply_trend': 'Стабильный',
            'price_trend': 'Растущий',
            'seasonality': 'Пик в июле-августе'
        },
        'investment_opportunities': [
            {
                'type': 'Краткосрочная аренда',
                'roi': '12-18%',
                'risk': 'Средний',
                'recommendation': 'Подходит для активных инвесторов'
            },
            {
                'type': 'Долгосрочная аренда',
                'roi': '6-10%',
                'risk': 'Низкий',
                'recommendation': 'Стабильный доход'
            },
            {
                'type': 'Перепродажа',
                'roi': '15-25%',
                'risk': 'Высокий',
                'recommendation': 'Требует глубокого анализа'
            }
        ]
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    return jsonify({'status': 'ok', 'message': 'API работает'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 