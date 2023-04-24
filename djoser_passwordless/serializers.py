from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, validators
from djoser_passwordless.constants import Messages
from django.contrib.auth import get_user_model
from .services import PasswordlessTokenService
from djoser.conf import settings

User = get_user_model()

class AbstractPasswordlessTokenRequestSerializer(serializers.Serializer):
    @property
    def token_request_identifier_field(self):
        return NotImplementedError("Passwordless request needs to define at least one field to request a token with.")
    
    def find_user_by_identifier(self, identifier_value):
        try:
            return User.objects.get(**{self.token_request_identifier_field: identifier_value})
        except User.DoesNotExist:
            return None

    def validate(self, data):
        validated_data = super().validate(data)
        identifier_value = validated_data[self.token_request_identifier_field]
        user = self.find_user_by_identifier(identifier_value)
        if not settings.PASSWORDLESS["REGISTER_NONEXISTENT_USERS"] and not user:
            raise serializers.ValidationError(Messages.CANNOT_SEND_TOKEN)
        return validated_data

    def create(self, validated_data):
        identifier_value = validated_data[self.token_request_identifier_field]
        user = self.find_user_by_identifier(identifier_value)

        if settings.PASSWORDLESS["REGISTER_NONEXISTENT_USERS"] is True and not user:
            attributes = {
                self.token_request_identifier_field: identifier_value,
                User.USERNAME_FIELD: settings.PASSWORDLESS["GENERATORS"].username_generator(),
            }
            user = User.objects.create(**attributes)
            user.set_unusable_password()
            user.save()
        return user


class PasswordlessEmailTokenRequestSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[settings.EMAIL_FIELD_NAME] = serializers.EmailField(required=True)
    
    @property
    def token_request_identifier_field(self):
        return settings.PASSWORDLESS["EMAIL_FIELD_NAME"]


class PasswordlessMobileTokenRequestSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[settings.PASSWORDLESS["MOBILE_FIELD_NAME"]] = PhoneNumberField(required=True)

    @property
    def token_request_identifier_field(self):
        return settings.PASSWORDLESS["MOBILE_FIELD_NAME"]
    

class PasswordlessEmailTokenRequestSerializer(PasswordlessEmailTokenRequestSerializerMixin, AbstractPasswordlessTokenRequestSerializer):
    pass

class PasswordlessMobileTokenRequestSerializer(PasswordlessMobileTokenRequestSerializerMixin, AbstractPasswordlessTokenRequestSerializer):
    pass


# EXCHANGE (Turning a OTP into an Auth token)
class AbstractPasswordlessTokenExchangeSerializer(serializers.Serializer):
    @property
    def token_request_identifier_field(self):
        return None

    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    }
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        super().validate(attrs)
        valid_token = PasswordlessTokenService.check_token(
              attrs.get("token", None),
              self.token_request_identifier_field,
              attrs.get(self.token_request_identifier_field, None),
          )
        if valid_token:
            self.user = valid_token.user
            return attrs
        self.fail("invalid_credentials")


class PasswordlessEmailTokenExchangeSerializer(PasswordlessEmailTokenRequestSerializerMixin, AbstractPasswordlessTokenExchangeSerializer):
    pass
    

class PasswordlessMobileTokenExchangeSerializer(PasswordlessMobileTokenRequestSerializerMixin, AbstractPasswordlessTokenExchangeSerializer):
    pass
    

class StandalonePasswordlessExchangeSerializer(serializers.Serializer):
    pass