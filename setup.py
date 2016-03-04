# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="shine",
    version='0.1.2',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    scripts=['shine/bin/shinectl.py'],
    install_requires=['colorlog'],
    url="https://github.com/dantezhu/shine",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="shine",
)
