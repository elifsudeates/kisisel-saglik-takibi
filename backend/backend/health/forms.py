from django import forms
from .models import DailyEntry

class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['water_liters', 'sleep_hours']
        labels = {
            'water_liters': 'Su Tüketimi (L)',
            'sleep_hours': 'Uyku Süresi (saat)'
        }
        widgets = {
            'water_liters': forms.NumberInput(attrs={'placeholder': 'Su Tüketimi (L)'}),
            'sleep_hours': forms.NumberInput(attrs={'placeholder': 'Uyku Süresi (saat)'})
        }
