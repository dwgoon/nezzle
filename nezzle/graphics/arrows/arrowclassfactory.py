from nezzle.graphics.arrows.basearrow import Triangle
from nezzle.graphics.arrows.basearrow import Hammer


class ArrowClassFactory(object):
    @staticmethod
    def create(arrow_type):
        if arrow_type.upper() == "TRIANGLE":
            return Triangle
        elif arrow_type.upper() == "HAMMER":
            return Hammer
        else:
            raise TypeError("Undefined edge type: %s" % (arrow_type))

    @staticmethod
    def get_available_heads():
        return ["Triangle", "Hammer"]