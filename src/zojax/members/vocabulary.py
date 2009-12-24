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
from zope import interface
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.security import checkPermission
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.security.interfaces import IAuthenticatedGroup, IEveryoneGroup

from zojax.catalog.utils import getRequest
from zojax.catalog.interfaces import ICatalog

_ = MessageFactory('zojax.members')

val1 = SimpleTerm('member', 'member', _('Members'))
val1.description = _(
    'Any Member can Invite a Site Member to Join the Group.')

val2 = SimpleTerm('manager', 'manager', _('Managers'))
val2.description = _(
    'Only Managers can Invite a Site Member to Join the Group.')

invitesVocabulary = SimpleVocabulary((val1, val2))


class MembersVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context, **kw):
        if not interfaces.IGroup.providedBy(context):
            return SimpleVocabulary(())

        members = []
        for principal in getPrincipals(context.principals):
            if IAuthenticatedGroup.providedBy(principal) or \
               IEveryoneGroup.providedBy(principal):
                continue

            members.append(
                (principal.title,
                 SimpleTerm(principal.id, principal.id, principal.title)))

        members.sort()
        return SimpleVocabulary([term for title, term in members])
