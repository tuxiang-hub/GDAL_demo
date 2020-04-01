#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/5 11:05
# version: python 37

from osgeo import gdal
import time
start = time.time()
inpath = r"E:\HN_Image\test\GF1D_PMS_E111.4_N24.6_20190817_L1A1256618333\GF1D_PMS_E111.4_N24.6_20190817_L1A1256618333-MUX.tiff"
''''''
#TempOut1 = "TempOut1.tif"
#TempOut2 = "TempOut2.tif"
def offset_image(inImage, coner_col_row, coner_coord,temp1,temp2):
    '''
    根据影像的脚点行列号及坐标，对影像进行偏移（配准）
    :param inImage:输入影像路径
    :param coner_col_row:元组，(upperLeft_col_row, lowerLeft_col_row, lowerRight_col_row, upperRight_col_row)
    :param coner_coord:元组，(upperLeft_xy, lowerLeft_xy, lowerRight_xy, upperRight_xy)
    '''
    # gdal.GCP()是gdal中地面控制点的数据结构，顺序依次是：空间位置x,y,z,影像列号，行号
    coordlist = [gdal.GCP(coner_coord[0][0], coner_coord[0][1], 0, coner_col_row[0][0], coner_col_row[0][1]),
                 gdal.GCP(coner_coord[1][0], coner_coord[1][1], 0, coner_col_row[1][0], coner_col_row[1][1]),
                 gdal.GCP(coner_coord[2][0], coner_coord[2][1], 0, coner_col_row[2][0], coner_col_row[2][1]),
                 gdal.GCP(coner_coord[3][0], coner_coord[3][1], 0, coner_col_row[3][0], coner_col_row[3][1])]

    # 根据脚点坐标进行配准
    gdal.Translate(temp1, inImage, GCPs=coordlist)
    gdal.Warp(temp2, temp1, format="MEM", srcNodata=0.0, dstNodata=0.0, dstSRS="EPSG:4326")

dst_ds = gdal.Open(inpath)
driver = gdal.GetDriverByName('MEM')
temp1_ds = driver.CreateCopy("temp1",dst_ds)
temp2_ds = driver.CreateCopy("temp2",dst_ds)

te1 = gdal.Open("temp1")
te2 = gdal.Open("temp2")

raster_info = gdal.Info(dst_ds,format = "json")
cols_rows = raster_info["size"]
cols = cols_rows[0]
rows = cols_rows[1]
upperLeft_col_row = (0, 0)
lowerLeft_col_row = (0, rows)
lowerRight_col_row = (cols, rows)
upperRight_col_row = (cols, 0)
coner_col_row = (upperLeft_col_row, lowerLeft_col_row,upperRight_col_row, lowerRight_col_row)
coner_coord = ((111.0160537,  24.9845278), (111.0160537,  24.2794623), (111.7918916,  24.9845278), (111.7918916,  24.2794623))
#print(info2)
for i in range(10):
    print(i)
    offset_image(dst_ds, coner_col_row, coner_coord,te1,te2)

end = time.time()
print("time: ",end-start)
#driver = gdal.GetDriverByName('MEM')
