#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/26 19:48
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
outDS = outDriver.CreateDataSource(r"E:\HN_Image\test\boundary_out.shp")
# 创建图层，创建一个多边形图层，这里没有指定空间参考，如果需要的话，需要在这里进行指定
print("数据源",outDS.GetName())
papszLCO = []
outLayer = outDS.CreateLayer("TestPolygon", oLayer.GetSpatialRef(), geom_type = oLayer.GetGeomType())

# 下面创建属性表
# 先创建一个叫FieldID的整型属性
# outFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)
# outLayer.CreateField(outFieldID, 1)

filed_list = []
for iAttr in range(iFieldCount):
    oField = oDefn.GetFieldDefn(iAttr)
    print(oField.GetNameRef(), oField.GetType(), oField.GetFieldTypeName(oField.GetType()), oField.GetWidth(),
          oField.GetPrecision())
    filed_list.append((oField.GetNameRef(), oField.GetType(), oField.GetFieldTypeName(oField.GetType()),
                       oField.GetWidth(), oField.GetPrecision()))
    outFieldID = ogr.FieldDefn(oField.GetNameRef(), oField.GetType())
    outLayer.CreateField(outFieldID, 1)  # 创建字段，参数1为兼容设置

outfeatureddefn = outLayer.GetLayerDefn()

oFeature = oLayer.GetFeature(0)
#print(dir(oFeature))
#geom = oFeature.GetGeometryRef()
outfeature = ogr.Feature(outfeatureddefn)
print(dir(outfeature))
#print(geom.ExportToWkt())
wkt2 = "POLYGON ((114.837484008666 28.1090485692271,115.973553274691 28.1090485692271,115.973553274691 27.1502224596923,114.837484008666 27.1502224596923,114.837484008666 28.1090485692271))"
polygon = ogr.CreateGeometryFromWkt(wkt2)

outfeature.SetFrom(oFeature)
outfeature.SetGeometry(polygon)
outLayer.CreateFeature(outfeature)

