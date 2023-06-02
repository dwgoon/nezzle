from qtpy.QtCore import Qt
from qtpy.QtGui import QImage
from qtpy.QtGui import QPainter

from nezzle.utils import extract_name_and_ext


def write_image(net,
                fpath,
                image_width=None, image_height=None,
                transparent=True,
                quality=100,
                scale_width=200, scale_height=200,
                dpi_width=350, dpi_height=350,
                pad_width=10, pad_height=10):

    fname, fext = extract_name_and_ext(fpath)

    scene = net.scene
    scene.clearSelection()
    scene.clearFocus()
    brect = scene.itemsBoundingRect()
    brect.adjust(-pad_width, -pad_height, +2*pad_width, +2*pad_height)

    if image_width and image_height:
        image = QImage(image_width,
                       image_height,
                       QImage.Format_ARGB32_Premultiplied)
    else:
        image = QImage(int((scale_width/100.0) * brect.width()),
                       int((scale_height/100.0) * brect.height()),
                       QImage.Format_ARGB32_Premultiplied)

    # [REF] http://stackoverflow.com/a/13425280/4136588
    # dpm = 300 / 0.0254 # ~300 DPI
    dpm_width = int(dpi_width / 0.0254)
    dpm_height = int(dpi_height / 0.0254)
    image.setDotsPerMeterX(dpm_width)
    image.setDotsPerMeterY(dpm_height)

    bbrush = scene.backgroundBrush()

    painter = QPainter(image)
    if not transparent or fext in ["jpeg", "jpg"]:
        image.fill(Qt.white)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bbrush.color())
        painter.drawRect(0, 0, image.width(), image.height())
    elif fext in ['png']:
        image.fill(bbrush.color())

    painter.setRenderHints(QPainter.TextAntialiasing
                           | QPainter.Antialiasing
                           | QPainter.SmoothPixmapTransform
                           | QPainter.HighQualityAntialiasing)

    scene.render(painter)
    image.save(fpath, fext.upper(), quality)
    painter.end()
# end of def

