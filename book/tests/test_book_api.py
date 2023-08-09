from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book:book-list")


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_anon_user_allow_get(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="test_title",
            author="test_author",
            cover="HARD",
            inventory=1,
            daily_fee=6.66,
        )

    def test_regular_user_get_method_only(self):
        res = self.client.post(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books(self):
        res = self.client.get(BOOK_URL)
        books = Book.objects.all()

        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book(self):
        url = reverse("book:book-detail", args=[self.book.id])
        res = self.client.get(url)

        serializer = BookSerializer(self.book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.super_user)

    def test_create_book(self):
        payload = {
            "title": "title",
            "author": "author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": Decimal("6.99"),
        }
        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))
