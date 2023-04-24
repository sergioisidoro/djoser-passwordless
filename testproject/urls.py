from django.urls import include, re_path
from django.views.generic import TemplateView

urlpatterns = (
    re_path(r"^passwordless/", include("djoser_passwordless.urls")),
)
