from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DailyEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    water_liters = models.FloatField(default=0.0)
    sleep_hours = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'date')
        
        