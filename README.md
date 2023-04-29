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


## Credits
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

* Aaronn's `django-rest-framework-passwordless` project https://github.com/aaronn/django-rest-framework-passwordless
* Sunscrapers' Djoser project - https://github.com/sunscrapers/djoser
* Cookiecutter: https://github.com/audreyr/cookiecutter
* `audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

## License
* Free software: MIT license
* Do no harm