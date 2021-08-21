from nezzle.graphics.headers.baseheader import Arrow
from nezzle.graphics.headers.baseheader import Hammer


class HeaderClassFactory(object):
    @staticmethod
    def create(header_type):
        if header_type.upper() == 'ARROW':
            return Arrow
        elif header_type.upper() == 'HAMMER':
            return Hammer
        else:
            raise TypeError("Undefined link type: %s" % (header_type))

    @staticmethod
    def get_available_headers():
        return ["Arrow", "Hammer"]