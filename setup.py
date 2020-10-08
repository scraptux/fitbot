# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='fitbot',
    version='0.0.1',
    description='FitBot is a telegram bot helping you to keep track of your gym performance',
    long_description=readme,
    author='scraptux',
    url='https://github.com/scraptux/fitbot',
    license=license,
    packages=find_packages()
)
