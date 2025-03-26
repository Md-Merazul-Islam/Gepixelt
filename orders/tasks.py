# myapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(recipient_email):
    logger.info(f"Received email: {recipient_email}")  # Log the recipient email

    try:
        send_mail(
            'Automated Message',
            'This is an automated message sent after 1 minute.',
            settings.EMAIL_HOST_USER,  # Sender email
            [recipient_email],  # Receiver email
        )
        logger.info(f"Email sent successfully to: {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")

# myapp/tasks.py
@shared_task
def test_task():
    print("Test task executed successfully.")
