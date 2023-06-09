from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user
from django.conf import settings
from django.test.utils import override_settings
from djoser_passwordless.conf import settings as djoser_passwordless_settings
from .utils import create_token
from django.utils import timezone
from datetime import timedelta
from unittest import mock


User = get_user_model()

class TestPasswordlessTokenExchange(APITestCase, assertions.StatusCodeAssertionsMixin):
    url = reverse("email_passwordless_token_exchange")
    standalone_url = reverse("standalone_passwordless_token_exchange")

    def test_should_fail_with_dummy_token(self):
        data = {"token": "dubidubidu"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_should_fail_with_short_token(self):
        token = create_token("email")
        data = {"token": token.short_token}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_should_accept_long_token_standalone(self):
        token = create_token("email")
        data = {"token": token.token}
        response = self.client.post(self.standalone_url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_should_accept_short_token_when_same_info_included(self):
        token = create_token("email")
        data = {
            "token": token.short_token,
            "email": token.user.email
            }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "MAX_TOKEN_USES": 1
        })
    )
    def test_should_allow_redeeming_token_only_limited_times(self):
        token = create_token("email")
        data = {
            "token": token.short_token,
            "email": token.user.email
            }
        response = self.client.post(self.url, data=data)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "MAX_TOKEN_USES": 2
        })
    )
    def test_should_allow_redeeming_token_only_limited_times(self):
        token = create_token("email")
        data = {
            "token": token.short_token,
            "email": token.user.email
        }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN": True
        })
    )
    def test_redeeming_wrong_token_redeems_it_if_configured(self):
        token = create_token("email")
        data = {
            "token": "bad-token",
            "email": token.user.email
        }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        token.refresh_from_db()
        self.assertEqual(token.uses, 2)

    @override_settings(
        DJOSER_PASSWORDLESS=dict(settings.DJOSER_PASSWORDLESS, **{
          "INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN": False
        })
    )
    def test_redeeming_wrong_token_does_not_redeem_it_if_configured(self):
        token = create_token("email")
        data = {
            "token": "bad-token",
            "email": token.user.email
        }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        token.refresh_from_db()
        self.assertEqual(token.uses, 0)

    def test_redeeming_expired_token_does_not_work(self):
        past_time = timezone.now() - timedelta(seconds=djoser_passwordless_settings.TOKEN_LIFETIME + 1)
        
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=past_time)):
          # Create a toke in the past
          token = create_token("email")

        data = {
            "token": token.short_token,
            "email": token.user.email
        }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)


    def test_redeeming_standalone_expired_token_does_not_work(self):
        past_time = timezone.now() - timedelta(seconds=djoser_passwordless_settings.TOKEN_LIFETIME + 1)
        
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=past_time)):
          # Create a toke in the past
          token = create_token("email")

        data = {
            "token": token.token,
        }
        response = self.client.post(self.standalone_url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)