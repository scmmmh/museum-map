# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'spacy',
    'compound-jsonapi>=1.0.1',
    'plaster_pastedeploy',
    'pyramid >= 1.9a',
    'pyramid_retry',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'kajiki',
    'pywebtools>=1.1.3',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

setup(
    name='museum-map',
    version='0.0.4',
    description='Code for generating the thematic museum map',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Mark Hall',
    author_email='mark.hall@edgehill.ac.uk',
    license='MIT',
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = museum_map:main',
        ],
        'console_scripts': [
            'MuseumMap = museum_map.scripts.main:cli'
        ],
    },
)
