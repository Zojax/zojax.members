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
from zope.component import getAdapter, getAdapters
from zope.app.security.interfaces import IAuthenticatedGroup, IEveryoneGroup

from zojax.wizard.step import WizardStep
from zojax.members.interfaces import IMembersAware
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.notifications.interfaces import IContentNotification
from zojax.content.space.utils import getSpace 

from interfaces import _


class Notifications(WizardStep):

    members = None
    notifications = None

    def update(self):
        request = self.request
        context = self.context

        context = IMembersAware(getSpace(context), None)
        if context is None:
            return

        notifications = []
        for name, notification in getAdapters((self.context,), IContentNotification):
            notifications.append((notification.title, name, notification))

        notifications.sort()
        self.notifications = [notification for title, name, notification
                              in notifications]

        members = []
        for member in context.members.values():
            principal = member.principal
            if principal is None:
                continue

            title = member.title
            members.append((title, {'id': principal.id,
                                    'title': title,
                                    'principal': principal}))

        members.sort()
        self.members = [info for _t, info in members]

        if 'notifications.save' in request:
            checked = {}
            for id in request.get('notifications', ()):
                pid, nid = id.split(':', 1)
                data = checked.setdefault(nid, [])
                data.append(pid)

            for notification in self.notifications:
                data = checked.get(notification.type, [])
                for member in self.members:
                    if member['id'] in data:
                        notification.subscribe(member['id'])
                    else:
                        notification.unsubscribe(member['id'])

            IStatusMessage(request).add(
                _('Email notification subscriptions have been updated.'))

    def isAvailable(self):
        if not self.notifications or not self.members:
            return False

        return super(Notifications, self).isAvailable()
