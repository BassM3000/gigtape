import schedule
import time
from .scrapers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

#class VenueList(generics.ListAPIView):
#  queryset = Venue.objects.all()
#  serializer_class = VenueSerializer

#class VenueDetail(generics.RetrieveAPIView):
#  queryset = Venue.objects.all()
#  serializer_class = VenueSerializer

#class EventList(generics.ListAPIView):
#  queryset = Event.objects.all()
#  serializer_class = EventSerializer

#class EventDetail(generics.RetrieveAPIView):
#  queryset = Event.objects.all()
#  serializer_class = EventSerializer

class VenueListView(APIView):
    def get(self, request):
        venues = Venue.objects.all()
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VenueDetailView(APIView):
    def get(self, request, venue_id):
        try:
            venue = Venue.objects.get(pk=venue_id)
            serializer = VenueSerializer(venue)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Venue.DoesNotExist:
            return Response({"error": "Venue not found"}, status=status.HTTP_404_NOT_FOUND)

class EventListView(APIView):
    def get(self, request):
      events = Event.objects.order_by('event_date')
      serializer = EventSerializer(events, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

class EventDetailView(APIView):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)