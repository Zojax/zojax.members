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
from zope.proxy import removeAllProxies
from zope.component import getUtility, getUtilitiesFor
from zope.traversing.browser import absoluteURL

from zojax.table.table import Table
from zojax.table.column import Column
from zojax.wizard.step import WizardStep
from zojax.formatter.utils import getFormatter
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.content.table.author import AvatarColumn, AuthorNameColumn
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.ownership.interfaces import IOwnership
from zojax.members.interfaces import _, IMembers

from interfaces import IManageMembersTable


class ManageMembersTable(Table):
    interface.implements(IManageMembersTable)
    component.adapts(IMembers, interface.Interface, interface.Interface)

    title = _('Members')

    pageSize = 15
    enabledColumns = ('id', 'avatar', 'authorname',
                      'role', 'email', 'joined', 'approved')
    msgEmptyTable = _('There are no members in this group.')

    def initDataset(self):
        keys = list(removeAllProxies(self.context.notapproved))
        keys.extend([id for id in self.context.keys() if id not in keys])

        self.dataset = keys

    def records(self):
        if self.batch is not None:
            for content in self.batch:
                yield self.RecordClass(self, self.context[content])
        else:
            for content in self.dataset:
                yield self.RecordClass(self, self.context[content])


class IdColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    name = 'id'
    title = u''

    def query(self, default=None):
        return self.content.__name__

    def render(self):
        return u'<input type="checkbox" name="table.members.ids:list" value="%s" />'%(
            self.query())


class AvatarColumn(AvatarColumn):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    def getPrincipal(self, content):
        try:
            return content.principal
        except:
            return None


class AuthorNameColumn(AuthorNameColumn):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    title = _(u'Name')

    def getPrincipal(self, content):
        try:
            return content.principal
        except:
            return None


class RoleColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    name = 'role'
    title = _(u'Role in group')

    def query(self, default=None):
        members = self.content.__parent__
        if self.content.__name__ in members.managers:
            return _('Manager')
        else:
            return _('Member')


class EmailColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    name = 'email'
    title = u'Email'

    def query(self, default=None):
        try:
            principal = self.content.principal
        except:
            return None

        profile = IPersonalProfile(principal, None)
        if profile is not None:
            return profile.email


class JoinedColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    name = 'joined'
    title = _(u'Joined')

    def update(self):
        self.formatter = getFormatter(self.request, 'humanDatetime', 'medium')

    def query(self, default=None):
        joined = self.content.joined
        if joined:
            return self.formatter.format(joined)

        return u'---'


class ApprovedColumn(Column):
    component.adapts(
        interface.Interface, interface.Interface, IManageMembersTable)

    name = 'approved'
    title = _(u'Status')

    def query(self, default=None):
        if self.content.approved:
            return _('Approved')
        else:
            return _('Not yet approved')


class ManageMembersForm(WizardStep):

    owner = None

    def update(self):
        request = self.request
        context = self.context
        owner = IOwnership(self.context.__parent__).owner
        if owner is None:
            self.owner = {'title': _('Unknown principal'), 'desc': ''}
        else:
            self.owner = {'title': owner.title, 'desc': owner.description}

        pid = request.principal.id
        ids = request.get('table.members.ids', ())
        members = self.context
        #if pid in ids:
        #    IStatusMessage(request).add(_(u"You can't change your own membership"))

        if 'members.buttons.member' in request:
            if not ids:
                IStatusMessage(request).add(
                    _(u'Please select members.'), 'warning')
            else:
                changed = False
                for id in ids:
                    if id != pid:
                        members.toMember(id)
                        changed = True
                if changed:
                    IStatusMessage(request).add(_(u'Role has been changed.'))

        if 'members.buttons.manager' in request:
            if not ids:
                IStatusMessage(request).add(
                    _(u'Please select members.'), 'warning')
            else:
                changed = False
                for id in ids:
                    if id != pid:
                        members.toManager(id)
                        changed = True
                if changed:
                    IStatusMessage(request).add(_(u'Role has been changed.'))

        if 'members.buttons.remove' in request:
            if not ids:
                IStatusMessage(request).add(
                    _(u'Please select members.'), 'warning')
            else:
                changed = False
                for id in ids:
                    if id != pid and id in members:
                        del members[id]
                        changed = True
                if changed:
                    IStatusMessage(request).add(_(u'Members have been removed.'))

        if 'members.buttons.approve' in request:
            if not ids:
                IStatusMessage(request).add(
                    _(u'Please select members.'), 'warning')
            else:
                changed = False
                for id in ids:
                    members.approve(id)
                    changed = True
                if changed:
                    IStatusMessage(request).add(_(u'Members have been updated.'))

        super(ManageMembersForm, self).update()
