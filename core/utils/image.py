from __future__ import unicode_literals, absolute_import, print_function, division

from PIL import Image


class NoCellAvailable(Exception):
    pass


class ImageRejected(Exception):
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

    def get_resized_dimension(self, primary_dimension, secondary_dimension, new_size):
        secondary_dimension *= new_size / primary_dimension
        return new_size, int(round(secondary_dimension))

    def center_image(self, image, delta_width, delta_height, horizontal, vertical):
        assert isinstance(image, Image.Image), "Center image can only be done with a PIL image"
        assert delta_width >= 0, "Can't center an image if its delta_width is {}".format(delta_width)
        assert delta_height >= 0, "Can't center an image if its delta_height is {}".format(delta_height)

        if delta_width % 2:
            delta_width -= 1
        if delta_height % 2:
            delta_height -= 1
        offset_width = int(delta_width / 2)
        offset_height = int(delta_height / 2)

        box = (
            offset_width,
            offset_height,
            offset_width + self.cell_width * horizontal,
            offset_height + self.cell_height * vertical,
        )
        image.crop(box)
        return image, horizontal, vertical

    def validate_image_size(self, image, horizontal=1, vertical=1):
        # Validate grid (TODO: move)
        if horizontal > self.columns:
            raise NoCellAvailable("Image spans more columns than available")
        if vertical > self.rows:
            raise NoCellAvailable("Image spans more rows than available")

        # Calculate image properties
        image_width, image_height = image.size
        delta_width = image_width - self.cell_width * horizontal
        delta_height = image_height - self.cell_height * vertical
        is_landscape = image_width >= image_height

        # See if image spans multiple cells or not
        if delta_width >= self.cell_width * horizontal - self.scale_margin and is_landscape:
            return self.validate_image_size(image, horizontal+1, 1)
        elif delta_height >= self.cell_height * vertical - self.scale_margin and not is_landscape:
            return self.validate_image_size(image, 1, vertical+1)

        # Center image if it overflows the cell(s)
        if delta_width >= 0 and delta_height >= 0:
            return self.center_image(image, delta_width, delta_height, horizontal, vertical)

        # Image is smaller than cell in at least one dimension.
        # Correct the delta's to make them easier to work with
        delta_width *= -1
        delta_height *= -1

        # Reject image if it is smaller than the cell and can't be scaled up within allowed limits
        if delta_width > self.scale_margin or delta_height > self.scale_margin:
            print(image_width, image_height)
            raise ImageRejected("Image with delta {}/{} is too small for set scale margin {}".format(
                delta_width,
                delta_height,
                self.scale_margin
            ))

        if delta_width > 0:
            new_width, new_height = self.get_resized_dimension(image_width, image_height, self.cell_width * horizontal)
            image.resize((new_width, new_height,))
            return self.validate_image_size(image, horizontal, vertical)
        elif delta_height > 0:
            new_height, new_width = self.get_resized_dimension(image_height, image_width, self.cell_height * vertical)
            image.resize((new_width, new_height,))
            return self.validate_image_size(image, horizontal, vertical)

        raise AssertionError("validate_image_size didn't process its image at all")

    def cell_image(self, image):
        assert isinstance(image, Image.Image), "Cell image expects a PIL image not {}".format(type(image))

    def fill(self, images):
        for image in images:
            try:
                self.images.append(self.cell_image(image))
            except NoCellAvailable:
                pass