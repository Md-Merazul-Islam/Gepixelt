from django.urls import path
from .views import WeeklyOrderCreateView, WeeklyOrderConfirmPaymentView

urlpatterns = [
    path('order/', WeeklyOrderCreateView.as_view(), name='weekly-order-create'),
    path('order/confirm-payment/', WeeklyOrderConfirmPaymentView.as_view(), name='weekly-order-confirm-payment'),
]
