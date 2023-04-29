from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user
from django.conf import settings
from django.test.utils import override_settings

User = get_user_model()

class TestPasswordlessEmailTokenRequest(APITestCase, assertions.StatusCodeAssertionsMixin):
    url = reverse("passwordless_email_signup_request")

    def test_post_gibberish_will_return_validation_errors(self):
        data = {"email": "Totally an email address"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "REGISTER_NONEXISTENT_USERS": False
        })
    )
    def test_post_with_non_existing_user_should_return_400_if_registration_disabled(self):
        data = {"email": "super@duper.com"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "REGISTER_NONEXISTENT_USERS": True
        })
    )
    def test_post_request_with_new_user_successful_with_unusable_password_when_registration_enabled(self):
        data = {"email": "super@duper.com"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        user = User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        self.assertFalse(user.has_usable_password())

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "REGISTER_NONEXISTENT_USERS": True,
          "REGISTRATION_SETS_UNUSABLE_PASSWORD": False
        })
    )
    def test_post_request_with_new_user_successful_with_usable_password_when_registration_enabled(self):
        data = {"email": "super@duper.com"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        user = User.objects.filter(email=data["email"]).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.has_usable_password())

    def test_post_request_with_existing_user_successful(self):
        user = create_user()
        data = {"email": user.email}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_post_request_for_staff_fails(self):
        user = create_user()
        user.is_staff = True
        user.save()
        data = {"email": user.email}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "ALLOW_ADMIN_AUTHENTICATION": True
        })
    )
    def test_post_request_for_staff_succeeds_if_allowed(self):
        user = create_user()
        user.is_staff = True
        user.save()
        data = {"email": user.email}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "TOKEN_REQUEST_THROTTLE_SECONDS": None
        })
    )
    def test_post_request_user_should_not_have_more_than_one_active_token(self):
        user = create_user()
        data = {"email": user.email}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        user.djoser_passwordless_tokens.count() == 1
