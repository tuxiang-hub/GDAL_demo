#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/23 23:07
# version: python 

import os,sys
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import numpy
import transformer
# 为了支持中文路径，请添加下面这句代码


pathname = ""

#choose = sys.argv[2]
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
# 为了使属性表字段支持中文，请添加下面这句
gdal.SetConfigOption("SHAPE_ENCODING", "")
# 注册所有的驱动
ogr.RegisterAll()
# 数据格式的驱动
driver = ogr.GetDriverByName('ESRI Shapefile')
ds = driver.Open(pathname, update=1)
if ds is None:
    print('Could not open %s'%pathname)
    sys.exit(1)
# 获取第0个图层
layer0 = ds.GetLayerByIndex(0)
# 投影
spatialRef = layer0.GetSpatialRef()
# 输出图层中的要素个数
print('要素个数=%d'%(layer0.GetFeatureCount(0)))
print('属性表结构信息')
defn = layer0.GetLayerDefn()
fieldindex = defn.GetFieldIndex('x')
xfield = defn.GetFieldDefn(fieldindex)
#新建field
fieldDefn = ogr.FieldDefn('newx', xfield.GetType())
fieldDefn.SetWidth(32)
fieldDefn.SetPrecision(6)
layer0.CreateField(fieldDefn,1)
fieldDefn = ogr.FieldDefn('newy', xfield.GetType())
fieldDefn.SetWidth(32)
fieldDefn.SetPrecision(6)
layer0.CreateField(fieldDefn,1)
feature = layer0.GetNextFeature()
# 下面开始遍历图层中的要素
while feature is not None:
    # 获取要素中的属性表内容
    x = feature.GetFieldAsDouble('x')
    y = feature.GetFieldAsDouble('y')
    newx, newy = transformer.begintrans(choose, x, y)
    feature.SetField('newx', newx)
    feature.SetField('newy', newy)
    layer0.SetFeature(feature)
    feature = layer0.GetNextFeature()
feature.Destroy()
ds.Destroy()