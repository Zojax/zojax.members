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
from zope import interface, component
from zope.app.security.settings import Allow, Unset, Deny
from zope.securitypolicy.interfaces import IPrincipalRoleMap

from zojax.security.interfaces import IPrincipalGroups
from zojax.content.type.interfaces import IDraftedContent

from interfaces import IMembersAware


class MembersAwareLocalroles(object):
    component.adapts(IMembersAware)
    interface.implements(IPrincipalRoleMap)

    managers = ()
    principals = ()

    def __init__(self, context):
        self.context = context
        self.members = context.members

    def getPrincipalsForRole(self, role_id):
        principals = {}
        if role_id == 'group.Manager':
            for principal in self.members.managers:
                principals[principal] = 1
            return [(principal, Allow) for principal in principals.keys()]
        elif role_id == 'group.Member':
            return [(pname, Allow) for pname in self.members.principals \
                        if pname not in self.members.notapproved]
        else:
            return ()

    def getRolesForPrincipal(self, principal_id):
        roles = {'group.Manager':0, 'group.Member':0}
        if principal_id in self.members.managers:
            roles = {'group.Manager':1, 'group.Member':1}

        elif principal_id in self.members.principals and \
                principal_id not in self.members.notapproved:
            roles['group.Member'] = 1
        return [(role, value and Allow or Deny) for role, value in roles.items()]

    def getSetting(self, role_id, principal_id):
        if role_id == 'group.Manager':
            if principal_id in self.members.managers:
                return Allow
            return Deny


        if role_id == 'group.Member':
            if principal_id in self.members.principals and \
                    principal_id not in self.members.notapproved:
                return Allow
            return Deny

        return Unset

    def getPrincipalsAndRoles(self):
        pass


@component.adapter(IDraftedContent)
@interface.implementer(IPrincipalRoleMap)
def getMembersAwareLocalroles(context):
    return None
