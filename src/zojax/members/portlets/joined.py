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
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL
from zojax.formatter.utils import getFormatter


class RecentlyJoinedMembersPortlet(object):

    def getMembers(self):
        request = self.request
        context = self.context

        members = context.members
        formatter = getFormatter(request, 'humanDatetime', 'medium')

        idx = 0
        joined = removeAllProxies(members.joined)
        keys = joined.keys()
        for nidx in range(len(keys)-1, -1, -1):
            jdate = keys[nidx]
            pid = joined[jdate]
            member = members[pid]

            profile = member.profile
            if profile is not None:
                info = {'avatar': profile.avatarUrl(request),
                        'author': profile.title,
                        'joined': formatter.format(jdate),
                        'space': None}

                space = member.space
                if space is not None:
                    info['space'] = '%s/'%absoluteURL(space, request)

                yield info

            idx += 1
            if idx > self.number:
                break
