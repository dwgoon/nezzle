from nezzle.graphics.links.straightlink import StraightLink
from nezzle.graphics.links.curvedlink import CurvedLink
from nezzle.graphics.links.elbowlink import VerticalElbowLink
from nezzle.graphics.links.elbowlink import HorizontalElbowLink
from nezzle.graphics.links.selflooplink import SelfloopLink


class LinkClassFactory(object):

    @staticmethod
    def create(link_type):
        if link_type.upper() == 'STRAIGHT_LINK':
            return StraightLink
        elif link_type.upper() == "VERTICAL_ELBOW_LINK":
            return VerticalElbowLink
        elif link_type.upper() == "HORIZONTAL_ELBOW_LINK":
            return HorizontalElbowLink
        elif link_type.upper() == 'CURVED_LINK':
            return CurvedLink
        elif link_type.upper() == 'SELFLOOP_LINK':
            return SelfloopLink
        else:
            raise TypeError("Undefined link type: %s" % (link_type))
