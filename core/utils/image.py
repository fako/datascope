from __future__ import unicode_literals, absolute_import, print_function, division

from PIL import Image


class NoCellAvailable(Exception):
    pass


class ImageGrid(object):

    def __init__(self, columns, rows, cell_width, cell_height, scale_margin):
        self.columns = columns
        self.rows = rows
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.images = []
        self.cells = list(
            [None for cell in xrange(0, rows) for row in xrange(0, columns)]
        )
        self.index = 0
        self.scale_margin = scale_margin

    def fill_from_src(self, sources):
        pass

    def validate_image_size(self, image, horizontal=1, vertical=1):
        if horizontal > self.columns:
            raise NoCellAvailable("Image spans more columns than available")
        if vertical > self.rows:
            raise NoCellAvailable("Image spans more rows than available")

        image_width, image_height = image.size
        delta_width = image_width - self.cell_width * horizontal + self.scale_margin
        delta_height = image_height - self.cell_height * vertical + self.scale_margin
        is_landscape = image_width >= image_height

        if delta_width >= 0 and delta_height >= 0:
            if delta_width % 2:
                delta_width -= 1
            if delta_height % 2:
                delta_height -= 1
            offset_width = int(delta_width / 2)
            offset_height = int(delta_height / 2)
            return offset_width, offset_height, offset_width + self.cell_width, offset_height + self.cell_height


    def cell_image(self, image):
        assert isinstance(image, Image.Image), "Cell image expects a PIL image not {}".format(type(image))


    def fill(self, images):
        for image in images:
            try:
                self.images.append(self.cell_image(image))
            except NoCellAvailable:
                pass