from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^request/email/$",
        views.PasswordlessEmailTokenRequestView.as_view(),
        name="passwordless_email_signup_request",
    ),
    re_path(
        r"^request/mobile/$",
        views.PasswordlessMobileTokenRequestView.as_view(),
        name="passwordless_mobile_signup_request",
    ),
    re_path(
        r"^exchange/mobile$",
        views.MobileExchangePasswordlessTokenForAuthTokenView.as_view(),
        name="mobile_passwordless_token_exchange",
    ),
    re_path(
        r"^exchange/email$",
        views.EmailExchangePasswordlessTokenForAuthTokenView.as_view(),
        name="email_passwordless_token_exchange",
    ),
    re_path(
        r"^exchange/standalone$",
        views.StandaloneExchangePasswordlessTokenForAuthTokenView.as_view(),
        name="email_passwordless_token_exchange",
    )
]
