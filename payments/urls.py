from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet,  CompletePaymentView,TransactionListView,UserSubscriptionDetailView
# CreateOrderFromCardView
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'user-subscriptions', UserSubscriptionViewSet)
from . import views



urlpatterns = [
    path('', include(router.urls)),
     path('complete-payment/<int:plan_id>/', CompletePaymentView.as_view(), name='complete_payment'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),  # List all transactions
    path('user-subscription/', UserSubscriptionDetailView.as_view(), name='user-subscription-detail'),
    
    # path('orders/', views.OrderListView.as_view(), name='order_list'),
    # path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    # path('orders/<int:order_id>/place/', views.OrderPlaceOrderView.as_view(), name='order_place_order'),
    # path('orders/create/', views.CreateOrderFromCardView.as_view(), name='create_order_from_card'),
]
