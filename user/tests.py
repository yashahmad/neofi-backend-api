from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')

    def test_user_registration_success(self):
        data = {
            'username': 'newuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # self.assertIn('success', response.data)  # Adjust based on your actual success response structure

    
    def test_user_registration_duplicate_username(self):
        User.objects.create_user('existinguser', 'testpassword123')
        data = {
            'username': 'existinguser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('username', response.data)  # Adjust based on your actual error response structure


class UserLoginAPITestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse('token_obtain_pair')  # Adjust based on your actual login endpoint
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        # No need to create a token here since JWTs will be generated dynamically upon login

    def test_user_login_success_with_jwt(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)  # Check for access token in response
        self.assertIn('refresh', response.data)  # Check for refresh token in response

        # Optionally, validate the structure or header of the JWT, though this might be complex and
        # unnecessary for basic tests, as it involves decoding the JWT.
