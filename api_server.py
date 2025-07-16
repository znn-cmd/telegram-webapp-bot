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
from supabase import create_client, Client
from locales import locales

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для WebApp

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL и SUPABASE_KEY должны быть заданы в переменных окружения!")
supabase: Client = create_client(supabase_url, supabase_key)

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

@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    username = data.get('username')
    first_name = data.get('tg_name')
    last_name = data.get('last_name')
    language_code = data.get('language_code', 'en')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    # Проверяем пользователя в базе
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if user:
        lang = user.get('language') or (language_code[:2] if language_code[:2] in locales else 'en')
        return jsonify({
            'exists': True,
            'is_new_user': False,
            'language': user.get('language') or lang,
            'language_code': lang,
            'welcome': locales[lang]['welcome_back'],
            'menu': locales[lang]['menu'],
            'name': user.get('name'),
            'tg_name': user.get('tg_name'),
            'last_name': user.get('last_name'),
            'username': user.get('username'),
            'balance': user.get('balance', 0),
            'telegram_id': user.get('telegram_id'),
            'user_status': user.get('user_status', None),
        })
    else:
        # Новый пользователь
        lang = language_code[:2] if language_code[:2] in locales else 'en'
        supabase.table('users').insert({
            'telegram_id': telegram_id,
            'username': username,
            'tg_name': first_name,
            'last_name': last_name,
            'language': lang,
            'balance': 0
        }).execute()
        return jsonify({
            'exists': False,
            'is_new_user': True,
            'language': lang,
            'language_code': lang,
            'welcome': locales[lang]['welcome_new'],
            'choose_language': locales[lang]['choose_language'],
            'languages': locales[lang]['language_names'],
            'balance': 0,
            'telegram_id': telegram_id,
            'user_status': None,
        })

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
        report_cost = 1.0
        
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

@app.route('/api/admin_set_balance', methods=['POST'])
def admin_set_balance():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    # Проверяем, что вызывающий пользователь — admin
    user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if not user or user.get('user_status') != 'admin':
        return jsonify({'error': 'not allowed'}), 403
    # Устанавливаем баланс 100
    supabase.table('users').update({'balance': 100}).eq('telegram_id', telegram_id).execute()
    return jsonify({'success': True, 'balance': 100})

@app.route('/api/admin_user_stats', methods=['POST'])
def admin_user_stats():
    import datetime
    from dateutil.relativedelta import relativedelta
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    # Проверяем, что вызывающий пользователь — admin
    user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if not user or user.get('user_status') != 'admin':
        return jsonify({'error': 'not allowed'}), 403
    # Даты для фильтрации
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - relativedelta(months=1)
    quarter_ago = today - relativedelta(months=3)
    year_ago = today - relativedelta(years=1)
    # Пользователи (без админов)
    users = supabase.table('users').select('*').neq('user_status', 'admin').execute().data
    all_users = supabase.table('users').select('*').execute().data
    # Новые пользователи
    def count_new(users, date_field, since):
        return sum(1 for u in users if u.get(date_field) and u[date_field][:10] >= str(since))
    total_users = len(users)
    new_week = count_new(users, 'created_at', week_ago)
    new_month = count_new(users, 'created_at', month_ago)
    new_quarter = count_new(users, 'created_at', quarter_ago)
    new_year = count_new(users, 'created_at', year_ago)
    # Балансы
    total_balance = sum(u.get('balance', 0) or 0 for u in users)
    expired_users = [u for u in users if (u.get('period_end') and u['period_end'] < str(today)) or (u.get('period_end') is None)]
    expired_balance = sum(u.get('balance', 0) or 0 for u in expired_users)
    active_users = [u for u in users if not ((u.get('period_end') and u['period_end'] < str(today)) or (u.get('period_end') is None))]
    active_balance = sum(u.get('balance', 0) or 0 for u in active_users)
    # Отчеты
    reports = supabase.table('user_reports').select('*').execute().data
    def count_reports(since):
        return sum(1 for r in reports if r.get('created_at') and r['created_at'][:10] >= str(since))
    reports_week = count_reports(week_ago)
    reports_month = count_reports(month_ago)
    reports_quarter = count_reports(quarter_ago)
    reports_year = count_reports(year_ago)
    deleted_reports = sum(1 for r in reports if r.get('deleted_at'))
    # Отчеты по expired/active
    expired_user_ids = set(u['telegram_id'] for u in expired_users)
    active_user_ids = set(u['telegram_id'] for u in active_users)
    expired_reports = [r for r in reports if r.get('user_id') in expired_user_ids]
    active_reports = [r for r in reports if r.get('user_id') in active_user_ids]
    avg_expired_reports = len(expired_reports) / len(expired_user_ids) if expired_user_ids else 0
    # Сумма денег за отчеты active
    tariffs = supabase.table('tariffs').select('*').execute().data
    full_price = 0
    for t in tariffs:
        if t.get('name') == 'full':
            full_price = t.get('price', 100)
            break
    active_reports_money = len(active_reports) * full_price
    return jsonify({
        'total_users': total_users,
        'new_week': new_week,
        'new_month': new_month,
        'new_quarter': new_quarter,
        'new_year': new_year,
        'total_balance': total_balance,
        'expired_balance': expired_balance,
        'active_balance': active_balance,
        'reports_week': reports_week,
        'reports_month': reports_month,
        'reports_quarter': reports_quarter,
        'reports_year': reports_year,
        'deleted_reports': deleted_reports,
        'expired_reports_count': len(expired_reports),
        'avg_expired_reports': avg_expired_reports,
        'active_reports_count': len(active_reports),
        'active_reports_money': active_reports_money
    })

@app.route('/api/admin_publish', methods=['POST'])
def admin_publish():
    import requests
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    text = data.get('text')
    if not telegram_id or not text:
        return jsonify({'error': 'telegram_id and text required'}), 400
    # Проверяем, что вызывающий пользователь — admin
    user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if not user or user.get('user_status') != 'admin':
        return jsonify({'error': 'not allowed'}), 403
    # Получаем всех пользователей
    all_users = supabase.table('users').select('telegram_id, user_status').execute().data
    admin_count = 0
    user_count = 0
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    for u in all_users:
        uid = u.get('telegram_id')
        if not uid:
            continue
        payload = {
            'chat_id': uid,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        try:
            resp = requests.post(send_url, json=payload, timeout=5)
            if u.get('user_status') == 'admin':
                admin_count += 1
            else:
                user_count += 1
        except Exception:
            pass
    return jsonify({'success': True, 'admins': admin_count, 'users': user_count})

@app.route('/api/admin_api_keys', methods=['GET', 'POST'])
def admin_api_keys():
    if request.method == 'GET':
        telegram_id = request.args.get('telegram_id')
        if not telegram_id:
            return jsonify({'error': 'telegram_id required'}), 400
        user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
        user = user_result.data[0] if user_result.data else None
        if not user or user.get('user_status') != 'admin':
            return jsonify({'error': 'not allowed'}), 403
        keys = supabase.table('api_keys').select('*').execute().data
        return jsonify({'success': True, 'keys': keys})
    elif request.method == 'POST':
        data = request.json or {}
        telegram_id = data.get('telegram_id')
        key_name = data.get('key_name')
        key_value = data.get('key_value')
        if not telegram_id or not key_name or not key_value:
            return jsonify({'error': 'telegram_id, key_name, key_value required'}), 400
        user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
        user = user_result.data[0] if user_result.data else None
        if not user or user.get('user_status') != 'admin':
            return jsonify({'error': 'not allowed'}), 403
        # Обновить или добавить ключ
        existing = supabase.table('api_keys').select('*').eq('key_name', key_name).execute().data
        if existing:
            supabase.table('api_keys').update({'key_value': key_value}).eq('key_name', key_name).execute()
        else:
            supabase.table('api_keys').insert({'key_name': key_name, 'key_value': key_value}).execute()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'method not allowed'}), 405

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