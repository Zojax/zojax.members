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
from pytz import utc
from datetime import datetime

from zope import interface
from zope.security.proxy import removeSecurityProxy
from zojax.principal.invite.invitation import ObjectInvitation

from interfaces import IMemberInvitation


class MemberInvitation(ObjectInvitation):
    interface.implements(IMemberInvitation)

    name = u''

    def __init__(self, principal, oid, message):
        super(MemberInvitation, self).__init__(principal, oid)

        self.message = message
        self.expires = datetime(2100, 1, 1, tzinfo=utc)

    def accept(self):
        members = removeSecurityProxy(self.object.members)

        if self.principal not in members:
            members.joinPrincipal(self.principal)

        super(MemberInvitation, self).accept()
