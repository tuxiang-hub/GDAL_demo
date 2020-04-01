#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/4 15:57
# version: python 37

from osgeo import gdal

driver_count = gdal.GetDriverCount()
print(driver_count)

driver = gdal.GetDriver(1)
print(driver)