#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Tomas Vitvar, https://vitvar.com, tomas.vitvar@oracle.com

from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import os
import re
import sys
import argparse
import glob

from setuptools import find_packages
from setuptools import setup

# read file content
def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()

# finds the version of the package 
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
        
# setup main 
# required modules
install_requires = [
    'urllib3==1.26.8',
    'requests==2.27.1']

setup(
    name='dms-collector',
    version=find_version("dms_collector", "__init__.py"),
    description='Oracle FMW DMS Spy collector utility',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Tomas Vitvar',
    author_email='tomas@vitvar.com',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3.5.0',
    scripts=['bin/dms-collector'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
