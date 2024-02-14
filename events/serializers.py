from rest_framework import serializers
from .models import Venue, Event

class VenueSerializer(serializers.ModelSerializer):
  class Meta:
    model = Venue
    fields = ['id', 'name', 'website', 'venue_img']

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = ['id', 'venue', 'event_name', 'event_date', 'website', 'event_img']