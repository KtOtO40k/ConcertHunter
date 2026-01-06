from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Subscription, Artist, Event
from events.utils import get_tm_events
import time # Для задержек

class Command(BaseCommand):
    help = 'Обновляет список концертов для всех активных подписок'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем обновление концертов...'))
        
        subscriptions = Subscription.objects.filter(is_active=True).select_related('user', 'artist')
        total_new_events = 0

        for sub in subscriptions:
            self.stdout.write(f'  Проверяем подписку: {sub.artist.name} в {sub.city} для {sub.user.username}')
            
            events_data = get_tm_events(sub.artist.tm_id, sub.city)
            
            for event_item in events_data:
                # Пропускаем прошедшие события
                event_date = timezone.datetime.fromisoformat(event_item['date'].replace('Z', '+00:00'))
                if event_date < timezone.now():
                    continue

                # Создаем или обновляем событие
                event, created = Event.objects.get_or_create(
                    tm_event_id=event_item['tm_event_id'],
                    defaults={
                        'artist': sub.artist,
                        'name': event_item['name'],
                        'date': event_date,
                        'venue_name': event_item['venue_name'],
                        'city': event_item['city'],
                        'latitude': event_item['latitude'],
                        'longitude': event_item['longitude'],
                        'ticket_url': event_item['ticket_url'],
                    }
                )
                if created:
                    total_new_events += 1
                    self.stdout.write(self.style.SUCCESS(f'    > Найден новый концерт: {event.name} в {event.city} ({event.date})'))
                # else:
                #     self.stdout.write(self.style.NOTICE(f'    > Концерт уже существует: {event.name}'))

        self.stdout.write(self.style.SUCCESS(f'Обновление завершено. Всего новых событий: {total_new_events}'))