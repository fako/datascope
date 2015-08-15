from __future__ import unicode_literals, absolute_import, print_function, division

from PIL import Image

from unittest import TestCase
from mock import Mock

from core.utils.image import ImageGrid



class TestImageGrid(TestCase):

    def setUp(self):
        self.image_grid = ImageGrid(4, 3, 16, 9, 0)
        self.fit = Mock(Image.Image, size=(16, 9))
        self.oversize_x = Mock(Image.Image, size=(18, 9))
        self.oversize_y = Mock(Image.Image, size=(16, 11))
        self.oversize_xy = Mock(Image.Image, size=(18, 11))
        self.oversize_xyr = Mock(Image.Image, size=(17, 10))

    def test_init(self):
        ig = ImageGrid(4, 3, 16, 9, 0)
        self.assertEqual(len(ig.cells), 12)
        ig = ImageGrid(5, 5, 16, 9, 0)
        self.assertEqual(len(ig.cells), 25)

    def test_validate_image_size(self):
        left, upper, right, lower = self.image_grid.validate_image_size(self.fit)
        self.assertEqual(left, 0)
        self.assertEqual(upper, 0)
        self.assertEqual(right, 16)
        self.assertEqual(lower, 9)
        left, upper, right, lower = self.image_grid.validate_image_size(self.oversize_x)
        self.assertEqual(left, 1)
        self.assertEqual(upper, 0)
        self.assertEqual(right, 17)
        self.assertEqual(lower, 9)
        left, upper, right, lower = self.image_grid.validate_image_size(self.oversize_y)
        self.assertEqual(left, 0)
        self.assertEqual(upper, 1)
        self.assertEqual(right, 16)
        self.assertEqual(lower, 10)
        left, upper, right, lower = self.image_grid.validate_image_size(self.oversize_xy)
        self.assertEqual(left, 1)
        self.assertEqual(upper, 1)
        self.assertEqual(right, 17)
        self.assertEqual(lower, 10)
        left, upper, right, lower = self.image_grid.validate_image_size(self.oversize_xyr)
        self.assertEqual(left, 0)
        self.assertEqual(upper, 0)
        self.assertEqual(right, 16)
        self.assertEqual(lower, 9)
