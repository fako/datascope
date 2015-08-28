from __future__ import unicode_literals, absolute_import, print_function, division

import types

from PIL import Image

from unittest import TestCase
from mock import Mock, MagicMock

from core.utils.image import ImageGrid, ImageRejected, CouldNotFillGrid


def monkey_patch_mock_image(image):

    def resize(self, size, anti_alias):
        self.size = size
        return image

    image.resize = Mock(side_effect=types.MethodType(resize, image), return_value=image)
    image.crop = Mock(return_value=image)
    return image


class TestImageGrid(TestCase):

    maxDiff = None

    def setUp(self):
        self.image_grid = ImageGrid(4, 3, 16, 9)
        self.fit = monkey_patch_mock_image(MagicMock(Image.Image, size=(16, 9)))
        self.landscape = monkey_patch_mock_image(MagicMock(Image.Image, size=(20, 12)))
        self.panorama = monkey_patch_mock_image(MagicMock(Image.Image, size=(36, 10)))
        self.portrait = monkey_patch_mock_image(MagicMock(Image.Image, size=(18, 30)))

    def test_init(self):
        ig = ImageGrid(4, 3, 16, 9)
        self.assertEqual(len(ig.cells), 12)
        ig = ImageGrid(5, 5, 16, 9)
        self.assertEqual(len(ig.cells), 25)

    def test_validate_image_size(self):
        fit_panorama = Mock(Image.Image, size=(32, 9))
        fit_portrait = Mock(Image.Image, size=(16, 18))
        bigger = Mock(Image.Image, size=(17, 10))
        too_small_x = Mock(Image.Image, size=(12, 9))
        too_small_y = Mock(Image.Image, size=(16, 5))
        too_small_xy = Mock(Image.Image, size=(5, 5))

        exact_fit = self.image_grid.validate_image_size(self.fit)
        self.assertTrue(exact_fit)
        exact_fit = self.image_grid.validate_image_size(fit_panorama, horizontal=2)
        self.assertTrue(exact_fit)
        exact_fit = self.image_grid.validate_image_size(fit_portrait, vertical=2)
        self.assertTrue(exact_fit)
        exact_fit = self.image_grid.validate_image_size(bigger)
        self.assertFalse(exact_fit)
        try:
            self.image_grid.validate_image_size(too_small_x)
            self.fail("Grid didn't reject too narrow image")
        except ImageRejected:
            pass
        try:
            self.image_grid.validate_image_size(too_small_y)
            self.fail("Grid didn't reject too short image")
        except ImageRejected:
            pass
        try:
            self.image_grid.validate_image_size(too_small_xy)
            self.fail("Grid didn't reject too narrow and too short image")
        except ImageRejected:
            pass
    
    def test_get_image_info(self):
        is_landscape, is_panorama, is_portrait = self.image_grid.get_image_info(self.landscape)
        self.assertTrue(is_landscape)
        self.assertFalse(is_panorama)
        self.assertFalse(is_portrait)
        is_landscape, is_panorama, is_portrait = self.image_grid.get_image_info(self.panorama)
        self.assertFalse(is_landscape)
        self.assertTrue(is_panorama)
        self.assertFalse(is_portrait)
        is_landscape, is_panorama, is_portrait = self.image_grid.get_image_info(self.portrait)
        self.assertFalse(is_landscape)
        self.assertFalse(is_panorama)
        self.assertTrue(is_portrait)

    def test_size_image(self):
        # Fitting images should be ignored
        image, horizontal, vertical = self.image_grid.size_image(self.fit)
        image.resize.assert_not_called()
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)

        # Landscape size
        image, horizontal, vertical = self.image_grid.size_image(self.landscape)
        image.resize.assert_called_once_with((16, 10), 1)
        image.crop.called_once_with((0, 0, 16, 9))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)
        # Landscape size where resize shouldn't happen
        small_landscape = Mock(Image.Image, size=(22, 9))
        image, horizontal, vertical = self.image_grid.size_image(small_landscape)
        image.resize.assert_not_called()
        image.crop.called_once_with((3, 0, 19, 9))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 1)

        # Panorama size
        image, horizontal, vertical = self.image_grid.size_image(self.panorama)
        image.resize.assert_called_once_with((32, 9), 1)
        image.crop.called_once_with((0, 0, 0, 0))
        self.assertEqual(horizontal, 2)
        self.assertEqual(vertical, 1)
        # Landscape size where resize shouldn't happen
        small_panorama = Mock(Image.Image, size=(40, 9))
        image, horizontal, vertical = self.image_grid.size_image(small_panorama)
        image.resize.assert_not_called()
        image.crop.called_once_with((2, 0, 34, 9))
        self.assertEqual(horizontal, 2)
        self.assertEqual(vertical, 1)

        # Portrait size
        image, horizontal, vertical = self.image_grid.size_image(self.portrait)
        image.resize.assert_called_once_with((16, 27), 1)
        image.crop.called_once_with((0, 4, 16, 22))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 2)
        # Landscape size where resize shouldn't happen
        small_portrait = monkey_patch_mock_image(Mock(Image.Image, size=(19, 26)))
        image, horizontal, vertical = self.image_grid.size_image(small_portrait)
        image.resize.assert_not_called()
        image.crop.called_once_with((1, 4, 17, 22))
        self.assertEqual(horizontal, 1)
        self.assertEqual(vertical, 2)

    def test_center_image(self):
        image = self.image_grid.center_image(self.fit, 1, 1)
        image.crop.assert_called_once_with((0, 0, 16, 9))
        image = self.image_grid.center_image(self.landscape, 1, 1)
        image.crop.assert_called_once_with((2, 1, 18, 10))
        image = self.image_grid.center_image(self.panorama, 2, 1)
        image.crop.assert_called_once_with((2, 0, 34, 9))
        image = self.image_grid.center_image(self.portrait, 1, 2)
        image.crop.assert_called_once_with((1, 6, 17, 24))

    def test_fill(self):
        self.image_grid.fill([
            self.landscape,
            self.panorama,
            self.portrait
        ])
        self.assertEqual(self.image_grid.cells, [
            self.landscape, self.panorama, True, self.portrait,
            self.landscape, self.panorama, True, True,
            self.landscape, self.panorama, True, self.landscape,
        ])
        three_by_three = ImageGrid(3, 3, 16, 9)
        try:
            three_by_three.fill([
                self.panorama,
                self.portrait
            ])
            self.fail("Image grid completed a grid that is impossible.")
        except CouldNotFillGrid:
            pass
