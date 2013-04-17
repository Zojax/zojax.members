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
from zope.proxy import removeAllProxies

from zojax.batching.batch import Batch
from zojax.content.permissions.browser.wizard import ContentPermissions
from zojax.members.interfaces import IMembersAware
from zojax.security.utils import getPrincipals


class MembersAwareContentPermissions(ContentPermissions):

    def getPrincipals(self):
        context = removeAllProxies(self.context)
        members = removeAllProxies(IMembersAware(context).members).keys()

        batch = Batch(members, size=10, context=context, request=self.request)
        principals = getPrincipals(batch)

        return principals, batch
