#!/usr/bin/env python
# coding=utf-8
'''
The setup script for logkeycount
'''

from setuptools import setup, find_packages
import sys
import os

version = '0.1'

setup(name='logkeycount',
      version=version,
      description="Count the number of the specified keyword \
        present in log message, then send results to zabbix server",
      log_decription="""count the number of the specified key word present in \
        every log message line from rsyslog, then send statistics results to \
        zabbix server via calling zabbix_sender command line tool""",
      classifiers=[],
      keywords="log count tool depending on rsyslog's omprog",
      author='Rangochan',
      author_email='rangochan1989@gmail.com',
      url='https://github.com/rangochan/logkeycount',
      license='Apache License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
)
