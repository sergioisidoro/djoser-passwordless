# flake8: noqa E501
from django.apps import apps
from django.conf import Settings, LazySettings
from django.utils.module_loading import import_string

DJOSER_SETTINGS_NAMESPACE = "DJOSER_PASSWORDLESS"

auth_module, user_model = django_settings.AUTH_USER_MODEL.rsplit(".", 1)

User = apps.get_model(auth_module, user_model)


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super().__getattribute__(item)
        return val


default_settings = {
    "SHORT_TOKEN_LENGTH": 6,
    "LONG_TOKEN_LENGTH": 64,
    "SHORT_TOKEN_CHARS": "0123456789",
    "LONG_TOKEN_CHARS": "abcdefghijklmnopqrstuvwxyz0123456789",
    "TOKEN_LIFETIME": 600,
    "REGISTER_NONEXISTENT_USERS": True,
    "EMAIL_FIELD_NAME": "email",
    "MOBILE_FIELD_NAME": "phone_number",
    # If true, an attempt to redeem a token with the wrong token type
    # will count for the times a token has been used
    "INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN": False,
    "ALLOWED_PASSWORDLESS_METHODS": ["EMAIL", "MOBILE"],
    "MAX_TOKEN_USES": 1,
    "GENERATORS": ObjDict({
        "username_generator": "djoser_passwordless.utils.username_generator",
    }),
    "EMAIL": ObjDict ({
        "passwordless_request": "djoser_passwordless.email.PasswordlessRequestEmail",
    }),
    "SERIALIZERS": ObjDict({
        "passwordless_email_token_request": "djoser_passwordless.serializers.PasswordlessEmailTokenRequestSerializer",
        "passwordless_mobile_token_request": "djoser_passwordless.serializers.PasswordlessMobileTokenRequestSerializer",
        "passwordless_email_token_exchange": "djoser_passwordless.serializers.PasswordlessEmailTokenExchangeSerializer",
        'passwordless_mobile_token_exchange': 'djoser_passwordless.serializers.PasswordlessMobileTokenExchangeSerializer',
        'passwordless_standalone_token_exchange': "djoser_passwordless.serializers.StandalonePasswordlessExchangeSerializer"
    }),
    "PERMISSIONS": ObjDict({
        "passwordless_token_exchange": ["rest_framework.permissions.AllowAny"],
        "passwordless_token_request": ["rest_framework.permissions.AllowAny"],
    }),
    "DECORATORS": ObjDict({
        "token_request_rate_limit_decorator": "djoser_passwordless.utils.token_request_limiter",
        "token_redeem_rate_limit_decorator": "djoser_passwordless.utils.token_redeem_limiter",
    }),
    "SMS_SENDERS": ObjDict({
        "passwordless_request": "djoser_passwordless.sms.PasswordlessRequestSMS",
    }),
}

SETTINGS_TO_IMPORT = ["TOKEN_MODEL", "SOCIAL_AUTH_TOKEN_STRATEGY", "SMS_SENDER"]


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    global settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)
