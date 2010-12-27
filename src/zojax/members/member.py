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
from persistent import Persistent
from zope import interface, event, component
from zope.location import Location
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.authentication.utils import getPrincipal
from zojax.principal.profile.interfaces import IPersonalProfile

from interfaces import _, IMember


class Member(Persistent, Location):
    interface.implements(IMember)

    joined = None
    approved = True

    @property
    def principal(self):
        try:
            return getPrincipal(self.__name__)
        except PrincipalLookupError:
            return None

    @property
    def title(self):
        profile = IPersonalProfile(self.principal, None)
        if profile is not None:
            return profile.title

        return _('Unknown')

    @property
    def description(self):
        return self.principal.description

    @property
    def space(self):
        return self.profile.space

    @property
    def profile(self):
        return IPersonalProfile(self.principal, None)


@component.adapter(IMember, IObjectRemovedEvent)
def memberRemoved(object, ev):
    event.notify(ObjectModifiedEvent(ev.oldParent.__parent__))
