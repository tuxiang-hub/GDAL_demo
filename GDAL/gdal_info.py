#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/4 20:34
# version: python 

from osgeo import gdal
import time
start = time.time()
inImage = r"E:\HN_Image\test\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901-MUX.tiff"
#inImage = r"E:\HN_Image\test\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901-MUX2.tif"
#TempOut2 = r"E:\HN_Image\sourse.tif"

ds = gdal.Open(inImage)
#rows = ds.RasterYSize
#cols = ds.RasterXSize
#print(rows,cols)
#print(ds.GetGeoTransform())
#gdal.Warp("E:/HN_Image/work.tif",ds, format="GTiff",dstNodata=0.0, dstSRS="EPSG:4326")

info = gdal.Info(ds)
print(info)
end = time.time()
print(end-start)