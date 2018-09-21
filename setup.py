#!/usr/bin/env python

import os
import subprocess
import sys

from setuptools import setup

if sys.version_info < (3, 6):
    raise RuntimeError("This package requires Python 3.6 or later")


def get_version():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(current_dir, 'VERSION')
    if os.path.isfile(version_file):
        with open(version_file, 'r') as file:
            version = file.read().strip()
    else:
        version = subprocess.Popen("git describe --long | cut -d - -f 1-1", shell=True, stdout=subprocess.PIPE).stdout.read().strip().decode()
    return version


install_requires = [l.strip() for l in open('requirements.txt', 'r').readlines()]

setup(
    name='redis_lock',
    version=get_version(),
    author='ZhengYue',
    author_email='zyzzy0602@163.com',
    description='A distributed lock implement by Redis',
    url='https://github.com/yuezheng/Kado',
    packages=['redis_lock'],
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3.6',
    zip_safe=False
)