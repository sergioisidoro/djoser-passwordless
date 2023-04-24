# Djoser Passwordless
Djoser passwordless is a library that adds Passwordless authentication (via email or SMS) to the Djoser authentication ecosystem.
Although built on top of Djoser, reusing its settings and code and serializers, this project adds two major dependencies, and hence it is separate from Djoser
The dependencies are [django-sms](https://github.com/roaldnefs/django-sms) and [django-phonenumber-field](https://github.com/stefanfoulis/django-phonenumber-field)

Although these dependencies are needed for mobile, you can still use email only as passwordless authentication.

