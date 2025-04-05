# emails/urls.py
from django.urls import path
from .views import SendEmailAfterOneMinute

urlpatterns = [
    path('send-email/', SendEmailAfterOneMinute.as_view(), name='send_email_after_one_minute'),
]
