#!/usr/bin/env python

import os
import setuptools
from distutils.core import setup

repo_base_dir = os.path.abspath(os.path.dirname(__file__))
# pull in the packages metadata
package_about = {}
with open(os.path.join(repo_base_dir, "assess", "__about__.py")) as f:
    exec(f.read(), package_about)

if __name__ == '__main__':
    setup(
        name=package_about['__title__'],
        version=package_about['__version__'],
        descriptions=package_about['__summary__'],
        author=package_about['__author__'],
        author_email=package_about['__email__'],
        url="https://bitbucket.org/teamkseta/assess",
        packages=setuptools.find_packages(),
        dependency_links = ['git+ssh://git@github.com:MaineKuehn/dengraph.git',
                            'git+ssh://git@github.com:eileen-kuehn/treedistancegenerator.git'],
        install_requires=["zss", 'dengraph', 'treedistancegenerator', 'filelock'],
        # unit tests
        test_suite='assess_tests',
    )
