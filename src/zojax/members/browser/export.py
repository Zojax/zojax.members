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
import csv, StringIO

from zope.component import getUtility
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.layoutform import button, Fields
from zojax.wizard.step import WizardStepForm
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage

from interfaces import _, IExportForm, IMemberExported


class ExportForm(WizardStepForm):

    title = _(u'Export')
    label = _(u'Export Members Data')
    fields = Fields(IExportForm)

    result = None
    exportFields = Fields(IMemberExported).select(
        'title', 'firstname', 'lastname',
        'email', 'timezone', 'registered', 'lastLoginTime')

    def getContent(self):
        return {}

    def update(self):
        super(ExportForm, self).update()

        self.auth = getUtility(IAuthentication)

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
            'member': self.context.isMember(principal.id)}
        return info

    @button.buttonAndHandler(_(u'Export CSV'))
    def handleCSV(self, action):
        request = self.request
        data, errors = self.extractData()

        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'error')
        else:
            getPrincipal = self.auth.getPrincipal
            members = []
            for pid in self.context.keys():
                try:
                    principal = getPrincipal(pid)
                except PrincipalLookupError:
                    continue

                profile = IPersonalProfile(principal, None)
                if profile is None:
                    continue

                members.append(profile)

            self.result = self.export(members)

    def export(self, data):
        res = StringIO.StringIO()
        fields = self.exportFields.items()
        names = [value.field.title for key, value in fields]
        writer = csv.writer(res)
        writer.writerow(names)
        for value in data:
            writer.writerow([unicode(getattr(value, fname, '') or '')
                             for fname, field in fields])
        res.seek(0)
        return res.read()

    def __call__(self):
        if self.result:
            self.request.response.setHeader('Content-Type', 'text/csv')
            self.request.response.setHeader('Content-Disposition',
                                            'attachment; filename=members.csv')
            return self.result

        return super(ExportForm, self).__call__()
