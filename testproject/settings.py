import os

DEBUG = True

BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECRET_KEY = "_"

MIDDLEWARE = ["django.contrib.sessions.middleware.SessionMiddleware"]


INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "templated_mail",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "djoser_passwordless",
    "testapp",
)

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
}

ROOT_URLCONF = "urls"

TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

DJOSER = {
}

DJOSER_PASSWORDLESS = {
}