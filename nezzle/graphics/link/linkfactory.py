# -*- coding: utf-8 -*-

from .straightlink import StraightLink
from .curvedlink import CurvedLink
from .selflooplink import SelfloopLink


class LinkClassFactory(object):
    @staticmethod
    def create(link_type):
        if link_type.upper() == 'STRAIGHT_LINK':
            return StraightLink
        elif link_type.upper() == 'CURVED_LINK':
            return CurvedLink
        elif link_type.upper() == 'SELFLOOP_LINK':
            return SelfloopLink
        else:
            raise TypeError("Undefined link type: %s" % (link_type))
