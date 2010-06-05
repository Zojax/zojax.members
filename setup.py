##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zojax.members package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name = 'zojax.members',
      version = version,
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      description = "Group members",
      long_description = (
        'Detailed Documentation\n' +
        '======================\n'
        + '\n\n' +
        read('CHANGES.txt')
        ),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      url='http://zojax.net/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['zojax',],
      install_requires = ['setuptools',
                          'zope.component',
                          'zope.interface',
                          'zope.publisher',
                          'zope.traversing',
                          'zope.i18nmessageid',
                          'zope.lifecycleevent',
                          'zope.security',
                          'zope.securitypolicy',
                          'zope.app.intid',
                          'zope.app.component',
                          'zope.app.security',

                          'zojax.batching',
                          'zojax.catalog',
                          'zojax.security',
                          'zojax.ownership',
                          'zojax.content.activity',
                          'zojax.content.type',
                          'zojax.content.space',
                          'zojax.content.notifications',
                          'zojax.content.table',
                          'zojax.personal.space',
                          'zojax.principal.invite',
                          'zojax.principal.profile',
                          'zojax.principal.field',
                          'zojax.layout',
                          'zojax.layoutform',
                          'zojax.statusmessage',
                          'zojax.table',
                          'zojax.formatter',
                          'zojax.mailtemplate',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.component',
                                  'zope.app.zcmlfiles',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  'zojax.autoinclude',
                                  'zojax.personal.content',
                                  'zojax.personal.profile',
                                  'zojax.personal.invitation',
                                  'zojax.principal.roles',
                                  'zojax.principal.users'
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
