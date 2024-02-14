from django.urls import path
from .views import VenueListView, VenueDetailView
from django.http import JsonResponse

urlpatterns = [
    path('api/venues/', VenueListView.as_view(), name='venue-list'),
    path('api/venues/<int:venue_id>/', VenueDetailView.as_view(), name='venue-detail'),
]

def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'error': 'The resource was not found',        
    })