#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Django notification setup file for pip package '''
import ast
import re

from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')  # pylint: disable=invalid-name

with open('notifications/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(  # pylint: disable=invalid-name
        f.read().decode('utf-8')).group(1)))


setup(
    name='django-notifications-pro',
    version=version,
    description='GitHub notifications alike app for Django with expo push notifications',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/nachoborrelli/django-notifications',
    install_requires=[
        'django>=3.2',
        'django-model-utils>=3.1.0',
        'jsonfield>=2.1.0',
        'pytz',
        'swapper',
        'pandas>=2.2.0',
        'requests>=2.30',
        'packaging',
    ],
    extras_require={
        'expo': ['exponent-server-sdk~=2.0.0'],
        'crontab': ['django_crontab~=0.7.1'],
    },
    packages=[
        'notifications',
        'notifications.base',
        'notifications.templatetags',
        'notifications.migrations',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities'
    ],
    keywords='django notifications github action event stream expo push viewset cron crontab',
    license='MIT',
)
