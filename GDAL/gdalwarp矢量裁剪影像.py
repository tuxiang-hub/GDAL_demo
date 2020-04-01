#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "tuxiang"
# Email: tuxiang1993@126.com
# Time: 2019/12/27 13:54
# version: python 37

from osgeo import gdal
import time

starttime = time.time()
inpath = r"E:\DATA\test.tif"
inshp = r"E:\DATA\testclip.shp"
outpath = r"E:\DATA\testclip.tif"
for i in range(50):
    gdal.Warp(outpath,inpath,cutlineDSName=inshp)

endtime = time.time()
print("TIME: ",endtime - starttime)