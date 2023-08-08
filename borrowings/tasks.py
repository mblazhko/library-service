from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from .models import Borrowing
from .telegram_notifications import send_telegram_notification


@shared_task
def send_daily_notification():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Borrowing due tomorrow:\nBook: {borrowing.book.title}\n"
                f"Expected Return Date: {borrowing.expected_return_date}"
                "It's last day to return the book!"
            )
            send_telegram_notification(message)
    else:
        message = "No borrowings due tomorrow!"
        send_telegram_notification(message)
