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
""" Members interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

from zojax.richtext.field import RichText
from zojax.filefield.field import ImageField
from zojax.widget.radio.field import RadioChoice
from zojax.widget.checkbox.field import CheckboxList
from zojax.content.type.interfaces import IItem
from zojax.content.space.interfaces import ISpace, IWorkspace, IWorkspaceFactory
from zojax.content.activity.interfaces import IContentActivityRecord
from zojax.principal.invite.interfaces import IObjectInvitation
from zojax.content.feeds.interfaces import IRSS2Feed
from zojax.members import vocabulary

_ = MessageFactory('zojax.members')


class IMembersAware(interface.Interface):
    """ marker interface """

    members = interface.Attribute('IMembers object')


class IMember(interface.Interface):
    """ member """

    title = interface.Attribute('Principal title')

    description = interface.Attribute('Principal description')

    principal = interface.Attribute('IPrincipal object')

    joined = interface.Attribute('Joined date')

    space = interface.Attribute('Personal space')

    profile = interface.Attribute('Personal profile')

    approved = interface.Attribute('Approved status')


class IMembers(interface.Interface):
    """ members container """

    joined = interface.Attribute('Joined dates')
    managers = interface.Attribute('List of group managers')
    principals = interface.Attribute('List of members principal ids')
    notapproved = interface.Attribute('List of not approved members')

    joining = CheckboxList(
        title = _(u'Join Group Permissions'),
        description = _(u'Site Members can Join Groups.'),
        vocabulary = "zojax.roles",
        required = False)

    approving = schema.Bool(
        title = _(u'Join Approvals'),
        description = _(u'Members Wanting to Join a Group Must be Approved.'),
        default = True,
        required = True)

    invites = CheckboxList(
        title = _(u'Group Invitations Permissions'),
        description = _(u'Specify who can invite site members to join a Group.'),
        vocabulary = vocabulary.invitesVocabulary,
        required = True)

    def join():
        """ join current principal to group """

    def joinPrincipal(principalId, approved=True):
        """ join principal to group """

    def isMember(principalId):
        """ check if principal member of group """


class IMemberApprovedEvent(interface.Interface):
    """ member approved """

    member = interface.Attribute("IGroupMember object")


class MemberApprovedEvent(object):
    interface.implements(IMemberApprovedEvent)

    def __init__(self, member):
        self.member = member


class IMemberRoleManagement(interface.Interface):
    """ group management """

    def toMember(id):
        """ set role to member """

    def toManager(id):
        """ set role to manager """

    def approve(id):
        """ approve member """

    def removeInvitation(id):
        """ remove invitation """


class IMemberInvitation(IObjectInvitation):
    """ member invitation """

    message = interface.Attribute('Message')


class IMemberJoinedActivityRecord(IContentActivityRecord):
    """ activity record """

    principal = schema.TextLine(
        title = u'Principal id',
        required = True)


# members rss feed

class IMembersRSSFeed(IRSS2Feed):
    pass
