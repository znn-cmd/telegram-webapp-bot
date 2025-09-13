import requests

try:
    r = requests.get('http://localhost:8080/api/dashboard/stats')
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('Data keys:', list(data.keys()))
        print('Users total:', data.get('users', {}).get('total_users', 'N/A'))
        print('Reports total:', data.get('reports', {}).get('total_reports', 'N/A'))
    else:
        print('Error:', r.text)
except Exception as e:
    print('Exception:', e)
