from django.urls import path
from .views import VenueListView, VenueDetailView, EventListView, EventDetailView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/venues/', VenueListView.as_view(), name='venue-list'),
    path('api/venues/<int:venue_id>/', VenueDetailView.as_view(), name='venue-detail'),
    path('api/events/', EventListView.as_view(), name='event-list'),
    path('api/events/<int:event_id>/', EventDetailView.as_view(), name='event-detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'error': 'The resource was not found',        
    })