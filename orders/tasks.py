from celery import shared_task
from datetime import datetime
import smtplib  # You can use any method to send the message, like email or SMS


@shared_task
def send_daily_message():
    # Your logic to send the message, e.g., email
    subject = "Daily Message"
    body = "This is your daily reminder!"

    # Example of sending an email (customize this part based on your requirement)
    to_email = "mdmerazul75@gmail.com"
    from_email = "bluskybooking.io@gmail.com"

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        # Use environment variables for password
        server.login('bluskybooking.io@gmail.com', 'rsypyovoqpsbswox')
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(from_email, to_email, message)

    return "Message Sent Successfully"
