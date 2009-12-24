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
from zope import interface, schema

from zojax.table.interfaces import ITable
from zojax.widget.checkbox.field import CheckboxList
from zojax.content.actions.interfaces import IAction, IManageContentCategory
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.members.interfaces import _


class IJoinGroupAction(IAction):
    """ join group action """


class IInviteMembersAction(IAction):
    """ invite to group action """


class IInvitationsAction(IAction):
    """ invitations """


class IManageMembersAction(IAction, IManageContentCategory):
    """ manage members action """


class IManageMembersTable(ITable):
    """ manage members table """


class IInvitationsTable(ITable):
    """ invitations table """


class IInviteMembersForm(interface.Interface):
    """ invite form """

    message = schema.Text(
        title = _('Message'),
        required = True)


class ISendMessageForm(interface.Interface):
    """ invite form """

    message = schema.Text(
        title = _('Message'),
        required = True)


class IExportForm(interface.Interface):
    """ export form """


class IMemberExported(IPersonalProfile):
    """ member exported """

    title = schema.TextLine(title=_(u'Principal full name'))
    firstname = schema.TextLine(title=_(u'Principal first name'))
    lastname = schema.TextLine(title=_(u'Principal last name'))
    email = schema.TextLine(title=_(u'Principal email'))
