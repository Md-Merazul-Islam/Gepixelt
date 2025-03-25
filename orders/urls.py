from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderAPIView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('my-order/', OrderAPIView.as_view(), name='order-list'),  # For GET and POST (list and create orders)
    path('my-order/<int:order_id>/', OrderAPIView.as_view(), name='order-detail'),  # For GET, PUT, PATCH, DELETE (single order)
]
