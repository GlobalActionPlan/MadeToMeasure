from BTrees.OOBTree import OOBTree
from pyramid.location import lineage
from pyramid.traversal import find_root
from zope.interface import implements
import colander
import deform

from madetomeasure.interfaces import ISecurityAware
from madetomeasure import security
from madetomeasure import MadeToMeasureTSF as _


ROLES_NAMESPACE = 'role:'
GROUPS_NAMESPACE = 'group:'
NAMESPACES = (ROLES_NAMESPACE, GROUPS_NAMESPACE, )


class SecurityAware(object):
    """ Mixin for all content that should handle groups.
        Principal in this terminology is a userid or a group id.
    """
    implements(ISecurityAware)

    @property
    def _groups(self):
        try:
            return self.__groups__
        except AttributeError:
            self.__groups__ = OOBTree()
            return self.__groups__
    
    def get_groups(self, principal):
        """ Return groups for a principal in this context.
            The special group "role:Owner" is never inherited.
        """
        groups = set()
        for location in lineage(self):
            location_groups = location._groups
            try:
                if self is location:
                    groups.update(location_groups[principal])
                else:
                    groups.update([x for x in location_groups[principal]])
            except KeyError:
                continue

        return tuple(groups)

    def add_groups(self, principal, groups):
        """ Add a groups for a principal in this context.
        """
        self._check_groups(groups)
        groups = set(groups)
        groups.update(self.get_groups(principal))
        self._groups[principal] = tuple(groups)
    
    def set_groups(self, principal, groups):
        """ Set groups for a principal in this context. (This clears any previous setting)
        """
        self._check_groups(groups)
        self._groups[principal] = tuple(groups)

    def update_userids_permissions(self, value):
        """ Set permissions from a list of dicts with the following layout:
            {'userid':<userid>,'groups':<set of groups that the user should have>}.
        """
        #Unset all permissions from users that exist but aren't provided
        submitted_userids = [x['userid'] for x in value]
        for userid in self._groups:
            if userid not in submitted_userids:
                del self._groups[userid]
        
        #Set the new permissions
        for item in value:
            self.set_groups(item['userid'], item['groups'])

    def get_security(self):
        """ Return the current security settings.
        """
        userids_and_groups = []
        for userid in self._groups:
            userids_and_groups.append({'userid':userid, 'groups':self.get_groups(userid)})
        return userids_and_groups

    def _check_groups(self, groups):
        for group in groups:
            if not group.startswith(NAMESPACES):
                raise ValueError('Groups need to start with either "group:" or "role:"')

    def list_all_groups(self):
        """ Returns a set of all groups in this context. """
        groups = set()
        [groups.update(x) for x in self._groups.values()]
        return groups
