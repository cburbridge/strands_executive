'''
strands_domain.py
--------------------

Provides a domain definition with all the STRANDS actions in it.
'''
from rospkg import rospack

import domain
import state

########################################################################
class STRANDSDomain(object):
    """
    
    """
    _instance = None
    __rospack = rospack.RosPack()
    #----------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        """Force to be singleton"""
        if cls._instance is not None:
            return cls._instance
        cls._instance = object.__new__(cls, *args, **kwargs)
        cls._instance.__find_actions(**kwargs)
        return cls._instance
    
    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        pass

    #----------------------------------------------------------------------
    def __find_actions(self, **kwargs):
        """Scans the ros packages for exported strands actions. Stores
        them here in a domain."""
        packages=[]
        for pkg in STRANDSDomain.__rospack.list():
            manifest = STRANDSDomain.__rospack.get_manifest(pkg)
            for export in manifest.exports:
                if export.tag == "strands_action_domain":
                    if export.attrs.has_key('action'):
                        pth = STRANDSDomain.__rospack.get_path(pkg)
                        packages.append([pkg, export.attrs['action'].replace("${prefix}",pth)])
                    else:
                        rospy.logerr("Package '%s' has <strands_action_domain>"
                                     " tag in export but it misses 'action' "
                                     "attribute." % pkg)
                        
        self.domain = domain.DomainDefinition("STRANDS")
        for pkg, action_yaml in packages:
            with open(action_yaml, "r") as f:
                action = domain.Action.load_yaml(f.read())
                self.domain.addExistingAction(action)
