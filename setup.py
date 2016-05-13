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
    dependency_links=[
        os.path.expanduser("~/Development/python/cachemap"),
        os.path.expanduser("~/Development/python/gnmutils"),
        os.path.expanduser("~/Development/python/utility")
    ],
    install_requires=["cachemap", "gnmutils", "utility"],
)
