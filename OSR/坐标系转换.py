#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/16 14:47
# version: python 37

from osgeo import gdal,osr

ds = gdal.Open(r"E:\HN_Image\sourse.tif")
sr = ds.GetProjectionRef()
osr_ds = osr.SpatialReference()
osr_ds.ImportFromWkt(sr)

osr_wgs84 = osr.SpatialReference()
osr_wgs84.SetWellKnownGeogCS("WGS84")
judge = osr_wgs84.IsSame(osr_ds)
print(judge)
ct = osr.CoordinateTransformation(osr_ds,osr_wgs84)
ct.TransformPoint(590000,4928000)

print("WKT--->>>",osr_wgs84.ExportToWkt())
print("PROJ.4--->>>",osr_wgs84.ExportToProj4())
print("ESRI WKT--->>>",osr_wgs84.MorphToESRI())