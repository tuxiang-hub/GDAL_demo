#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/17 9:17
# version: python 37

from osgeo import gdal,osr

ds = gdal.Open(r"E:\HN_Image\430182_ZY3_ZY302_GF1_2MDOM\430182_ZY3_ZY302_GF1_2MDOM.img")
sr = ds.GetProjectionRef()
#osr_ds_obj = osr.SpatialReference()
#osr_ds_obj.ImportFromWkt(sr)

#osr_wgs84_obj = osr.SpatialReference()
#osr_wgs84_obj.SetWellKnownGeogCS("WGS84")
gdal.Warp("test.tif",ds,format="GTiff",srcSRS = sr,dstSRS ="EPSG:4326")