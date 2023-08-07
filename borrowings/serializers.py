from rest_framework import serializers

from book.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.telegram_notifications import send_telegram_notification


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )

    def validate_book(self, value):
        if value.inventory <= 0:
            raise serializers.ValidationError(
                "Book is not available for borrowing."
            )
        return value

    def create(self, validated_data):
        book = validated_data["book"]

        borrowing = Borrowing.objects.create(**validated_data)

        book.inventory -= 1
        book.save()

        message = (
            f"New borrowing created:\nBook: {borrowing.book.title}\n"
            f"Expected Return Date: {borrowing.expected_return_date}\n"
            f"Book in inventory: {borrowing.book.inventory}"
        )
        send_telegram_notification(message)

        return borrowing


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
