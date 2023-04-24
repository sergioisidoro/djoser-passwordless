from djoser_passwordless.conf import settings
from djoser.conf import settings as djoser_settings
from rest_framework import status
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser_passwordless.constants import Messages
from djoser.compat import get_user_email
from djoser.views import TokenCreateView
from djoser import signals, utils

from .services import PasswordlessTokenService

class AbstractPasswordlessTokenRequestView(APIView):
    """
    This returns a callback challenge token we can trade for a user's Auth Token.
    """
    success_response = Messages.TOKEN_SENT
    failure_response = Messages.CANNOT_SEND_TOKEN

    permission_classes = settings.PERMISSIONS.passwordless_token_request

    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @property
    def token_request_identifier_field(self):
        raise NotImplementedError

    @property
    def token_request_identifier_type(self):
        raise NotImplementedError
    
    def send(self, token):
        raise NotImplementedError

    def _respond_ok(self):
        status_code = status.HTTP_200_OK
        response_detail = self.success_response
        return Response({'detail': response_detail}, status=status_code)
        
    def _respond_not_ok(self):
        status_code = status.HTTP_400_BAD_REQUEST
        response_detail = self.failure_response
        return Response({'detail': response_detail}, status=status_code)


    @method_decorator(settings.DECORATORS.token_request_rate_limit_decorator)  
    def post(self, request, *args, **kwargs):
        if self.token_request_identifier_type.upper() not in settings.ALLOWED_PASSWORDLESS_METHODS:
            # Only allow auth types allowed in settings.
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            # Might create user if settings allow it, or return the user to whom the token should be sent.
            user = serializer.save()
            
            if not user:
                self._respond_not_ok()
                
            # Create and send callback token
            token = PasswordlessTokenService.create_token(user, self.token_request_identifier_field)
            self.send(token)
            
            if token:
                return self._respond_ok()
            else:
                return self._respond_not_ok()
        else:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class PasswordlessEmailTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.SERIALIZERS.passwordless_email_token_request
    token_request_identifier_field = settings.EMAIL_FIELD_NAME
    token_request_identifier_type = 'email'

    def send(self, token):
        user = token.user
        context = {
            "user": user,
            "token": token.token,
            "short_token": token.short_token
          }
        to = [get_user_email(user)]
        settings.EMAIL.passwordless_request(self.request, context).send(to)


class PasswordlessMobileTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.SERIALIZERS.passwordless_mobile_token_request
    token_request_identifier_field = settings.MOBILE_FIELD_NAME
    token_request_identifier_type = 'mobile'
  
    def send(self, token):
        user = token.user
        context = {
            "user": user,
            "token": token.token,
            "short_token": token.short_token
          }
        to = getattr(user, settings.MOBILE_FIELD_NAME)
        return settings.SMS_SENDERS.passwordless_request(self.request, context).send(to)


class AbstractExchangePasswordlessTokenForAuthTokenView(TokenCreateView):
    """Use this endpoint to obtain user authentication token."""
    permission_classes = settings.PERMISSIONS.passwordless_token_exchange   
    
    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @method_decorator(settings.DECORATORS.token_redeem_rate_limit_decorator)  
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def _action(self, serializer):
        user = serializer.user

        if not user.is_active:
          user.is_active = True
          user.save()
          signals.user_activated.send(
              sender=self.__class__, user=user, request=self.request
          )
        
        token = utils.login_user(self.request, user)
        token_serializer_class = djoser_settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )


class EmailExchangePasswordlessTokenForAuthTokenView(AbstractExchangePasswordlessTokenForAuthTokenView):
    serializer_class = settings.SERIALIZERS.passwordless_email_token_exchange

class MobileExchangePasswordlessTokenForAuthTokenView(AbstractExchangePasswordlessTokenForAuthTokenView):
    serializer_class = settings.SERIALIZERS.passwordless_mobile_token_exchange

class StandaloneExchangePasswordlessTokenForAuthTokenView(AbstractExchangePasswordlessTokenForAuthTokenView):
    serializer_class = settings.SERIALIZERS.passwordless_standalone_token_exchange
