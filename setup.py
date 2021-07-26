#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(
    name='Mushicoin',
    version='0.0.2',
    description='Experimental blockchain',
    author='Smelly',
    author_email='ilike2code1234@gmail.com',
    url='https://github.com/smellyslab/mushicoin',
    entry_points={
        'console_scripts': [
            'mushicoin = mushicoin.cli:main'
        ],
    },
    include_package_data=True,
    install_requires=['requests', 'wheel', 'pyyaml', 'flask', 'flask-socketio',
                      'pycrypto', 'm3-cdecimal', 'pyopenssl',
                      'werkzeug', 'tabulate', 'ecdsa', 'plyvel'],
    packages=find_packages(exclude=("tests", "tests.*")),
)
