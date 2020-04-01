#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/6 23:59
# version: python 37

from osgeo import gdal

inpath = r"E:\HN_Image\test\GF1D_PMS_E111.4_N24.6_20190817_L1A1256618333\GF1D_PMS_E111.4_N24.6_20190817_L1A1256618333-MUX.tiff"

ds = gdal.Open(inpath)
#print(ds.GetGCPs())
print(gdal.Info(inpath,format='json'))
#gdal.GCP()是gdal中地面控制点的数据结构，顺序依次是：空间位置x,y,z,影像列号，行号
coordlist = [gdal.GCP(111.0160537,  24.9845278, 0, 0.0, 0.0),
             gdal.GCP(111.0160537,  24.2794623, 0, 0.0, 8488.0),
             gdal.GCP(111.7918916,  24.9845278, 0, 8540.0, 0.0),
             gdal.GCP(111.7918916,  24.2794623, 0, 8540.0, 8488.0)]
#print(dir(ds))

wkt = 'GEOGCRS["WGS 84",\n DATUM["World Geodetic System 1984",\n ELLIPSOID["WGS 84",6378137,298.257223563,\n LENGTHUNIT["metre",1]]],\n PRIMEM["Greenwich",0,\n ANGLEUNIT["degree",0.0174532925199433]],\n  CS[ellipsoidal,2],\n AXIS["geodetic latitude (Lat)",north,\n  ORDER[1],\nANGLEUNIT["degree",0.0174532925199433]],\n AXIS["geodetic longitude (Lon)",east,\n ORDER[2],\n  ANGLEUNIT["degree",0.0174532925199433]],\n    USAGE[\n        SCOPE["unknown"],\n        AREA["World"],\n        BBOX[-90,-180,90,180]],\n    ID["EPSG",4326]]'
ds.SetGCPs(coordlist,wkt)