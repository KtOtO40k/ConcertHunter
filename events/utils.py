import requests
from django.conf import settings
import time

def get_tm_artist(artist_name):
    """
    Ищет артиста в Ticketmaster API.
    Возвращает список словарей [{'name', 'tm_id', 'image_url'}, ...].
    """
    url = "https://app.ticketmaster.com/discovery/v2/attractions.json"
    params = {
        'apikey': settings.TM_API_KEY,
        'keyword': artist_name,
        'classificationName': 'music',  # Ищем только музыкантов
        'size': 5  # Ограничим вывод 5 результатами
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Если ничего не нашли
        if '_embedded' not in data:
            return []

        artists_data = []
        for item in data['_embedded']['attractions']:
            # Ищем картинку с хорошим разрешением (обычно ratio 16_9)
            image_url = ""
            if 'images' in item:
                # Берем первую попавшуюся или конкретную
                image_url = item['images'][0]['url']

            artists_data.append({
                'name': item['name'],
                'tm_id': item['id'],
                'image_url': image_url,
                'external_url': item.get('url', '')
            })
        
        return artists_data

    except requests.RequestException as e:
        print(f"Error fetching data from TM: {e}")
        return []
    
def get_tm_artist_details(tm_id):
    """
    Получает детальную информацию об артисте по ID.
    """
    url = f"https://app.ticketmaster.com/discovery/v2/attractions/{tm_id}.json"
    params = {'apikey': settings.TM_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Ищем лучшую картинку
        image_url = ""
        if 'images' in data:
            image_url = data['images'][0]['url']

        return {
            'tm_id': data['id'],
            'name': data['name'],
            'image_url': image_url,
            'external_url': data.get('url', '')
        }
    except Exception as e:
        print(f"Error fetching details: {e}")
        return None

def get_tm_events(artist_tm_id, city):
    """
    Ищет события для конкретного артиста в конкретном городе.
    Возвращает список словарей с деталями событий.
    """
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': settings.TM_API_KEY,
        'attractionId': artist_tm_id,
        'city': city,
        'sort': 'date,asc',  # Сортируем по дате
        'size': 20, # Ограничим количество событий
    }

    try:
        time.sleep(0.5) # Небольшая задержка между запросами
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if '_embedded' not in data or 'events' not in data['_embedded']:
            return []

        events_list = []
        for event_item in data['_embedded']['events']:
            venue_name = ""
            city_name = ""
            latitude = None
            longitude = None

            if '_embedded' in event_item and 'venues' in event_item['_embedded']:
                venue = event_item['_embedded']['venues'][0] # Берем первую площадку
                venue_name = venue.get('name', 'Неизвестная площадка')
                city_name = venue.get('city', {}).get('name', city) # Используем город из API, если есть, иначе из подписки
                
                # Координаты для карты!
                location = venue.get('location', {})
                latitude = float(location['latitude']) if 'latitude' in location else None
                longitude = float(location['longitude']) if 'longitude' in location else None
            
            # Статус билетов
            ticket_status = event_item.get('dates', {}).get('status', {}).get('code', 'unknown')

            events_list.append({
                'tm_event_id': event_item['id'],
                'name': event_item['name'],
                'date': event_item['dates']['start']['dateTime'], # Важно: это строка, потом преобразуем в DateTime
                'venue_name': venue_name,
                'city': city_name,
                'latitude': latitude,
                'longitude': longitude,
                'ticket_url': event_item.get('url', '#'),
                'ticket_status': ticket_status
            })
        return events_list

    except requests.RequestException as e:
        print(f"Error fetching events from TM: {e}")
        return []