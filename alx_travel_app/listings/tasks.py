from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_confirmation_email(user_email):
    send_mail(
        'Booking Confirmation',
        'Your booking has been confirmed!',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
    