
from django.utils.timezone import now, timedelta
from django.db.models import Q
from djoser_passwordless.conf import settings
from django.db import transaction, IntegrityError
from .utils import (
    create_challenge,
)
from .models import PasswordlessChallengeToken

class PasswordlessTokenService(object):
    @staticmethod
    def create_token(user, identifier_type):
        # We need to ensure the token is unique, so we'll wrap it in a
        # transaction that retries if the token is not unique.
        tries = 0
        # Only clear tokens that already go beyond the throttle time.
        PasswordlessChallengeToken.objects.delete_expired(settings.TOKEN_LIFETIME, settings.MAX_TOKEN_USES, settings.TOKEN_REQUEST_THROTTLE_SECONDS)
        try:
            with transaction.atomic():
                return PasswordlessTokenService._generate_create_token(user, identifier_type)
        except IntegrityError as exception:
            if tries < 5:
                tries += 1
                return PasswordlessTokenService._generate_create_token(user, identifier_type)
            else:
                # If we've cannot generate a unique token after 5 tries, we'll
                # raise the exception. Maybe add a message to the admin to cleanup
                # expired stale tokens, or to increase the token length.
                raise exception

    @staticmethod
    def should_throttle(user):
        if settings.TOKEN_REQUEST_THROTTLE_SECONDS:
            return user.djoser_passwordless_tokens.filter(created_at__gt=now() - timedelta(seconds=settings.TOKEN_REQUEST_THROTTLE_SECONDS)).count() > 0
        return False

    @staticmethod
    def _generate_create_token(user, identifier_type):
        # Remove all tokens for this user when issuing a new one
        user.djoser_passwordless_tokens.all().delete()
        token = PasswordlessChallengeToken.objects.create(
            token = create_challenge(settings.LONG_TOKEN_LENGTH, settings.LONG_TOKEN_CHARS),
            short_token = create_challenge(settings.SHORT_TOKEN_LENGTH, settings.SHORT_TOKEN_CHARS),
            token_request_identifier=identifier_type,
            user=user
        )
        return token
    

    @staticmethod
    def check_token(challenge, identifier_field, identifier_value):
        if not challenge:
            return None
        try:
            query = Q(token=challenge)
            if identifier_value and identifier_field:
                query = query | Q(
                  **{
                    "short_token": challenge,
                    "token_request_identifier": identifier_field,
                    "user__"+identifier_field: identifier_value,
                  }
                )
            token = PasswordlessChallengeToken.objects.get(query)
        except PasswordlessChallengeToken.DoesNotExist:
            if identifier_value and identifier_field and settings.INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN:
                # If the token is not found, we'll check if the identifier_value
                # and identifier_field match an existing token. If so, we'll increment the
                # number of attempts for the user. If the user has reached the
                # max number of attempts, we'll lock the user out.
                try:
                    tokens = PasswordlessChallengeToken.objects.filter(
                        **{
                            "token_request_identifier": identifier_field,
                            "user__"+identifier_field: identifier_value,
                        }
                    )
                    for token in tokens:
                        token.redeem()
                except PasswordlessChallengeToken.DoesNotExist:
                    pass
    
            return None

        if not token.is_valid(settings.TOKEN_LIFETIME, settings.MAX_TOKEN_USES):
            return None
            
        token.redeem()
        return token
