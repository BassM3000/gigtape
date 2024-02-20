from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Venue, Event
from .serializers import VenueSerializer, EventSerializer
from datetime import datetime

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
        # Get the offset from query parameters (default to 0 if not provided)
        offset = int(request.query_params.get('offset', 0))
        
        # Retrieve events starting from the specified offset
        events = Event.objects.filter(event_date__gte=datetime.now()).order_by('event_date')[offset:offset + 12]
        
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
