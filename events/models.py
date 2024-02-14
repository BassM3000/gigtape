from django.utils import timezone
from django.db import models

class Venue(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, default='N/A')
    website = models.TextField(default='N/A')
    venue_img = models.TextField(default='N/A')
    
    class Meta:
        app_label = 'events'

class Event(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200, default='N/A')
    event_date = models.DateField('event date')
    website = models.TextField(default='N/A')
    event_img = models.TextField(default='N/A')
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['venue', 'event_name', 'event_date'], name='event_venue_name_date_idx')]
        indexes = [models.Index(fields=['event_date'], name='event_date_idx')]

        