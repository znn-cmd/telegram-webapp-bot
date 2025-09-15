import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def convert_datetime_to_string(obj):
    """Конвертирует объекты datetime в строки для JSON сериализации"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    else:
        return obj

class DashboardAPI:
    def __init__(self):
        self.headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
        }
    
    def get_users_stats(self) -> Dict[str, Any]:
        """Получение статистики пользователей"""
        try:
            # Общее количество уникальных пользователей (по telegram_id)
            url = f"{SUPABASE_URL}/rest/v1/users?select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                total_users = len(telegram_ids)
            else:
                total_users = 0
            
            # Пользователи за последние 30 дней
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{thirty_days_ago}&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                new_users_30d = len(telegram_ids)
            else:
                new_users_30d = 0
            
            # Пользователи за последние 7 дней
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{seven_days_ago}&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                new_users_7d = len(telegram_ids)
            else:
                new_users_7d = 0
            
            # Активные пользователи (с активностью за последние 7 дней)
            url = f"{SUPABASE_URL}/rest/v1/users?last_activity=gte.{seven_days_ago}&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                active_users = len(telegram_ids)
            else:
                active_users = 0
            
            # Пользователи с балансом
            url = f"{SUPABASE_URL}/rest/v1/users?balance=gt.0&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                users_with_balance = len(telegram_ids)
            else:
                users_with_balance = 0
            
            # Статистика подписок
            today = datetime.now().isoformat()
            
            # Пользователи с действующей подпиской (period_end > сегодня)
            url = f"{SUPABASE_URL}/rest/v1/users?period_end=gt.{today}&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                active_subscriptions = len(telegram_ids)
            else:
                active_subscriptions = 0
            
            # Пользователи с истекшей подпиской (period_end < сегодня)
            url = f"{SUPABASE_URL}/rest/v1/users?period_end=lt.{today}&period_end=not.is.null&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                expired_subscriptions = len(telegram_ids)
            else:
                expired_subscriptions = 0
            
            # Неактивные пользователи (last_activity < периода отчета)
            # Используем фиксированный период 30 дней, так как request недоступен в этом контексте
            period_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/users?last_activity=lt.{period_days_ago}&select=telegram_id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                telegram_ids = set()
                for user in response.json():
                    telegram_id = user.get('telegram_id')
                    if telegram_id:
                        telegram_ids.add(telegram_id)
                inactive_users = len(telegram_ids)
            else:
                inactive_users = 0
            
            # Топ языки пользователей
            url = f"{SUPABASE_URL}/rest/v1/users?select=language"
            response = requests.get(url, headers=self.headers)
            languages = {}
            if response.status_code == 200:
                for user in response.json():
                    lang = user.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
            
            return {
                'total_users': total_users,
                'new_users_30d': new_users_30d,
                'new_users_7d': new_users_7d,
                'active_users': active_users,
                'users_with_balance': users_with_balance,
                'active_subscriptions': active_subscriptions,
                'expired_subscriptions': expired_subscriptions,
                'inactive_users': inactive_users,
                'languages': languages
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_reports_stats(self) -> Dict[str, Any]:
        """Получение статистики отчетов"""
        try:
            # Общее количество уникальных отчетов (по id)
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                report_ids = set()
                for report in response.json():
                    report_id = report.get('id')
                    if report_id:
                        report_ids.add(report_id)
                total_reports = len(report_ids)
            else:
                total_reports = 0
            
            # Отчеты за последние 30 дней
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/user_reports?created_at=gte.{thirty_days_ago}&select=id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                report_ids = set()
                for report in response.json():
                    report_id = report.get('id')
                    if report_id:
                        report_ids.add(report_id)
                reports_30d = len(report_ids)
            else:
                reports_30d = 0
            
            # Отчеты за последние 7 дней
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/user_reports?created_at=gte.{seven_days_ago}&select=id"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                report_ids = set()
                for report in response.json():
                    report_id = report.get('id')
                    if report_id:
                        report_ids.add(report_id)
                reports_7d = len(report_ids)
            else:
                reports_7d = 0
            
            # Статистика по типам отчетов
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=report_type"
            response = requests.get(url, headers=self.headers)
            report_types = {}
            if response.status_code == 200:
                for report in response.json():
                    report_type = report.get('report_type', 'unknown')
                    report_types[report_type] = report_types.get(report_type, 0) + 1
            
            # Статистика по валютам
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=currency"
            response = requests.get(url, headers=self.headers)
            currencies = {}
            if response.status_code == 200:
                for report in response.json():
                    currency = report.get('currency', 'EUR')
                    currencies[currency] = currencies.get(currency, 0) + 1
            
            # Средняя цена отчета
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=price&price=not.is.null"
            response = requests.get(url, headers=self.headers)
            prices = []
            if response.status_code == 200:
                prices = [r.get('price', 0) for r in response.json() if r.get('price')]
            
            avg_price = sum(prices) / len(prices) if prices else 0
            
            return {
                'total_reports': total_reports,
                'reports_30d': reports_30d,
                'reports_7d': reports_7d,
                'report_types': report_types,
                'currencies': currencies,
                'avg_price': avg_price
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_payments_stats(self) -> Dict[str, Any]:
        """Получение статистики платежей"""
        try:
            # Общее количество платежей
            url = f"{SUPABASE_URL}/rest/v1/payments?select=count"
            response = requests.get(url, headers=self.headers)
            total_payments = len(response.json()) if response.status_code == 200 else 0
            
            # Платежи за последние 30 дней
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/payments?created_at=gte.{thirty_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            payments_30d = len(response.json()) if response.status_code == 200 else 0
            
            # Общая сумма платежей
            url = f"{SUPABASE_URL}/rest/v1/payments?select=amount_euro&amount_euro=not.is.null"
            response = requests.get(url, headers=self.headers)
            amounts = []
            if response.status_code == 200:
                amounts = [p.get('amount_euro', 0) for p in response.json() if p.get('amount_euro')]
            
            total_revenue = sum(amounts)
            
            # Статистика по статусам
            url = f"{SUPABASE_URL}/rest/v1/payments?select=status"
            response = requests.get(url, headers=self.headers)
            statuses = {}
            if response.status_code == 200:
                for payment in response.json():
                    status = payment.get('status', 'unknown')
                    statuses[status] = statuses.get(status, 0) + 1
            
            # Статистика по методам платежа
            url = f"{SUPABASE_URL}/rest/v1/payments?select=payment_method"
            response = requests.get(url, headers=self.headers)
            payment_methods = {}
            if response.status_code == 200:
                for payment in response.json():
                    method = payment.get('payment_method', 'unknown')
                    payment_methods[method] = payment_methods.get(method, 0) + 1
            
            return {
                'total_payments': total_payments,
                'payments_30d': payments_30d,
                'total_revenue': total_revenue,
                'statuses': statuses,
                'payment_methods': payment_methods
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_currency_stats(self) -> Dict[str, Any]:
        """Получение статистики валют"""
        try:
            # Последние курсы валют
            url = f"{SUPABASE_URL}/rest/v1/currency?order=created_at.desc&limit=1"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                latest_rates = response.json()[0] if response.json() else {}
                result = {
                    'latest_rates': latest_rates,
                    'timestamp': latest_rates.get('created_at', 'N/A')
                }
                return convert_datetime_to_string(result)
            else:
                return {'error': 'Failed to fetch currency data'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_locations_stats(self) -> Dict[str, Any]:
        """Получение статистики локаций"""
        try:
            # Статистика по странам
            url = f"{SUPABASE_URL}/rest/v1/countries?select=count"
            response = requests.get(url, headers=self.headers)
            total_countries = len(response.json()) if response.status_code == 200 else 0
            
            # Статистика по городам
            url = f"{SUPABASE_URL}/rest/v1/cities?select=count"
            response = requests.get(url, headers=self.headers)
            total_cities = len(response.json()) if response.status_code == 200 else 0
            
            # Статистика по округам
            url = f"{SUPABASE_URL}/rest/v1/counties?select=count"
            response = requests.get(url, headers=self.headers)
            total_counties = len(response.json()) if response.status_code == 200 else 0
            
            # Статистика по районам
            url = f"{SUPABASE_URL}/rest/v1/districts?select=count"
            response = requests.get(url, headers=self.headers)
            total_districts = len(response.json()) if response.status_code == 200 else 0
            
            return {
                'total_countries': total_countries,
                'total_cities': total_cities,
                'total_counties': total_counties,
                'total_districts': total_districts
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_daily_stats(self, days: int = 30) -> Dict[str, Any]:
        """Получение ежедневной статистики за последние N дней"""
        try:
            daily_stats = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # Пользователи за день
                url = f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{date_str}&created_at=lt.{date_str}T23:59:59&select=count"
                response = requests.get(url, headers=self.headers)
                users_count = len(response.json()) if response.status_code == 200 else 0
                
                # Отчеты за день
                url = f"{SUPABASE_URL}/rest/v1/user_reports?created_at=gte.{date_str}&created_at=lt.{date_str}T23:59:59&select=count"
                response = requests.get(url, headers=self.headers)
                reports_count = len(response.json()) if response.status_code == 200 else 0
                
                # Платежи за день
                url = f"{SUPABASE_URL}/rest/v1/payments?created_at=gte.{date_str}&created_at=lt.{date_str}T23:59:59&select=amount_euro&amount_euro=not.is.null"
                response = requests.get(url, headers=self.headers)
                payments_amount = 0
                if response.status_code == 200:
                    amounts = [p.get('amount_euro', 0) for p in response.json() if p.get('amount_euro')]
                    payments_amount = sum(amounts)
                
                daily_stats.append({
                    'date': date_str,
                    'users': users_count,
                    'reports': reports_count,
                    'revenue': payments_amount
                })
            
            return {'daily_stats': daily_stats}
        except Exception as e:
            return {'error': str(e)}
    
    def get_regions_stats(self) -> Dict[str, Any]:
        """Получение статистики отчетов по регионам"""
        try:
            # Получаем все отчеты с адресами
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=address&address=not.is.null"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {'error': 'Failed to fetch reports data'}
            
            reports = response.json()
            
            # Подсчитываем количество отчетов по регионам
            region_counts = {}
            country_counts = {}
            state_counts = {}
            city_counts = {}
            district_counts = {}
            
            for report in reports:
                address = report.get('address', '').strip()
                if address:
                    # Разбиваем адрес на части (обычно формат: район, город, область, страна)
                    parts = [part.strip() for part in address.split(',')]
                    
                    # Если есть хотя бы одна часть
                    if parts:
                        # Первая часть - обычно район или город
                        district = parts[0]
                        if district:
                            district_counts[district] = district_counts.get(district, 0) + 1
                        
                        # Вторая часть - обычно город
                        if len(parts) > 1:
                            city = parts[1]
                            if city:
                                city_counts[city] = city_counts.get(city, 0) + 1
                        
                        # Третья часть - обычно область/штат
                        if len(parts) > 2:
                            state = parts[2]
                            if state:
                                state_counts[state] = state_counts.get(state, 0) + 1
                        
                        # Последняя часть - обычно страна
                        if len(parts) > 3:
                            country = parts[-1]
                            if country:
                                country_counts[country] = country_counts.get(country, 0) + 1
                        elif len(parts) == 3:
                            # Если только 3 части, то последняя может быть страной
                            country = parts[2]
                            if country:
                                country_counts[country] = country_counts.get(country, 0) + 1
                    
                    # Также считаем общий регион (первая часть адреса)
                    region = address.split(',')[0].strip()
                    if region:
                        region_counts[region] = region_counts.get(region, 0) + 1
            
            # Сортируем по количеству отчетов
            sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_districts = sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Топ 100 регионов
            top_100_regions = sorted_regions[:100]
            
            # Топ 10 регионов для графика
            top_10_regions = sorted_regions[:10]
            
            # Топ 10 по каждой категории
            top_10_countries = sorted_countries[:10]
            top_10_states = sorted_states[:10]
            top_10_cities = sorted_cities[:10]
            top_10_districts = sorted_districts[:10]
            
            return {
                'top_100_regions': top_100_regions,
                'top_10_regions': top_10_regions,
                'top_10_countries': top_10_countries,
                'top_10_states': top_10_states,
                'top_10_cities': top_10_cities,
                'top_10_districts': top_10_districts,
                'total_regions': len(region_counts),
                'total_countries': len(country_counts),
                'total_states': len(state_counts),
                'total_cities': len(city_counts),
                'total_districts': len(district_counts),
                'total_reports_with_address': len(reports)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получение всех статистик для дашборда"""
        stats = {
            'users': self.get_users_stats(),
            'reports': self.get_reports_stats(),
            'payments': self.get_payments_stats(),
            'currency': self.get_currency_stats(),
            'locations': self.get_locations_stats(),
            'daily': self.get_daily_stats(),
            'regions': self.get_regions_stats()
        }
        return convert_datetime_to_string(stats)

# Создаем экземпляр для использования в API
dashboard_api = DashboardAPI()
