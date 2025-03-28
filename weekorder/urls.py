from django.urls import path
from .views import WeeklyOrderCreateView, WeeklyOrderConfirmPaymentView,WeeklyOrderListView,WeeklyOrderExportToExcelView

urlpatterns = [
    path('order/', WeeklyOrderCreateView.as_view(), name='weekly-order-create'),
    path('order/list/', WeeklyOrderListView.as_view(), name='weekly-order-create'),
    path('order/list/excel/', WeeklyOrderExportToExcelView.as_view(), name='weekly-order-create'),
    
    path('order/confirm-payment/', WeeklyOrderConfirmPaymentView.as_view(), name='weekly-order-confirm-payment'),
]
