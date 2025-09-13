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
            # Общее количество пользователей
            url = f"{SUPABASE_URL}/rest/v1/users?select=count"
            response = requests.get(url, headers=self.headers)
            total_users = len(response.json()) if response.status_code == 200 else 0
            
            # Пользователи за последние 30 дней
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{thirty_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            new_users_30d = len(response.json()) if response.status_code == 200 else 0
            
            # Пользователи за последние 7 дней
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{seven_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            new_users_7d = len(response.json()) if response.status_code == 200 else 0
            
            # Активные пользователи (с активностью за последние 7 дней)
            url = f"{SUPABASE_URL}/rest/v1/users?last_activity=gte.{seven_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            active_users = len(response.json()) if response.status_code == 200 else 0
            
            # Пользователи с балансом
            url = f"{SUPABASE_URL}/rest/v1/users?balance=gt.0&select=count"
            response = requests.get(url, headers=self.headers)
            users_with_balance = len(response.json()) if response.status_code == 200 else 0
            
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
                'languages': languages
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_reports_stats(self) -> Dict[str, Any]:
        """Получение статистики отчетов"""
        try:
            # Общее количество отчетов
            url = f"{SUPABASE_URL}/rest/v1/user_reports?select=count"
            response = requests.get(url, headers=self.headers)
            total_reports = len(response.json()) if response.status_code == 200 else 0
            
            # Отчеты за последние 30 дней
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/user_reports?created_at=gte.{thirty_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            reports_30d = len(response.json()) if response.status_code == 200 else 0
            
            # Отчеты за последние 7 дней
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            url = f"{SUPABASE_URL}/rest/v1/user_reports?created_at=gte.{seven_days_ago}&select=count"
            response = requests.get(url, headers=self.headers)
            reports_7d = len(response.json()) if response.status_code == 200 else 0
            
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
                return {
                    'latest_rates': latest_rates,
                    'timestamp': latest_rates.get('created_at', 'N/A')
                }
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
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получение всех статистик для дашборда"""
        return {
            'users': self.get_users_stats(),
            'reports': self.get_reports_stats(),
            'payments': self.get_payments_stats(),
            'currency': self.get_currency_stats(),
            'locations': self.get_locations_stats(),
            'daily': self.get_daily_stats()
        }

# Создаем экземпляр для использования в API
dashboard_api = DashboardAPI()
