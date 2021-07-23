from .straightlink import StraightLink
from .elbowlink import ElbowLink
from .curvedlink import CurvedLink
from .selflooplink import SelfloopLink

class LinkClassFactory(object):
    @staticmethod
    def create(link_type):
        if link_type.upper() == 'STRAIGHT_LINK':
            return StraightLink
        elif link_type.upper() == "ELBOW_LINK":
            return ElbowLink
        elif link_type.upper() == 'CURVED_LINK':
            return CurvedLink
        elif link_type.upper() == 'SELFLOOP_LINK':
            return SelfloopLink
        else:
            raise TypeError("Undefined lins type: %s" % (link_type))
