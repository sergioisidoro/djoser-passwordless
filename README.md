**⛔️ WORK IN PROGRESS - not yet released**
![Main status](https://github.com/sergioisidoro/djoser-passwordless/actions/workflows/test-suite.yml/badge.svg)
[![codecov](https://codecov.io/gh/sergioisidoro/djoser-passwordless/branch/main/graph/badge.svg?token=96USU05I2T)](https://codecov.io/gh/sergioisidoro/djoser-passwordless)

# Djoser passwordless
A Passwordless login add-on for Djoser (Django Rest Framework authentication). Built with `djoser`, `django-sms` and `django-phonenumber-field`

## 🔑 Before you start!
Please consider your risk and threat landscape before adopting this library. 

Authentication is always a trade-off of usability and security. This library has been built to give you the power to adjust those trade-offs as much as possible, and made an attempt to give you a reasonable set of defaults, but it's up to you to make those decisions. Please consider the following risks bellow 

## Installation 
```.sh
pip install djoser_passwordless
```

`settings.py`
```.py
INSTALLED_APPS = (
    ...
    "djoser",
    "djoser_passwordless",
    ...
)
...
DJOSER_PASSWORDLESS = {
    "ALLOWED_PASSWORDLESS_METHODS": ["EMAIL", "MOBILE"]
}
```
**Remember to set the settings for `django-sms` and `django-phonenumber-field`** if you are using mobile token requests

```
urlpatterns = (
    ...
    re_path(r"^passwordless/", include("djoser_passwordless.urls")),
    ...
)
```

## 🕵️ Risks 
### Brute force
Although token requests are throttled by default, and token lifetime is limited, if you know a user email/phone it is possible to continuously request tokens (the default throttle is 1 minute), and try to brute force that token during the token lifetime (10 minutes).

#### Mitigations
* Set `INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN` to `True`, so that any attempts at redeeming a token from an account will count as a user (`MAX_TOKEN_USES` is default set to 1) - **Tradeoff** is that if a user is being a victim of brute force attack, they will not be able to login with passwordless tokens, since it's likely the attacker will exhaust the token uses with failed attempts 

* Set `DECORATORS.token_redeem_rate_limit_decorator` or `DECORATORS.token_request_rate_limit_decorator` with your choice of request throttling library. - **Tradeoff** is that if there is an attacker hitting your service, you might prevent **any** user from logging in because someone is hitting this endpoint, so beware how you implement it. Note that because request limiting usually requires a key value db like redis, it is explicitly left out of this project to reduce it's dependencies and configuration needs.

## Features
* International phone number validation and standardization (expects db phone numbers to be in same format)
* Basic throttling
* Configurable tokens
* Short (for SMS) and long tokens for magic links
* Configurable serializers, permissions and decorators.

## Examples:
**Requesting a token**
```.sh
curl --request POST \
  --url http://localhost:8000/passwordless/request/email/ \
  --data '{
	"email": "sergioisidoro@example.com"
}'
```
Response
```.json
{
	"detail": "A token has been sent to you"
}
```

**Exchanging a one time token for a auth token**
```.sh
curl --request POST \
  --url http://localhost:8000/passwordless/exchange/ \
  --data '{
	"email": "sergioisidoro@example.com"
	"token": "902488"
}'
```
```.json
{
	"auth_token": "3b8e6a2aed0435f95495e728b0fb41d0367a872d"
}
```

## Config

#### Basic configuration

* `ALLOWED_PASSWORDLESS_METHODS` (default=["email"]) - Which methods can be used to request a token? (Valid - `["email", "mobile"]`)
* `EMAIL_FIELD_NAME` (default="email") - Name of the user field that holds the email info
* `MOBILE_FIELD_NAME` (default="phone_number") - Name of the user field that holds phone number info
* `SHORT_TOKEN_LENGTH` (default=6) - The length of the short tokens
* `LONG_TOKEN_LENGTH` (default=64) - The length of the tokens that can redeemed standalone (without the original request data)
* `SHORT_TOKEN_CHARS` (default="0123456789") - The characters to be used when generating the short token
* `LONG_TOKEN_CHARS` (default="abcdefghijklmnopqrstuvwxyz0123456789") - Tokens used to generate the long token
* `TOKEN_LIFETIME` (default=600) - Number of seconds the token is valid
* `MAX_TOKEN_USES` (default=1) - How many times a token can be used - This can be adjusted because some email clients try to follow links, and might accidentally use tokens.
* `TOKEN_REQUEST_THROTTLE_SECONDS` - (default=60) - How many seconds to wait before allowing a new token to be issued for a particular user
* `ALLOW_ADMIN_AUTHENTICATION` (default=False) - Allow admin users to login without password (checks `is_admin` and `is_staff` from Django `AbstractUser`)
* `REGISTER_NONEXISTENT_USERS` (default=False) - Register users who do not have an account and request a passwordless login token? - Will generate a random username which is configurable (See. conf.py)
* `REGISTRATION_SETS_UNUSABLE_PASSWORD` (Default=True) - When unusable password is set, users cannot reset passwords via the normal Django flows. This means users registered via passwordless cannot login through password.
* `INCORRECT_SHORT_TOKEN_REDEEMS_TOKEN` (default=False) - Should incorrect short token auth attempts count to the uses of a token? When set to true, together with `MAX_TOKEN_USES` to 1, this means a token has only one shot at being used.
* `PASSWORDLESS_EMAIL_LOGIN_URL` (default=None) - URL template for the link redeeming the standalone link: eg `my-app://page/{token}`


## Credits
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

* Aaronn's `django-rest-framework-passwordless` project https://github.com/aaronn/django-rest-framework-passwordless
* Sunscrapers' Djoser project - https://github.com/sunscrapers/djoser
* Cookiecutter: https://github.com/audreyr/cookiecutter
* `audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

## License
* Free software: MIT license
* Do no harm