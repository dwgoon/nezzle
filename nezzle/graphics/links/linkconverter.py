from typing import AnyStr
from typing import Union
from typing import Type

from nezzle.graphics.links.baselink import BaseLink
from nezzle.graphics.links.baselink import TwoNodeLink
from nezzle.graphics.links.straightlink import StraightLink
from nezzle.graphics.links.curvedlink import CurvedLink
from nezzle.graphics.links.elbowlink import VerticalElbowLink, HorizontalElbowLink
from nezzle.graphics.links.linkfactory import LinkClassFactory


class LinkConverter(object):

    @staticmethod
    def convert(link: BaseLink, link_type: Union[Type, AnyStr]):

        if isinstance(link_type, str):
            link_type = LinkClassFactory.create(link_type)

        if type(link) == link_type:
            return

        attr = link.to_dict()
        attr["ITEM_TYPE"] = link_type.ITEM_TYPE
        new_link = link_type.from_dict(attr=attr, source=link.source, target=link.target)
        return new_link
