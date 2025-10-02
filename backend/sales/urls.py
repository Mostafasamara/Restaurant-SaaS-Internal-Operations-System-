from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, CustomerViewSet, DealViewSet, DealActivityViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'activities', DealActivityViewSet, basename='deal-activity')

urlpatterns = [
    path('', include(router.urls)),
]
