from django.urls import include, re_path

urlpatterns = (
    re_path(r"^passwordless/", include("djoser_passwordless.urls")),
)
