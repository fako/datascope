from __future__ import unicode_literals, absolute_import, print_function, division

from PIL import Image

from unittest import TestCase
from mock import Mock

from core.utils.image import ImageGrid, ImageRejected



class TestImageGrid(TestCase):

    def setUp(self):
        self.image_grid = ImageGrid(4, 3, 16, 9, 3)

        self.fit = Mock(Image.Image, size=(16, 9))
        self.oversize_x = Mock(Image.Image, size=(18, 9))
        self.oversize_y = Mock(Image.Image, size=(16, 11))
        self.oversize_xy = Mock(Image.Image, size=(18, 11))
        self.oversize_xyr = Mock(Image.Image, size=(17, 10))
        self.kingsize_x = Mock(Image.Image, size=(32, 12))
        self.kingsize_y = Mock(Image.Image, size=(16, 20))
        self.too_small_x = Mock(Image.Image, size=(12, 9))
        self.too_small_y = Mock(Image.Image, size=(16, 5))
        self.too_small_xy = Mock(Image.Image, size=(5, 5))

    def test_init(self):
        ig = ImageGrid(4, 3, 16, 9, 0)
        self.assertEqual(len(ig.cells), 12)
        ig = ImageGrid(5, 5, 16, 9, 0)
        self.assertEqual(len(ig.cells), 25)

    def test_validate_image_size(self):
        image, horizontal, vertical = self.image_grid.validate_image_size(self.fit)
        image.crop.assert_called_once_with((0, 0, 16, 9,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.oversize_x)
        image.crop.assert_called_once_with((1, 0, 17, 9,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.oversize_y)
        image.crop.assert_called_once_with((0, 1, 16, 10,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.oversize_xy)
        image.crop.assert_called_once_with((1, 1, 17, 10,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.oversize_xyr)
        image.crop.assert_called_once_with((0, 0, 16, 9,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.kingsize_x)
        image.crop.assert_called_once_with((0, 1, 32, 10,))
        self.assertEqual(horizontal, 2)
        self.assertEqual(vertical, 1)
        image, horizontal, vertical = self.image_grid.validate_image_size(self.kingsize_y)
        image.crop.assert_called_once_with((0, 1, 16, 19,))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 2)
        try:
            self.image_grid.validate_image_size(self.too_small_x)
            self.fail("Grid didn't reject too narrow image")
        except ImageRejected:
            pass
        try:
            self.image_grid.validate_image_size(self.too_small_y)
            self.fail("Grid didn't reject too short image")
        except ImageRejected:
            pass
        try:
            self.image_grid.validate_image_size(self.too_small_xy)
            self.fail("Grid didn't reject too narrow and too short image")
        except ImageRejected:
            pass


