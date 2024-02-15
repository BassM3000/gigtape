from django.core.management.base import BaseCommand
from events.models import Event
from datetime import datetime

class Command(BaseCommand):
    help = 'Expires event objects which are out-of-date'
    
    def handle(self, *args, **kwargs):
        expired_events = Event.objects.filter(event_date__lt=datetime.now())
        expired_events.delete()
        self.stdout.write(self.style.SUCCESS('Expired events deleted successfully'))