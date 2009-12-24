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
from zope import interface, event
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from zojax.content.actions.action import Action
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.members.interfaces import _, IMembersAware
from zojax.members.browser.interfaces import IJoinGroupAction


class Join(object):

    def update(self):
        context = self.context
        request = self.request

        if 'form.join' in request:
            context.members.join()
            member = context.members[request.principal.id]

            if member.approved:
                IStatusMessage(request).add(_('You have been joined to group.'))
            else:
                IStatusMessage(request).add(
                    _('Your membership has been submitted. Waiting manager approvement.'))
            self.redirect('./')

        if 'form.cancel' in request:
            self.redirect('./')


class JoinAction(Action):
    interface.implements(IJoinGroupAction)

    weight = 60
    title = _(u'Join this group')
    permission = 'zojax.JoinGroup'
    contextInterface = IMembersAware

    @property
    def url(self):
        return '%s/join.html'%(absoluteURL(self.context, self.request))

    def isAvailable(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return False

        if not self.context.members.isMember(self.request.principal.id):
            return super(JoinAction, self).isAvailable()

        return False
