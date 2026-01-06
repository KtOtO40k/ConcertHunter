from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.artist_search, name='search'),
    path('subscribe/<str:tm_id>/', views.subscribe, name='subscribe'),
    path('delete/<int:sub_id>/', views.delete_subscription, name='delete_subscription'),
    
    # Новый путь
    path('signup/', views.signup, name='signup'),
]