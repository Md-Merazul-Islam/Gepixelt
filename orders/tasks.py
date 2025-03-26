from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_email_task(recipient_email):
    print(f"Sending email to: {recipient_email}")
    try:
        send_mail(
            'Automated Message',
            'This is an automated message sent after 1 minute.',
            settings.DEFAULT_FROM_EMAIL,  # Sender email
            [recipient_email],  # Receiver email
        )
    except Exception as e:
        # Log error
        print(f"Error sending email: {e}")
