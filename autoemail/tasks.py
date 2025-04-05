from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail




from django.conf import settings


@shared_task
def send_email_task():
    subject = "Automated Email"
    message = "This is an automated email sent every 1 minute."
    from_email = settings.EMAIL_HOST_USER  
    recipient_list = ['mdmerazul75@gmail.com']

    send_mail(subject, message, from_email, recipient_list)
    print("Email sent successfully!")


def create_periodic_task():
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1, period=IntervalSchedule.MINUTES)

    
    task_name = 'Send Email Every Minute'
    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'interval': schedule,
            'task': 'autoemail.tasks.send_email_task',  
        }
    )

    
    if not created:
        task.interval = schedule
        task.task = 'autoemail.tasks.send_email_task'
        task.save()
