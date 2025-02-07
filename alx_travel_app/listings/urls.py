from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, initiate_payment, verify_payment, payment_success

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/verify/', verify_payment, name='verify_payment'),
]
