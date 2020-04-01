#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/12 9:07
# version: python 37

from osgeo import gdal

ds = gdal.Open(r"E:\HN_Image\test\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901-MUX.tiff")
print(gdal.Info(ds))
band = ds.GetRasterBand(1)#波段编号从1开始的
min_max = band.ComputeRasterMinMax(True)
print(min_max)

temp = r"E:\HN_Image\test\test.tif"
gdal.Warp(temp,ds, format="GTiff",dstNodata=0.0,rpc=True, dstSRS="EPSG:4326")
ds2 = gdal.Open(temp)
print(gdal.Info(ds2))
band2 = ds2.GetRasterBand(1)#波段编号从1开始的
min_max2 = band2.ComputeRasterMinMax()
print(min_max2)
