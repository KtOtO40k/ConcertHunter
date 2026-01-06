from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    """Исполнитель. Храним, чтобы не опрашивать API постоянно."""
    name = models.CharField(max_length=200, verbose_name="Исполнитель")
    tm_id = models.CharField(max_length=50, unique=True, verbose_name="ID Ticketmaster")
    image_url = models.URLField(blank=True, null=True, verbose_name="Фото")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Артист"
        verbose_name_plural = "Артисты"


class Subscription(models.Model):
    """Подписка пользователя на артиста в конкретном городе."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='subscriptions')
    city = models.CharField(max_length=100, verbose_name="Город поиска")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"{self.user.username} -> {self.artist.name} ({self.city})"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Event(models.Model):
    """Найденный концерт."""
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255, verbose_name="Название события")
    date = models.DateTimeField(verbose_name="Дата и время")
    venue_name = models.CharField(max_length=255, verbose_name="Площадка")
    city = models.CharField(max_length=100, verbose_name="Город")
    
    # Поля для карты (Leaflet)
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    
    ticket_url = models.URLField(verbose_name="Ссылка на билеты")
    tm_event_id = models.CharField(max_length=50, unique=True, verbose_name="ID События TM")

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} | {self.artist.name} in {self.city}"

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ['date']