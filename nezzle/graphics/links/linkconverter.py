from typing import ClassVar

from nezzle.graphics.links.baselink import BaseLink
from nezzle.graphics.links.baselink import TwoNodeLink
from nezzle.graphics.links.straightlink import StraightLink
from nezzle.graphics.links.curvedlink import CurvedLink
from nezzle.graphics.links.elbowlink import VerticalElbowLink, HorizontalElbowLink


class LinkConverter(object):

    @staticmethod
    def to_link(link: TwoNodeLink, link_type: ClassVar):

        if type(link) == link_type:
            return

        attr = link.to_dict()
        new_link = link_type.from_dict(attr=attr, source=link.source, target=link.target)
        #new_link.initialize()
        return new_link
        # if link_type.upper() == 'STRAIGHT_LINK':
        #     return LinkConverter._to_straight_link(new_link)
        # elif link_type.upper() == 'CURVED_LINK':
        #     return LinkConverter._to_curved_link(new_link)
        # elif link_type.upper() == "VERTICAL_ELBOW_LINK":
        #     return LinkConverter._to_vertical_elbow_link(new_link)
        # elif link_type.upper() == "HORIZONTAL_ELBOW_LINK":
        #     return LinkConverter._to_horizontal_elbow_link(new_link)
        # else:
        #     raise TypeError("Illegal link type: %s" % (link_type))


    # @staticmethod
    # def _to_straight_link(link):
    #     pass
    #
    # @staticmethod
    # def _to_curved_link(link):
    #     pass
    #
    # @staticmethod
    # def _to_vertical_elbow_link(link):
    #     pass
    #
    # @staticmethod
    # def _to_horizontal_elbow_link(link):
    #     pass