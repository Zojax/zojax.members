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
"""

$Id$
"""
from zojax.catalog.utils import Indexable
from zc.catalog.catalogindex import SetIndex

from interfaces import IMembersAware


def membersIndex():
    return SetIndex('value', Indexable('zojax.members.indexes.Members'))


class Members(object):

    def __init__(self, content, default=None):
        self.value = default

        content = IMembersAware(content, None)
        if content is not None and content.members is not None:
            self.value = tuple(content.members.keys())
