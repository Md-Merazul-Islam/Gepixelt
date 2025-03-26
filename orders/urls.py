from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderAPIView, CancelOrderAPIView,  OrderStatusUpdateView,SendEmailView

router = DefaultRouter()
router.register(r'all', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # For GET and POST (list and create orders)
    path('my-order/', OrderAPIView.as_view(), name='order-list'),
    # For GET, PUT, PATCH, DELETE (single order)
    path('my-order/<int:order_id>/', OrderAPIView.as_view(), name='order-detail'),
    path('cancel-order/<int:order_id>/', CancelOrderAPIView.as_view(),
         name='cancel-order'),  # For cancel order
    path('<int:order_id>/update-status/',
         OrderStatusUpdateView.as_view(), name='order-status-update'),
    
     path('send-email/', SendEmailView.as_view(), name='send_email'),
]
