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
import time, rfc822
from zope import interface, component
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.content.feeds.rss2 import RSS2Feed
from zojax.catalog.interfaces import ICatalog
from zojax.ownership.interfaces import IOwnership
from zojax.content.space.interfaces import ISpace
from zojax.content.space.utils import getSpace
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.filefield.interfaces import IImage
from zojax.ownership.interfaces import IOwnership
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.principal.profile.interfaces import IPersonalProfile


from interfaces import _, IMembersRSSFeed, IMembersAware


class MembersRSSFeed(RSS2Feed):
    component.adapts(IMembersAware)
    interface.implementsOnly(IMembersRSSFeed)

    name = u'members'
    title = _(u'Recent members')
    description = _(u'List of recently joined members.')

    def items(self):
        request = self.request
        results = self.context['members'].values()
        auth = getUtility(IAuthentication)
        for member in results:
            try:
                principal = auth.getPrincipal(member.__name__)
            except PrincipalLookupError:
                principal = None

            space = IPersonalSpace(principal, None)
            profile = IPersonalProfile(principal, None)

            image = getattr(profile, 'profileImage', None)
            if image and IImage.providedBy(image):
                w, h = image.width, image.height
                if w > 128:
                    xscale = 128.0/w
                else:
                    xscale = 1.0
                if h > 128:
                    yscale = 120.0/h
                else:
                    yscale = 1.0
                scale = xscale < yscale and xscale or yscale
                image = (int(round(w*scale)), int(round(h*scale)))
                default = False
            else:
                image = (128, 97)
                default = True

            info = {
                'id': member.__name__,
                'title': getattr(profile, 'title', _(u'Unknown')),
                'description': getattr(principal, 'description', u''),
                'manager': u'',
                'personalspace': u'',
                'joined': member.joined,
                'imagex': image[0],
                'imagey': image[1],
                'default': default}

            if space is not None:
                info['manager'] = space.title
                info['personalspace'] = absoluteURL(space, self.request)

            info = {
                'title': info['title'],
                'description': info['description'],
                'guid': info['personalspace'] or info['id'],
                'pubDate': rfc822.formatdate(time.mktime(
                        info['joined'].timetuple())),
                'isPermaLink': True}

            if profile is not None:
                info['author'] = u'%s (%s)'%(profile.email, profile.title)

            yield info
