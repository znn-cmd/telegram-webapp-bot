import requests

try:
    r = requests.get('http://localhost:8080/api/dashboard/regions')
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('Data keys:', list(data.keys()))
        print('Top 10 regions:', data.get('top_10_regions', [])[:5])
        print('Total regions:', data.get('total_regions', 'N/A'))
        print('Total reports with address:', data.get('total_reports_with_address', 'N/A'))
    else:
        print('Error:', r.text)
except Exception as e:
    print('Exception:', e)
