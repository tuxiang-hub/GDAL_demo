#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/29 17:03
# version: python 37

from osgeo import gdal_array as ga

def calculateNdvi(clip_raster,ndvi_raster):
    print("calculate NDVI...")
    img_array = ga.LoadFile(clip_raster)
    a = img_array[3]-img_array[2]
    b = img_array[3]+img_array[2]
    ndvi_array = a/b
    outndvi = ga.SaveArray(ndvi_array,ndvi_raster,format="GTiff",prototype=clip_raster)
    outndvi = None

