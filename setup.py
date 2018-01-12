#!/usr/bin/env python

from setuptools import setup

setup(
    name='shelfy',
    version='0.1',
    packages=['shelfy'],
    include_package_data=True,
    install_requires=[
        'flask',
    ]
)
