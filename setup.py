#!/usr/bin/env python

import os
import setuptools
from distutils.core import setup

setup(
    name="ASSESS",
    version="0.1",
    description="Comparison of different distance algorithms for dynamic trees",
    author="Eileen Kuehn",
    author_email="eileen.kuehn@kit.edu",
    url="https://bitbucket.org/teamkseta/assess",
    packages=setuptools.find_packages(),
    dependency_links=[
        os.path.expanduser("~/Development/libs/cachemap"),
        os.path.expanduser("~/Development/libs/gnmutils"),
        os.path.expanduser("~/Development/libs/utility")
    ],
)
