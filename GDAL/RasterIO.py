#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/30 20:18
# version: python 37

from osgeo import gdal
input_file = ""
dataset = gdal.Open(input_file)
proj = dataset.GetProjection()
geo = dataset.GetGeoTransform()
rows = dataset.RasterYSize
cols = dataset.RasterXSize
couts = dataset.RasterCount

band = dataset.GetRasterBand(1)#波段编号从1开始的
band.Raster