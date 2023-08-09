from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="regular@example.com", password="testpassword"
        )
        self.superuser = get_user_model().objects.create_superuser(
            email="superuser@example.com", password="testpassword"
        )

    def test_create_regular_user(self):
        url = reverse("user:create")
        data = {
            "email": "newuser@example.com",
            "password": "testpassword",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            get_user_model().objects.get(email="newuser@example.com"),
            get_user_model().objects.all(),
        )

    def test_create_superuser(self):
        url = reverse("user:create")
        data = {
            "email": "superuser2@example.com",
            "password": "testpassword",
            "is_staff": True,
            "is_superuser": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            get_user_model().objects.get(email="superuser2@example.com"),
            get_user_model().objects.all(),
        )

    def test_retrieve_user_details_authenticated(self):
        url = reverse("user:manage")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_retrieve_user_details_unauthenticated(self):
        url = reverse("user:manage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_valid_credentials(self):
        url = reverse("user:token_obtain_pair")
        data = {
            "email": "regular@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
