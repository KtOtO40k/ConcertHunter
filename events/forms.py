from django import forms
from .models import Subscription

class ArtistSearchForm(forms.Form):
    artist_name = forms.CharField(
        label="Исполнитель",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например, Rammstein'})
    )

class SubscriptionForm(forms.ModelForm):
    """Форма для подписки (выбор города)"""
    class Meta:
        model = Subscription
        fields = ['city']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город (например, London)'})
        }