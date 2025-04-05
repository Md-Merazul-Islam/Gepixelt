# emails/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import send_email_task

class SendEmailAfterOneMinute(APIView):
    def post(self, request, *args, **kwargs):
        # Get email parameters from request
        subject = request.data.get('subject')
        message = request.data.get('message')
        from_email = 'bluskybooking.io@gmail.com'  # Replace with your email
        recipient_list = ['mdmerazul75@gmail.com']  # Replace with recipient's email

        # Schedule the task to run after 1 minute (60 seconds)
        send_email_task.apply_async(
            args=[subject, message, from_email, recipient_list],
            countdown=60  # Delay of 1 minute (60 seconds)
        )

        return Response({"message": "Email will be sent in 1 minute"}, status=status.HTTP_200_OK)
