from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet, OrderViewSet,  CompletePaymentView,TransactionListView
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'user-subscriptions', UserSubscriptionViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('', include(router.urls)),
     path('complete-payment/<int:plan_id>/', CompletePaymentView.as_view(), name='complete_payment'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),  # List all transactions
]
