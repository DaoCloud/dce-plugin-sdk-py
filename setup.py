#!/usr/bin/env python
import os

from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

install_requires = []

setup(
    name="dce-plugin-sdk",
    version='0.1',
    description="DCE plugin SDK for Python.",
    url='https://github.com/DaoCloud/dce-plugin-sdk-py',
    packages=['dce_plugin'],
    install_requires=install_requires,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
)
