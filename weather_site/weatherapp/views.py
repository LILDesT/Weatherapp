
from django.shortcuts import render
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_weather(request):
    city = request.GET.get('city', '').strip()
    if not city:
        return render(request, 'weatherapp/weatherapp.html', {'weather': None})

    api_key = '4ef1894feee89d860fe3192fa4a13997'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    url = 'https://api.openweathermap.org/data/2.5/weather'

    # Настройка повторных попыток
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    headers = {"Accept": "application/json"}

    try:
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Бросает исключение для статус-кодов 4xx/5xx
        data = response.json()  # Преобразуем ответ в JSON-формат
    except requests.RequestException as e:
        return render(request, 'weatherapp/weatherapp.html', {'error': f'Error fetching weather data: {str(e)}'})

    # Извлечение необходимых данных
    temperature = data.get('main', {}).get('temp', 'No data')  # Температура
    humidity = data.get('main', {}).get('humidity', 'No data')  # Влажность
    weather_description = data.get('weather', [{}])[0].get('description', 'No description')  # Описание погоды

    return render(request, 'weatherapp/weatherapp.html', {
        'weather': weather_description,
        'temperature': temperature,
        'humidity': humidity,
        'city': city
    })