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
from zope.component import getUtility
from zope.app.container.interfaces import IObjectAddedEvent

from zojax.activity.record import ActivityRecord
from zojax.activity.interfaces import IActivity, IActivityRecordDescription
from zojax.principal.invite.interfaces import IInvitationAcceptedEvent

from interfaces import _
from interfaces import IMember, IMemberApprovedEvent, IMemberJoinedActivityRecord


class MemberJoinedActivityRecord(ActivityRecord):
    interface.implements(IMemberJoinedActivityRecord)

    score = 0.0
    type = u'member.joined'
    verb = u'joined'


class MemberJoinedActivityRecordDescription(object):
    interface.implements(IActivityRecordDescription)

    title = _(u'Member')
    description = _(u'Person joined group.')


@component.adapter(IMemberApprovedEvent)
def memberJoinedHandler(ev):
    getUtility(IActivity).add(
        ev.member.__parent__.__parent__,
        MemberJoinedActivityRecord(principal=ev.member.__name__))
