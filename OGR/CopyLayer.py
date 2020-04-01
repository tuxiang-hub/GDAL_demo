#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/26 21:19
# version: python 37

from osgeo import gdal, osr, ogr
from shapely.wkt import dumps, loads
import json, geojson

src_file = r"E:\HN_Image\test\boundary.shp"
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
gdal.SetConfigOption("SHAPE_ENCODING", "")
ogr.RegisterAll()
ds = ogr.Open(src_file, update=1)
# print(dir(ds))
print(ds.GetName())
driver = ds.GetDriver()
print(driver.GetName())
# print(dir(driver))
oLayer = ds.GetLayerByIndex(0)
print(oLayer.GetFeatureCount())
oDefn = oLayer.GetLayerDefn()  # 获取图层的属性表结构
iFieldCount = oDefn.GetFieldCount()
print("字段个数", iFieldCount)

#############创建##############
outDriverName = "ESRI Shapefile"
outDriver = ogr.GetDriverByName(outDriverName)
# 创建数据源
outDS = outDriver.CreateDataSource(r"E:\HN_Image\test\boundary_out1.shp")
# 创建图层，创建一个多边形图层，这里没有指定空间参考，如果需要的话，需要在这里进行指定
print(dir(outDS))
print("数据源",outDS.GetName())
outLayer = outDS.CopyLayer(oLayer,"test")

#outfeatureddefn = outLayer.GetLayerDefn()

outFeature = outLayer.GetFeature(0)
#print(dir(oFeature))
#geom = oFeature.GetGeometryRef()
#outfeature = ogr.Feature(outfeatureddefn)
#print(dir(outfeature))
#print(geom.ExportToWkt())
wkt2 = "POLYGON ((114.837484008666 28.1090485692271,115.973553274691 28.1090485692271,115.973553274691 27.1502224596923,114.837484008666 27.1502224596923,114.837484008666 28.1090485692271))"
polygon = ogr.CreateGeometryFromWkt(wkt2)

#outFeature.SetFrom(oFeature)
outFeature.SetGeometry(polygon)
#outLayer.CreateFeature(outfeature)
outDS.Destroy()

