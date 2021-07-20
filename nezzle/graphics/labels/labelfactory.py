from .textlabel import TextLabel

class LabelClassFactory(object):

    @staticmethod
    def create(label_type):
        if label_type.upper() == 'TEXT_LABEL':
            return TextLabel
        else:
            raise TypeError("Undefined labels type: %s" % (label_type))
