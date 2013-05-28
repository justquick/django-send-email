#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='django-send-email',
    version='0.1.0',
    packages=['django_send_email', 'django_send_email.management', 'django_send_email.management.commands'],
    license='BSD License',
    description="Send emails from the command line using Django's settings",
    long_description=README,
    url='https://github.com/justquick/django-send-email',
    author='Justin Quick',
    author_email='justquick@gmail.com',
    classifiers=[
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email'
    ],
)
