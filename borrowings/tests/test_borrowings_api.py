import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from book.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
)

BORROWING_URL = reverse("borrowings:borrowing-list")
NEXT_DAY = timezone.now() + datetime.timedelta(days=1)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.super_user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="test_title",
            author="test_author",
            cover="HARD",
            inventory=2,
            daily_fee=6.66,
        )

    def test_list_borrowing_current_user_only(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY, book=self.book, user=self.user
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY,
            book=self.book,
            user=self.super_user,
        )

        res = self.client.get(BORROWING_URL)

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_borrowing_retrieve(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=NEXT_DAY, book=self.book, user=self.user
        )
        url = reverse("borrowings:borrowing-detail", args=[borrowing.id])
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        self.client.force_authenticate(self.user)
        payload = {
            "expected_return_date": NEXT_DAY,
            "book": self.book.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["book"])
        self.assertEqual(book.inventory, 1)

        for key in payload:
            if key in ["book", "user"]:
                self.assertEqual(payload[key], getattr(borrowing, key).id)
            else:
                self.assertEqual(payload[key], getattr(borrowing, key))

    def test_return_borrowing(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=NEXT_DAY, book=self.book, user=self.user
        )
        url = (
            reverse("borrowings:borrowing-detail", args=[borrowing.id])
            + "return/"
        )

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()

        self.assertFalse(borrowing.is_active)
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 2)


class AdminBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="testpassword",
        )
        self.user = get_user_model().objects.create_user(
            email="regular@regular.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.admin)
        self.book = Book.objects.create(
            title="admin_title",
            author="admin_author",
            cover="HARD",
            inventory=2,
            daily_fee=6.66,
        )

    def test_filtering_by_user_id(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY, book=self.book, user=self.user
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY,
            book=self.book,
            user=self.admin,
        )

        res = self.client.get(BORROWING_URL, {"user_id": self.user.id})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtering_by_is_active(self):
        borrowing1 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY, book=self.book, user=self.user
        )
        borrowing2 = Borrowing.objects.create(
            expected_return_date=NEXT_DAY,
            book=self.book,
            user=self.admin,
        )
        borrowing1.is_active = False
        borrowing1.save()

        res = self.client.get(BORROWING_URL, {"is_active": False})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
