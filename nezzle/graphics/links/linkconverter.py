from typing import ClassVar

from nezzle.graphics.links.baselink import BaseLink
from nezzle.graphics.links.baselink import TwoNodeLink
from nezzle.graphics.links.straightlink import StraightLink
from nezzle.graphics.links.curvedlink import CurvedLink
from nezzle.graphics.links.elbowlink import VerticalElbowLink, HorizontalElbowLink


class LinkConverter(object):

    @staticmethod
    def to_link(link: BaseLink, link_type: ClassVar):

        if type(link) == link_type:
            return

        attr = link.to_dict()
        new_link = link_type.from_dict(attr=attr, source=link.source, target=link.target)
        return new_link
