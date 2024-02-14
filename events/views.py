import schedule
import time
from .scrapers import *
from rest_framework import generics
from .models import Venue, Event
from .serializers import VenueSerializer, EventSerializer

#def scrape_all_events():
#    scrape_yotalo('https://yo-talo.fi/tapahtumat')
#    scrape_vastavirta('https://vastavirta.net/')
#    scrape_tullikamari('https://tullikamari.fi/tapahtumat/')
#   scrape_telakka('https://www.telakka.eu/ohjelma/')
#    scrape_tavaraasema('https://tavara-asema.fi/ohjelma/')
#    scrape_tamperetalo('https://www.tampere-talo.fi/tapahtumat/?em_l=list')
#    scrape_paappa('https://paappa.fi/ohjelma/')
#    scrape_olympia('https://olympiakortteli.fi/keikat/')
#    scrape_nokiaarena('https://nokiaarena.fi/tapahtumat/')
#    scrape_glivelab('https://glivelab.fi/tampere/?show_all=1')

#def job():
#    scrape_all_events()

#schedule.every().day.at("00:01").do(job)

#while True:
#    schedule.run_pending()
#    time.sleep(1)
#job()

class VenueList(generics.ListAPIView):
  queryset = Venue.objects.all()
  serializer_class = VenueSerializer

class VenueDetail(generics.RetrieveAPIView):
  queryset = Venue.objects.all()
  serializer_class = VenueSerializer

class EventList(generics.ListAPIView):
  queryset = Event.objects.all()
  serializer_class = EventSerializer

class EventDetail(generics.RetrieveAPIView):
  queryset = Event.objects.all()
  serializer_class = EventSerializer