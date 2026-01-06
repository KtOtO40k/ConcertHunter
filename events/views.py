import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .forms import ArtistSearchForm, SubscriptionForm
from .utils import get_tm_artist, get_tm_artist_details
from .models import Artist, Subscription, Event
from deep_translator import GoogleTranslator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def artist_search(request):
    search_form = ArtistSearchForm()
    results = []

    if 'artist_name' in request.GET:
        search_form = ArtistSearchForm(request.GET)
        if search_form.is_valid():
            name = search_form.cleaned_data['artist_name']
            results = get_tm_artist(name)

    context = {
        'form': search_form,
        'results': results
    }
    return render(request, 'events/search.html', context)

@login_required
def subscribe(request, tm_id):
    artist_data = get_tm_artist_details(tm_id)
    
    if not artist_data:
        messages.error(request, "Не удалось получить данные об артисте.")
        return redirect('search')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            raw_city = form.cleaned_data['city']

            try:
                # 1. Переводим
                city_english = GoogleTranslator(source='auto', target='en').translate(raw_city)
                # 2. УДАЛЯЕМ ЛИШНИЕ ПРОБЕЛЫ И ДЕЛАЕМ ПЕРВУЮ БУКВУ ЗАГЛАВНОЙ
                city_english = city_english.strip().title()
            except Exception as e:
                print(f"Ошибка перевода: {e}")
                city_english = raw_city.strip().title()

            artist, created = Artist.objects.get_or_create(
                tm_id=artist_data['tm_id'],
                defaults={
                    'name': artist_data['name'],
                    'image_url': artist_data['image_url']
                }
            )

            # Создаем подписку с "чистым" названием города
            sub, sub_created = Subscription.objects.get_or_create(
                user=request.user,
                artist=artist,
                city=city_english
            )

            if sub_created:
                messages.success(request, f"Вы подписались на {artist.name} в городе {city_english}!")
            else:
                messages.info(request, f"Вы уже подписаны на этого артиста в городе {city_english}.")
            
            return redirect('search')
    else:
        form = SubscriptionForm()

    context = {
        'form': form,
        'artist': artist_data
    }
    return render(request, 'events/subscribe.html', context)

@login_required
def dashboard(request):
    user_subscriptions = Subscription.objects.filter(user=request.user, is_active=True)
    
    q_objects = Q()
    for sub in user_subscriptions:
        # ИСПОЛЬЗУЕМ __iexact ДЛЯ ПОИСКА БЕЗ УЧЕТА РЕГИСТРА
        # Это значит, что London найдется, даже если в базе london
        q_objects |= Q(artist=sub.artist, city__iexact=sub.city)

    if user_subscriptions.exists():
        events = Event.objects.filter(q_objects, date__gte=timezone.now()).order_by('date')
    else:
        events = Event.objects.none()
    
    map_data = []
    for event in events:
        if event.latitude and event.longitude:
            map_data.append({
                'lat': event.latitude,
                'lon': event.longitude,
                'title': f"{event.artist.name} - {event.name}",
                'date': event.date.strftime('%d.%m.%Y %H:%M'),
                'city': event.city,
                'venue': event.venue_name,
                'ticket_url': event.ticket_url,
            })

    context = {
        'events': events,
        'map_data_json': json.dumps(map_data),
        'subscriptions': user_subscriptions  # <--- ДОБАВЬ ЭТУ СТРОКУ
    }
    return render(request, 'events/dashboard.html', context)
@login_required
def delete_subscription(request, sub_id):
    # Удаляем подписку только если она принадлежит текущему пользователю
    subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)
    
    artist_name = subscription.artist.name
    subscription.delete()
    
    messages.success(request, f"Подписка на {artist_name} удалена.")
    return redirect('dashboard')
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Сразу логиним пользователя после регистрации
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})