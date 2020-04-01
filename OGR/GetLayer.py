#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/2 10:39
# version: python 37

from osgeo import ogr

path = r"E:\HN_Image\GF3\Temp\Boundary.shp"
#info = gdal.Info(r"E:\HN_Image\GF3\GF3_SAY_NSC_015430_E113.7_N29.0_20190716_L1A_HHHV_L10004118271.tar.gz")
#print(info)
drv = ogr.GetDriverByName("ESRI Shapefile")
ds = drv.Open(path, 0)
#ds = ogr.Open(path)
oLayer = ds.GetLayer(0)
layercount = ds.GetLayerCount()
print(layercount)
sr = oLayer.GetSpatialRef()
print(sr)

featureCount = oLayer.GetFeatureCount()
print(featureCount)
oFeature = oLayer.GetFeature(0)


#print(dir(oFeature))
geom = oFeature.GetGeometryRef()#wktvalue的字符串
boundary = geom.Boundary()
print(boundary)