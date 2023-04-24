from djoser import utils
from djoser_passwordless.conf import settings
from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from sms import send_sms

class SMSMessage(object):
    def __init__(self, request, context={}):
        self.request = request
        self.context = {} if context is None else context

    def get_context_data(self):
        context = self.context
        if self.request:
            site = get_current_site(self.request)
            context["user"] = context.get('user', None) or self.request.user
            context["site_name"] = context.get('site_name') or (
                getattr(django_settings, 'SITE_NAME', '') or site.name
            )
        return context

    def send(self, to):
        context = self.get_context_data()
        content = render_to_string(self.template_name, context)

        send_sms(
            content,
            None,
            [to],
            fail_silently=False
        )
        return context


class PasswordlessRequestSMS(SMSMessage):
    template_name = "mobile/passwordless_request.txt"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["token"] = context["short_token"]
        
        return context
