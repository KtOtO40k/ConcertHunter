from django.contrib import admin
from .models import Artist, Subscription, Event

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'tm_id')
    search_fields = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'city', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('user__username', 'artist__name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('artist', 'city', 'date', 'venue_name')
    list_filter = ('city', 'date')
    search_fields = ('artist__name', 'city', 'name')