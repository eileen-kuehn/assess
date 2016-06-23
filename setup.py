#!/usr/bin/env python

import os
import setuptools
from distutils.core import setup

setup(
    name="assess",
    version="0.1",
    description="Comparison of different distance algorithms for dynamic trees",
    author="Eileen Kuehn",
    author_email="eileen.kuehn@kit.edu",
    url="https://bitbucket.org/teamkseta/assess",
    packages=setuptools.find_packages(),
    dependendy_links = ['git+ssh://git@bitbucket.org/eileenkuehn/gnmutils.git@develop#egg=gnmutils-0.1']
    install_requires=["zss", 'gnmutils'],
)
