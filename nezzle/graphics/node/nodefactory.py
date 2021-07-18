# -*- coding: utf-8 -*-

from .ellipsenode import EllipseNode
from .ellipsenode import CircleNode

class NodeClassFactory(object):
    @staticmethod
    def create(node_type):
        if node_type.upper() == 'ELLIPSE_NODE':
            return EllipseNode
        elif node_type.upper() == 'CIRCLE_NODE':
            return CircleNode
        else:
            raise TypeError("Undefined node type: %s" % (node_type))
