#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'djoser>=2.0.0',
    'django-sms>=0.6.0'
    'django-phonenumber-field[phonenumberslite]>7.0.2'
]

test_requirements = ['pytest>=3', ]

setup(
    author="Sergio Isidoro",
    author_email='smaisidoro@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A Passwordless login add-on for Djoser (Django Rest Framework authentication)",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='djoser_passwordless',
    name='djoser_passwordless',
    packages=find_packages(include=['djoser_passwordless', 'djoser_passwordless.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/sergioisidoro/djoser_passwordless',
    version='0.1.0',
    zip_safe=False,
)
