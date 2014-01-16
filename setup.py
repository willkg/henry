#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def get_version():
    VERSIONFILE = os.path.join('henry', '__init__.py')
    VSRE = r"""^__version__ = ['"]([^'"]*)['"]"""
    version_file = open(VERSIONFILE, 'rt').read()
    return re.search(VSRE, version_file, re.M).group(1)


setup(
    name='henry',
    version=get_version(),
    description='Henry is a GitHub issues cli',
    long_description=readme + '\n\n' + history,
    author='Will Kahn-Greene',
    author_email='willkg@bluesock.org',
    url='https://github.com/willkg/henry',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/henry-cmd'],
    install_requires=[
        'blessings',
        'requests',
    ],
    license="BSD",
    zip_safe=True,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
