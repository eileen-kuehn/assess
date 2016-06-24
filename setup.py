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
    dependency_links = ['git+ssh://git@bitbucket.org/eileenkuehn/gnmutils.git@develop#egg=gnmutils-0.1',
                        'git+ssh://git@gitlab.scc.kit.edu/fq8360/cachemap.git@develop#egg=cachemap-0.1'],
    install_requires=["zss", 'gnmutils==0.1', 'cachemap==0.1'],
)
