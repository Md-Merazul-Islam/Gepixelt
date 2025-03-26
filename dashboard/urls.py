
from django.urls import path
from .views import DashboardStatsView,export_orders_excel,export_orders_excel_by_german,export_orders_json

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('export-orders-excel/', export_orders_excel, name='export_orders_excel'),
    path('export-orders-excel-by-german/', export_orders_excel_by_german, name='export_orders_excel_by_german'),
    path('export-orders-json/', export_orders_json, name='export_orders_json'),
]
