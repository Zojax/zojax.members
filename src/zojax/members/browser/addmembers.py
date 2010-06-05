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
from zojax.layoutform.interfaces import ISaveAction
"""

$Id$
"""
from zope import interface, schema
from zope.component import getUtility, queryUtility
from zope.traversing.browser import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile

from zojax.layoutform import Fields, button
from zojax.batching.batch import Batch
from zojax.wizard.step import WizardStep, WizardStepForm
from zojax.catalog.interfaces import ICatalog
from zojax.principal.field.field import PrincipalField, UserField
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.personal.space.interfaces import IPersonalSpace, IPersonalSpaceManager
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.members.interfaces import _, IMembers


class IAddMembers(interface.Interface):

    principals = schema.List(title=_('Select Users'),
                             value_type=UserField(),
                             required=False)


class AddMembersForm(WizardStepForm):

    title = _(u'Add members')
    #template = ViewPageTemplateFile('addmembers.pt')
    fields = Fields(IAddMembers)
    ignoreContext = True

    @button.buttonAndHandler(_(u'Add Members'), name="add", provides=ISaveAction)
    def selectButtonHandler(self, action):
        data, errors = self.extractData()
        context = self.context
        request = self.request
        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'error')
            return
        uids = data['principals']
        if not uids:
            IStatusMessage(self.request).add(
                _('Please select user(s).'), 'warning')
        else:
            for uid in data['principals']:
                context.joinPrincipal(uid)
            IStatusMessage(request).add(u'Users have been added to group.')
            self.redirect('.')


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
