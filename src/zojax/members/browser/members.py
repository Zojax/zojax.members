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
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.content.actions.action import Action
from zojax.batching.batch import Batch
from zojax.filefield.interfaces import IImage
from zojax.ownership.interfaces import IOwnership
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.members.browser import interfaces
from zojax.members.interfaces import _, IMembers, IMembersAware


class Members(object):

    def update(self):
        self.auth = getUtility(IAuthentication)

        self.batch = Batch(
            list(self.context.keys()), size=15,
            context=self.context, request=self.request)
        super(Members, self).update()

    def getMemberInfo(self, id):
        member = self.context[id]

        try:
            principal = self.auth.getPrincipal(member.__name__)
        except PrincipalLookupError:
            principal = None

        try:
            profile = IPersonalProfile(principal)
        except:
            return

        image = profile.profileImage
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
            'id': id,
            'title': getattr(profile, 'title', _(u'Unknown')),
            'description': getattr(principal, 'description', u''),
            'manager': u'',
            'personalspace': u'',
            'joined': member.joined,
            'imagex': image[0],
            'imagey': image[1],
            'default': default,
            'photo': profile.photoUrl(self.request)}

        space = profile.space
        if space is not None:
            info['manager'] = space.title
            info['personalspace'] = absoluteURL(space, self.request)

        return info


class ManageMembers(Action):
    component.adapts(IMembers, interface.Interface)
    interface.implements(interfaces.IManageMembersAction)

    weight = 10
    title = _(u'Manage members')
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/context.html'%(absoluteURL(self.context, self.request))


class ManageMembersGroup(Action):
    component.adapts(IMembersAware, interface.Interface)
    interface.implements(interfaces.IManageMembersAction)

    weight = 60
    title = _(u'Manage members')
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/members/context.html'%(absoluteURL(self.context, self.request))
