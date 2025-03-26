from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet,  CompletePaymentView, TransactionListView, UserSubscriptionDetailView,UserSubscriptionList
# CreateOrderFromCardView
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'my-subscriptions', UserSubscriptionViewSet, basename='my-subscriptions')
router.register(r'all-subscriptions', UserSubscriptionList , basename='all-subscriptions')




urlpatterns = [
    path('', include(router.urls)),
    path('complete-payment/<int:plan_id>/',CompletePaymentView.as_view(), name='complete_payment'),
    path('transactions/', TransactionListView.as_view(),
         name='transaction-list'),  # List all transactions
    path('user-subscription/', UserSubscriptionDetailView.as_view(),name='user-subscription-detail'),
 
]
