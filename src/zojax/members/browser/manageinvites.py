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
import cgi
from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import getUtility, getMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.app.security.interfaces import IAuthentication
from zope.contentprovider.interfaces import IContentProvider

from zojax.table.table import Table
from zojax.table.column import Column
from zojax.wizard.step import WizardStep
from zojax.formatter.utils import getFormatter
from zojax.layoutform import button, Fields, PageletForm, interfaces
from zojax.ownership.interfaces import IOwnership
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.principal.invite.interfaces import IInvitations
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.members.interfaces import IMembers
from zojax.members.browser.interfaces import _, IInvitationsTable


class MembersInvitations(WizardStep):

    label = title = _(u'Invitations')

    def update(self):
        request = self.request
        context = self.context

        ids = request.get('invitations', ())
        members = self.context

        if 'buttons.remove' in request:
            if not ids:
                IStatusMessage(request).add(
                    _(u'Please select invitations.'), 'warning')
            else:
                for id in ids:
                    context.removeInvitation(id)
                IStatusMessage(request).add(_(u'Invitations has been removed.'))

        self.table = getMultiAdapter(
            (context, request, self), IContentProvider, 'group.invitations')
        self.table.update()


class InvitationsTable(Table):
    interface.implements(IInvitationsTable)
    component.adapts(IMembers, interface.Interface, interface.Interface)

    title = _('Invitations')

    pageSize = 15
    enabledColumns = ('id', 'code', 'owner', 'principal', 'date')
    msgEmptyTable = _('There are no invitations in this group.')

    def initDataset(self):
        self.dataset = getUtility(IInvitations).getInvitationsByObject(
            removeAllProxies(self.context.__parent__))


class IdColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IInvitationsTable)

    name = 'id'
    title = u''

    def query(self, default=None):
        return self.content.__name__

    def render(self):
        return u'<input type="checkbox" name="invitations:list" value="%s" />'%(
            self.query())


class CodeColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IInvitationsTable)

    name = 'code'
    title = _(u'Invitation code')

    def query(self, default=None):
        return self.content.__name__


class OwnerColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IInvitationsTable)

    name = 'owner'
    title = _(u'Owner')

    def query(self, default=None):
        return IOwnership(self.content).owner

    def render(self):
        owner = self.query()
        if owner is not None:
            profile = IPersonalProfile(owner)
            space = IPersonalSpace(owner, None)
            if space is not None:
                return '<a href="%s">%s</a>'%(
                    absoluteURL(space, self.request), cgi.escape(profile.title))
            else:
                return cgi.escape(profile.title)
        else:
            return '----'


class PrincipalColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IInvitationsTable)

    name = 'principal'
    title = _(u'Member')

    def query(self, default=None):
        try:
            return getUtility(IAuthentication).getPrincipal(self.content.principal)
        except:
            return None

    def render(self):
        owner = self.query()
        if owner is not None:
            profile = IPersonalProfile(owner)
            space = IPersonalSpace(owner, None)
            if space is not None:
                return '<a href="%s">%s</a>'%(
                    absoluteURL(space, self.request), cgi.escape(profile.title))
            else:
                return cgi.escape(profile.title)
        else:
            return '----'


class DateColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IInvitationsTable)

    name = 'date'
    title = _(u'Date')

    def query(self, default=None):
        date = IDCTimes(self.content).created
        if date:
            return getFormatter(
                self.request, 'fancyDatetime', 'medium').format(date)

        return u'---'
