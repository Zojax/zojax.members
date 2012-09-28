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

from zojax.catalog.interfaces import ICatalog
from zojax.wizard.step import WizardStep
from zojax.members.interfaces import IMembersAware
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.notifications.interfaces import IContentNotification
from zojax.content.space.utils import getSpace
from zojax.resourcepackage.library import includeInplaceSource

from interfaces import _
from zope.component._api import getUtility


class Notifications(WizardStep):

    renderDict = None
    notifications = None

    def update(self):
        includeInplaceSource(jssource)
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
        spaces = list(getUtility(ICatalog).searchResults(
            type={'any_of': ('content.space',)},
            traversablePath={'any_of': [context]}))

        spaces.append(context)
        for space in spaces:
            for member in space.members.values():
                principal = member.principal
                if principal is None:
                    continue
                title = member.title
                position = -1
                for pos, memb in enumerate(members):
                    if member.title in memb:
                        position = pos
                if position != -1:
                    members[position][1]['spaces'].append(space.title)
                else:
                    members.append((title, {'id': principal.id,
                                            'title': title,
                                            'spaces': [space.title]
                                            }))
        self.renderDict = self.createRenderDict(sorted(spaces, key=lambda sp: sp.title), members)
        self.members = [val[1] for val in members]
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

    def createRenderDict(self, spaces, members):
        rd = {}
        if spaces:
            for space in spaces:
                for member in space.members.values():
                    principal = member.principal
                    if principal is None:
                        continue
                    members_dict = dict(members)
                    if member.title in members_dict.keys():
                        if space.title in rd:
                            rd[space.title].append([member.title, members_dict[member.title]['spaces'], members_dict[member.title]['id']])
                        else:
                            rd[space.title] = [[member.title, members_dict[member.title]['spaces'], members_dict[member.title]['id']]]
        return rd

    def isAvailable(self):
        if not self.notifications or not self.renderDict:
            return False

        return super(Notifications, self).isAvailable()

jssource = """<script type="text/javascript">
$(document).ready(function(){
    $('input:checkbox').click(function(){
        $('input[type=checkbox][name=' + $(this).attr("name") + '][value=' + $(this).attr("value") + ']').not(this).each(function(){
            if($(this).is(':checked')){
               $(this).removeAttr('checked');
            } else {
               $(this).attr('checked', 'checked');
            }
        });
    });
});
</script>"""