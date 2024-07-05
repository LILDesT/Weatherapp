from django.shortcuts import render
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from googletrans import Translator

def get_weather(request):
    city = request.GET.get('city', '').strip()
    if not city:
        return render(request, 'weatherapp/weatherapp.html', {'weather': None})

    api_key = '#'
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
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return render(request, 'weatherapp/weatherapp.html', {'error': f'Error fetching weather data: {str(e)}'})

    temperature = data.get('main', {}).get('temp', 'No data')
    humidity = data.get('main', {}).get('humidity', 'No data')
    weather_description = data.get('weather', [{}])[0].get('description', 'No description')
    lat = data.get('coord', {}).get('lat', None)
    lon = data.get('coord', {}).get('lon', None)

    try:
        translator = Translator()
        translated_description = translator.translate(weather_description, dest='ru').text
    except Exception as e:
        translated_description = weather_description  # Если перевод не работает, оставляем оригинальное описание

    context = {
        'weather': translated_description,
        'temperature': temperature,
        'humidity': humidity,
        'city': city,
        'lat': lat,
        'lon': lon,
        'error': None
    }
    return render(request, 'weatherapp/weatherapp.html', context)