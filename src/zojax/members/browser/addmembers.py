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
from zope.component import getUtility, queryUtility
from zope.traversing.browser import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile

from zojax.layoutform import Fields
from zojax.batching.batch import Batch
from zojax.wizard.step import WizardStep, WizardStepForm
from zojax.catalog.interfaces import ICatalog
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.personal.space.interfaces import IPersonalSpace, IPersonalSpaceManager
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.members.interfaces import _, IMembers


class AddMembersForm(WizardStep):

    title = _(u'Add members')
    template = ViewPageTemplateFile('addmembers.pt')

    def update(self):
        super(AddMembersForm, self).update()

        context = self.context
        request = self.request

        if 'formusers.select' in request:
            uids = request.get('principal.users')
            if not uids:
                IStatusMessage(request).add(u'Please select users.', 'warning')
            else:
                for uid in uids:
                    context.joinPrincipal(uid)

                IStatusMessage(request).add(u'Users have been added to group.')

        self.manager = queryUtility(IPersonalSpaceManager)
        if self.manager is None:
            return

        self.managerURL = absoluteURL(self.manager, self.request)

        results = getUtility(ICatalog).searchResults(
            type = {'any_of': ('personal.space',)},
            searchContext = (self.manager,), sort_on='title')

        self.batch = Batch(results, size=30, context=context, request=request)

    def getMemberInfo(self, space):
        principal = space.principal
        if principal is None:
            return

        profile = IPersonalProfile(principal)
        avatar = profile.avatarUrl(self.request)

        info = {
            'id': principal.id,
            'spaceid': space.__name__,
            'title': profile.title,
            'avatar': avatar,
            'member': self.context.isMember(principal.id)}
        return info


class MembersConfig(WizardStepForm):

    label = title = _(u'Configure')

    fields = Fields(IMembers)


class MembersAwareConfig(WizardStepForm):

    label = title = _(u'Membership')

    fields = Fields(IMembers)

    def getContent(self):
        return self.wizard.getContent().members
