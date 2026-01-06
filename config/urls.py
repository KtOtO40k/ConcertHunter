from django.contrib import admin
from django.urls import path, include  # <-- Добавь include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('events.urls')),  # <-- Подключаем наши урлы
]
