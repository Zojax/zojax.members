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
from datetime import datetime, timedelta
from rwproperty import getproperty, setproperty
from BTrees.OOBTree import OOBTree, OOTreeSet

from zope import interface, event, component
from zope.component import getUtility, queryUtility
from zope.proxy import removeAllProxies
from zope.datetime import parseDatetimetz
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.app.intid.interfaces import IIntIds, IIntIdAddedEvent
from zope.securitypolicy.interfaces import \
    Allow, IRole, IRolePermissionMap, IRolePermissionManager

from zojax.catalog.utils import getRequest
from zojax.ownership.interfaces import IOwnership
from zojax.content.type.container import BaseContentContainer
from zojax.content.space.interfaces import IWorkspace, IInactiveWorkspaceFactory
from zojax.content.permissions.utils import updatePermissions
from zojax.security.interfaces import IPublicRole
from zojax.principal.invite.interfaces import IInvitations

from interfaces import _, MemberApprovedEvent
from interfaces import IMembers, IMembersAware, IMemberRoleManagement

from member import Member
from invitation import MemberInvitation


class Members(BaseContentContainer):
    interface.implements(IWorkspace, IMembers, IMemberRoleManagement)

    title = _(u'Members')
    description = u''
    approving = True

    def __init__(self, **kw):
        super(Members, self).__init__(**kw)

        self.joined = OOBTree()
        self.notapproved = OOTreeSet()

    @getproperty
    def joining(self):
        roles = []
        for rid, setting in IRolePermissionMap(
            self.__parent__).getRolesForPermission('zojax.JoinGroup'):
            if setting is Allow:
                role = queryUtility(IRole, rid)
                if IPublicRole.providedBy(role):
                    roles.append(rid)

        return roles

    @setproperty
    def joining(self, value):
        roles = IRolePermissionManager(self.__parent__)
        for rid in value:
            role = queryUtility(IRole, rid)
            if IPublicRole.providedBy(role):
                roles.grantPermissionToRole('zojax.JoinGroup', rid)
            else:
                roles.denyPermissionToRole('zojax.JoinGroup', rid)

    @getproperty
    def invites(self):
        value = []
        roles = [
            role for role, setting in IRolePermissionMap(
                self.__parent__).getRolesForPermission('zojax.InviteGroupMember')
            if setting is Allow]
        if 'group.Member' in roles:
            value.append('member')
        if 'group.Manager' in roles:
            value.append('manager')

        return value

    @setproperty
    def invites(self, value):
        roles = IRolePermissionManager(self.__parent__)
        for val, role in [('member', 'group.Member'),
                          ('manager', 'group.Manager')]:
            if val in value:
                roles.grantPermissionToRole('zojax.InviteGroupMember', role)
            else:
                roles.unsetPermissionFromRole('zojax.InviteGroupMember', role)

    def join(self):
        request = getRequest()
        if request is not None:
            self.joinPrincipal(request.principal.id, self.approving)

    def remove(self):
        request = getRequest()
        if request is not None:
            self.removePrincipal(request.principal.id)

    def joinPrincipal(self, principalId, approved=True,
                      _td = timedelta(milliseconds=1)):
        if principalId not in self:
            member = Member()
            event.notify(ObjectCreatedEvent(member))
            self[principalId] = member

            joined = parseDatetimetz(str(datetime.now()))
            while joined in self.joined:
                joined = joined + _td

            member.joined = joined
            self.joined[joined] = principalId

            if not approved:
                member.approved = False
                self.notapproved.insert(principalId)
            else:
                event.notify(MemberApprovedEvent(member))

            event.notify(ObjectModifiedEvent(self.__parent__))
            updatePermissions(self.__parent__)

    def isMember(self, principalId):
        return principalId in self

    def isManager(self, principalId):
        return principalId in self.managers

    @Lazy
    def managers(self):
        self.managers = ()
        self._p_changed = True
        return self.managers

    @property
    def principals(self):
        return self.keys()

    def toMember(self, id):
        if id in self:
            if id in self.managers:
                managers = list(self.managers)
                managers.remove(id)
                self.managers = tuple(managers)
                updatePermissions(self.__parent__)
                event.notify(ObjectModifiedEvent(self.__parent__))

    def toManager(self, id):
        if id in self:
            if id not in self.managers:
                managers = list(self.managers)
                managers.append(id)
                self.managers = tuple(managers)
                updatePermissions(self.__parent__)
                event.notify(ObjectModifiedEvent(self.__parent__))

    def approve(self, id):
        if id in self:
            member = self[id]
            if not member.approved:
                del member.approved
                self.notapproved.remove(id)

                event.notify(MemberApprovedEvent(member))
                event.notify(ObjectModifiedEvent(self.__parent__))
                updatePermissions(self.__parent__)

    def __delitem__(self, key):
        member = self[key]
        self.toMember(key)
        del self.joined[member.joined]

        if key in self.notapproved:
            self.notapproved.remove(key)

        super(Members, self).__delitem__(key)
        updatePermissions(self.__parent__)

    def invite(self, principal, message):
        invitation = MemberInvitation(
            principal, getUtility(IIntIds).getId(self.__parent__), message)

        IOwnership(invitation).ownerId = getRequest().principal.id
        event.notify(ObjectCreatedEvent(invitation))

        getUtility(IInvitations).storeInvitation(invitation)

        return invitation

    def removeInvitation(self, id):
        configlet = removeAllProxies(getUtility(IInvitations))

        invitation = configlet.get(id)
        if invitation is not None and \
                invitation.oid == getUtility(IIntIds).getId(self.__parent__):
            del configlet[id]


class MembersFactory(object):
    interface.implements(IMembers, IInactiveWorkspaceFactory)

    name = u'members'
    title = _(u'Members')
    description = u''
    weight = 1

    def __init__(self, space):
        self.space = space

    def get(self):
        return self.space.get('members')

    def install(self):
        return self.space.get('members')

    def uninstall(self):
        pass

    def isInstalled(self):
        return True

    def isAvailable(self):
        return True


@component.adapter(IMembersAware, IIntIdAddedEvent)
def membersAwareObjectCreated(object, ev):
    if 'members' not in object:
        members = Members()
        event.notify(ObjectCreatedEvent(members))
        object['members'] = members

    request = getRequest()
    if request is not None:
        pid = request.principal.id
        members = object['members']
        members.joinPrincipal(pid,)
        members.toManager(pid)

    event.notify(ObjectModifiedEvent(object))
