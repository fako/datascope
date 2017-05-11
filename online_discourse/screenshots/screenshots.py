import json
from selenium import webdriver


# sites = json.load(open("tmp.json"))
# driver = webdriver.PhantomJS()
# driver.set_window_size(1024,768)
#
#
# for index, site in enumerate(sites):
#     try:
#         driver.get(site["url"])
#     except:
#         print("Skipped: {}".format(site["url"]))
#         continue
#     driver.save_screenshot("{}.png".format(index))

from core.utils.image import ImageGrid
import os
from PIL import Image
from random import shuffle

images = [Image.open(entry.name) for entry in os.scandir(".") if entry.name.endswith(".png")]

grid = ImageGrid(8, 6, 640, 360)
grid.fill(images=images)
grid.export('sites.png')
