# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

REQUIRES = [
    'spacy',
    'compound-jsonapi>=1.0.1',
]

setup(
    name='museum-map',
    version='0.0.1',
    description='Code for generating the thematic museum map',
    long_description='',
    author='Mark Hall',
    author_email='mark.hall@edgehill.ac.uk',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=REQUIRES,
    license='MIT',
    zip_safe=False
)
