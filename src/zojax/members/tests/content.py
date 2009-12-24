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
from zope import interface
from zojax.content.type.interfaces import IItem
from zojax.members.interfaces import IMembersAware
from zojax.content.space.content import ContentSpace


class IGroup(IItem):
    pass


class Group(ContentSpace):
    interface.implements(IGroup, IMembersAware)

    showTabs = True
    showHeader = True
    workspaces = ('members',)
    defaultWorkspace = 'members'

    @property
    def members(self):
        return self['members']
