# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='StockX',
    version='0.1.0',
    description='Python GUI application for trading stocks, forcasting stock prices and perform charting and basic technical analysis of stocks trading in the National Stock Exchange of India using Upstox Developer API.',
    long_description=readme,
    author='Sourav Basu Roy',
    author_email='wildr.slimshady@gmail.com',
    url='https://github.com/s13rw81/StockX',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

