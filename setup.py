# -*- coding: utf-8 -*-
"""
    po2strings
    ----------

    This utility helps you to localise your Apple or Android applications.

    :copyright: (c) 2016 Qurami srl.
    :license: MIT, see LICENSE for more details.
"""

import re
import sys
import codecs
from os import path
from setuptools import setup, find_packages

VERSION = re.search("VERSION = '([^']+)'", codecs.open(
    path.join(path.dirname(__file__), 'po2strings', '__init__.py'),
    encoding="utf-8",
).read().strip()).group(1)

LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.rst')).read()

REQUIREMENTS = [
]

setup(
    name='po2strings',
    version=VERSION,
    url='http://qurami.com/',
    license='MIT',
    description='Converts PO/POT files into Apple .strings or Android .xml locale files.',
    long_description=LONG_DESCRIPTION,
    author='Gianfranco Reppucci',
    author_email='gianfranco.reppucci@qurami.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['po2strings'],
    package_data={
        'po2strings': ['importers/*']
    },
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'po2strings = po2strings.po2strings:main',
        ],
    },
)
