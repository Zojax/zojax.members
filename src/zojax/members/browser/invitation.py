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
import zope
from z3c.form import widget, validator
from zope.component import getUtility, queryUtility
from zope.index.text.parsetree import ParseError
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.batching.batch import Batch
from zojax.ownership.interfaces import IOwnership
from zojax.layoutform import button, Fields, PageletForm, interfaces
from zojax.catalog.interfaces import ICatalog
from zojax.content.actions.action import Action
from zojax.preferences.interfaces import IRootPreferences
from zojax.principal.invite.interfaces import IInvitations
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.personal.space.interfaces import IPersonalSpaceManager
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.members.interfaces import IMembers, IMembersAware

from interfaces import _, IInviteMembersAction, IInviteMembersForm


class Invitation(object):

    def update(self):
        context = self.context
        request = self.request

        id = context.id

        if 'form.button.accept' in request:
            if request.get('invitation') == id:
                invitation = getUtility(
                    IInvitations).get(request.get('invitation'))
                if invitation is not None:
                    invitation.accept()
                    IStatusMessage(request).add(
                        _('Invitation has been accepted.'))
                    self.redirect(request.URL)
                    return

        if 'form.button.reject' in request:
            if request.get('invitation') == id:
                invitation = getUtility(
                    IInvitations).get(request.get('invitation'))
                if invitation is not None:
                    invitation.reject()
                    IStatusMessage(request).add(
                        _('Invitation has been rejected.'))
                    self.redirect(request.URL)
                    return

        group = removeSecurityProxy(context.object)
        visible = checkPermission('zope.View', group)

        owner = IOwnership(context).owner
        profile = IPersonalProfile(owner, None)

        message = cgi.escape(context.message)
        message = message.replace(' ', '&nbsp;')
        message = message.replace('\n', '<br />')

        self.invitation = {
            'id': id,
            'title': group.title,
            'description': group.description,
            'created': IDCTimes(group).created,
            'members': len(group.members),
            'url': u'%s/'%absoluteURL(group, request),
            'message': message,
            'default': not visible or not bool(getattr(group, 'logo', None)),
            'sender': getattr(profile, 'title', _('Unknown member'))}


class InviteMembersAction(Action):
    interface.implements(IInviteMembersAction)
    component.adapts(IMembersAware, interface.Interface)

    title = _('Invite members')
    weight = 61
    contextInterface = IMembersAware
    permission = 'zojax.InviteGroupMember'

    @property
    def url(self):
        return '%s/invite.html'%absoluteURL(self.context, self.request)


class InviteMembersForm(PageletForm):

    label = _(u'Invite members')
    fields = Fields(IInviteMembersForm)

    def getContent(self):
        return {'message': u'Hello,\n\nI would like to invite you to join this group.\n\nRegards,\n%s'%(
                IPersonalProfile(self.request.principal).title)}

    def getMembers(self):
        manager = queryUtility(IPersonalSpaceManager)
        if manager is None:
            return ()
        self.managerURL = absoluteURL(manager, self.request)
        try:
            if self.request.has_key('form.widgets.search'):
                results = getUtility(ICatalog).searchResults(
                    type = {'any_of': ('personal.space',)},
                    searchableText = (self.request.get('form.widgets.search')),
                    searchContext = (manager,), sort_on='title')
            else:
                results = getUtility(ICatalog).searchResults(
                    type = {'any_of': ('personal.space',)},
                    searchContext = (manager,), sort_on='title')
        except ParseError, err:
            results = []
            IStatusMessage(self.request).add(_(str(err)), 'error')
        return Batch(results, size=30, context = self.context, request = self.request)

    def getMemberInfo(self, space):
        principal = space.principal
        if principal is None:
            return

        profile = IPersonalProfile(principal)
        avatar = profile.avatarUrl(self.request)
        members = self.context.members

        info = {
            'id': principal.id,
            'spaceid': space.__name__,
            'title': profile.title,
            'avatar': avatar,
            'member': members.isMember(principal.id)}
        return info

    @button.buttonAndHandler(_(u'Invite'), provides=interfaces.IAddButton)
    def handleSend(self, action):
        request = self.request
        data, errors = self.extractData()

        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'error')
        else:
            message = data['message']
            members = self.context.members
            getPrincipal = getUtility(IAuthentication).getPrincipal
            invitations = getUtility(IInvitations)
            group = removeAllProxies(self.context)

            for pid in request.get('principal.users', ()):
                try:
                    principal = getPrincipal(pid)
                except PrincipalLookupError:
                    continue

                if not invitations.catalog.search(
                    group, type = {'any_of': ('invitation.member',)},
                    principal = {'any_of': (pid,)}):
                    removeSecurityProxy(members).invite(pid, message)

            IStatusMessage(request).add(_(u'Invitations have been sent.'))
            self.redirect('.')

    @button.buttonAndHandler(_(u'Cancel'), provides=interfaces.ICancelButton)
    def handleCancel(self, action):
        self.redirect('.')

    @button.buttonAndHandler(_(u'Search'))
    def handleSearch(self, action):
        pass