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
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.layoutform import button, Fields, interfaces
from zojax.batching.batch import Batch
from zojax.wizard.step import WizardStepForm
from zojax.formatter.utils import getFormatter
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.personal.space.interfaces import IPersonalSpaceManager
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.mailtemplate.interfaces import IMailTemplate, IMailHeaders

from interfaces import _, ISendMessageForm


class SendMessageForm(WizardStepForm):

    title = _(u'Send message')
    fields = Fields(ISendMessageForm)
    managerURL = u''

    def getContent(self):
        return {'message': u'Hello,\n\nWish you good luck.\n\nRegards,\n%s'%(
                IPersonalProfile(self.request.principal).title)}

    def update(self):
        super(SendMessageForm, self).update()

        context = self.context
        request = self.request

        self.manager = queryUtility(IPersonalSpaceManager)
        if self.manager is not None:
            self.managerURL = absoluteURL(self.manager, self.request)

        results = list(self.context.keys())
        self.batch = Batch(results, size=30, context=context, request=request)
        self.auth = getUtility(IAuthentication)
        self.formatter = getFormatter(request, 'fancyDatetime', 'medium')

    def getMemberInfo(self, id):
        member = self.context[id]

        try:
            principal = self.auth.getPrincipal(member.__name__)
        except PrincipalLookupError:
            return

        profile = IPersonalProfile(principal, None)
        if profile is None:
            return

        space = profile.space
        if space is None:
            return

        info = {
            'id': principal.id,
            'spaceid': space.__name__,
            'title': profile.title,
            'avatar': profile.avatarUrl(self.request),
            'joined': self.formatter.format(member.joined),
            'approved': member.approved and \
                _('Approved') or _('Not yet approved'),
            }

        return info

    @button.buttonAndHandler(_(u'Send'), provides=interfaces.IAddButton)
    def handleSend(self, action):
        request = self.request
        data, errors = self.extractData()

        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'error')
        else:
            self.message = data['message']
            members = self.context
            getPrincipal = self.auth.getPrincipal
            uids = request.get('principal.users', ())

            if not uids:
                IStatusMessage(request).add(
                    _(u'Please select users.'), 'warning')
                return

            template = getMultiAdapter((self, request), IMailTemplate, 'text')
            template.addAlternative(getMultiAdapter(
                    (self, request), IMailTemplate, 'html'))

            for pid in uids:
                try:
                    principal = getPrincipal(pid)
                except PrincipalLookupError:
                    continue

                profile = IPersonalProfile(principal, None)
                if profile is None:
                    continue

                email = profile.email
                if not email:
                    continue

                template.send((email,))

            IStatusMessage(request).add(_(u'Message to members has been sent.'))
            self.redirect('.')
