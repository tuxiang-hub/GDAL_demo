#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/27 15:23
# version: python 37

from osgeo import gdal, osr, ogr
from shapely.wkt import dumps, loads
from shapely.geometry import asShape
import json

src_file = r"E:\HN_Image\test\multiline.shp"
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
oFeature = oLayer.GetFeature(0)
geom = oFeature.GetGeometryRef()  # wktvalue的字符串
wkt = json.loads(geom.ExportToJson())
print(wkt)
mylist = wkt['coordinates']
#print(mylist)

for i in range(len(mylist)):
    print(i)
    print(mylist[i])


#shape = asShape(wkt)
#print(shape)
'''
#############创建##############
outDriverName = "ESRI Shapefile"
outDriver = ogr.GetDriverByName(outDriverName)
# 创建数据源
outDS = outDriver.CreateDataSource(r"E:\HN_Image\test\boundary_out3.shp")
# 创建图层，创建一个多边形图层，这里没有指定空间参考，如果需要的话，需要在这里进行指定
print("数据源",outDS.GetName())
papszLCO = []
outLayer = outDS.CreateLayer("TestPolygon", oLayer.GetSpatialRef(), geom_type = oLayer.GetGeomType())
outfeatureddefn = outLayer.GetLayerDefn()
outfeature = ogr.Feature(outfeatureddefn)

polygon = ogr.CreateGeometryFromWkt(str(shape))

#outfeature.SetFrom(oFeature)
outfeature.SetGeometry(polygon)
outLayer.CreateFeature(outfeature)
'''