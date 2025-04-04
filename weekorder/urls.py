from django.urls import path
from .views import WeeklyOrderCreateView, WeeklyOrderConfirmPaymentView,WeeklyOrderListView,WeeklyOrderExportToExcelView,OrderStatsView,WeeklyOrderCreateByPayPal,WeeklyOrderConfirmByPayPalPaymentView
from django.http import JsonResponse
def Payment_success(request):
    return JsonResponse({"message": "Payment Success.", "status": 200})

def Payment_Cancel(request):
    return JsonResponse({"message": "Payment cancel!", "status": 200})


urlpatterns = [
    #stripe_payment
    path('order/', WeeklyOrderCreateView.as_view(), name='weekly-order-create'),
    path('order/confirm-payment/', WeeklyOrderConfirmPaymentView.as_view(), name='weekly-order-confirm-payment'),
    #paypal_payment
    path('order/paypal/', WeeklyOrderCreateByPayPal.as_view(), name='weekly-order-paypal'),
    path('order/paypal/confirm/', WeeklyOrderConfirmByPayPalPaymentView.as_view(), name='weekly-order-paypal-confirm'),
    
    path('order/success/', Payment_success, name='payment-success'),
    path('order/cancel/', Payment_Cancel, name='payment-cancel'),
    
    path('order/list/', WeeklyOrderListView.as_view(), name='weekly-order-create'),
    path('order/list/excel/', WeeklyOrderExportToExcelView.as_view(), name='weekly-order-create'),
    path('order/dashboard/', OrderStatsView.as_view(), name='weekly-order-create'),
    

]
