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
from datetime import date
from email.Utils import formataddr

from zope import interface, component
from zope.component import getUtility, getMultiAdapter, getAdapters
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.component import getUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.app.component.hooks import getSite
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.catalog.utils import getRequest
from zojax.ownership.interfaces import IOwnership
from zojax.mailtemplate.interfaces import IMailTemplate, IMailHeaders
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.mailtemplate.base import MailTemplateBase


from zojax.members.interfaces import IMemberInvitation


class MemberMessageNotification(MailTemplateBase):

    def update(self):
        super(MemberMessageNotification, self).update()

        context = self.context
        request = self.request

        group = removeAllProxies(context.context).__parent__
        visible = checkPermission('zope.View', group)

        owner = IOwnership(group).owner
        profile = IPersonalProfile(owner, None)

        message = cgi.escape(context.message)
        message = message.replace(' ', '&nbsp;')
        message = message.replace('\n', '<br />')

        self.title = group.title
        self.sender = getattr(profile, 'title', 'Unknown member')

        self.info = {
            'title': group.title,
            'description': group.description,
            'created': IDCTimes(group).created,
            'members': len(group),
            'url': '%s/'%absoluteURL(group, request),
            'message': message,
            'default': not visible or not bool(getattr(group, 'logo', None)),
            'sender': self.sender}

        if profile is not None:
            self.addHeader(u'From', formataddr((self.sender, profile.email),))

        self.site = getSite()
        self.siteTitle = getattr(self.site, 'title', u'') or self.site.__name__
        self.siteURL = u'%s'%absoluteURL(self.site, request)

    @property
    def subject(self):
        return u'%s: %s sent you a message in %s'%(
            self.siteTitle, self.sender, self.title)

    @property
    def messageId(self):
        return u'<%s@zojax>'%self.context.id


@component.adapter(IMemberInvitation, IObjectAddedEvent)
def memberInvitationHandler(invitation, ev):
    try:
        principal = getUtility(
            IAuthentication).getPrincipal(invitation.principal)
    except PrincipalLookupError:
        return

    profile = IPersonalProfile(principal, None)
    if profile is None:
        return

    email = profile.email
    if not email:
        return

    template = getMultiAdapter(
        (invitation, getRequest()), IMailTemplate, 'text')
    template.addAlternative(
        getMultiAdapter(
            (invitation, getRequest()), IMailTemplate, 'html'))
    template.send((email,))
