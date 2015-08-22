from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import range

from PIL import Image


class ImageRejected(Exception):
    pass


class ImageDoesNotFit(Exception):
    pass


class CouldNotFillGrid(Exception):
    pass


class ImageGrid(object):

    def __init__(self, columns, rows, cell_width, cell_height):
        assert cell_width > cell_height, \
            "Image grid expect cells to be landscape oriented"
        self.columns = columns
        self.rows = rows
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.images = []
        self.cells = list(
            [None for cell in range(0, rows) for row in range(0, columns)]
        )
        self.index = 0
        self.stop = len(self.cells) - 1

    def set_stop(self):
        self.stop = self.index - 1

    def next_carousel_image(self):
        try:
            image = self.images[self.index]
        except IndexError:
            self.index = 0
            image = self.images[self.index]
        self.index += 1
        return image

    def get_image_info(self, image):
        image_width, image_height = image.size
        image_ratio = image_height / image_width
        panorama_ratio = self.cell_height / (self.cell_width*2)
        portrait_ratio = self.cell_height*2 / self.cell_width
        return (
            panorama_ratio < image_ratio < portrait_ratio,  # is_landscape
            image_ratio <= panorama_ratio,  # is_panorama
            image_ratio >= portrait_ratio,  # is_portrait
        )

    def validate_image_size(self, image, horizontal=1, vertical=1):
        image_width, image_height = image.size
        if image_width < self.cell_width * horizontal or image_height * vertical < self.cell_height:
            raise ImageRejected("Image with size {}:{} is too small for cell size {}:{}".format(
                image_width,
                image_height,
                self.cell_width,
                self.cell_height
            ))
        return image_width == self.cell_width * horizontal and image_height == self.cell_height * vertical

    def center_image(self, image, horizontal, vertical):
        assert isinstance(image, Image.Image), "Center image can only be done with a PIL image"
        image_width, image_height = image.size
        delta_width = image_width - self.cell_width * horizontal
        delta_height = image_height - self.cell_height * vertical
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
        return image

    @staticmethod
    def get_new_size(primary_dimension, secondary_dimension, new_size):
        secondary_dimension *= new_size / primary_dimension
        return new_size, int(round(secondary_dimension))

    def size_image(self, image):
        assert isinstance(image, Image.Image), "Cell image expects a PIL image not {}".format(type(image))
        exact_fit = self.validate_image_size(image)
        if exact_fit:
            return image, 1, 1

        is_landscape, is_panorama, is_portrait = self.get_image_info(image)
        image_width, image_height = image.size

        if is_landscape:
            horizontal, vertical = 1, 1
            new_height, new_width = self.get_new_size(image_height, image_width, self.cell_height)
        elif is_panorama:
            horizontal, vertical = 2, 1
            new_height, new_width = self.get_new_size(image_height, image_width, self.cell_height)
        elif is_portrait:
            horizontal, vertical = 1, 2
            new_width, new_height = self.get_new_size(image_width, image_height, self.cell_width)
        else:
            raise AssertionError("Image wasn't labeled as any category")

        if new_width >= self.cell_width and new_height >= self.cell_height:
            image.resize((new_width, new_height,))
        self.center_image(image, horizontal, vertical)

        return image, horizontal, vertical

    def cell_image(self, cell_index, image_info):
        image, horizontal, vertical = image_info
        self.cells[cell_index] = image

        # Reserve cells for landscape and panorama
        if horizontal > 1:
            for cell_index_modifier in range(0, horizontal):
                index = cell_index + cell_index_modifier
                self.cells[index] = image

        # Reserve cells for portrait
        if vertical > 1:
            for cell_index_modifier in range(0, vertical*self.columns, self.columns):
                index = cell_index + cell_index_modifier
                self.cells[index] = image

    def fill(self, images):
        for image in images:
            try:
                self.images.append(self.size_image(image))
            except ImageRejected:
                pass

        for index, cell in enumerate(self.cells):
            if cell is not None:
                continue

            for attempt in range(0, len(self.images)):
                try:
                    self.cell_image(index, self.next_carousel_image())
                    break
                except IndexError:
                    pass
            else:
                raise CouldNotFillGrid("Unable to fill the grid with provided images")

    def fill_from_src(self, sources):
        pass
