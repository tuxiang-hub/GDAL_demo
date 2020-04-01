#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/18 14:54
# version: python 37

from osgeo import gdal

def get_col_row(cols,rows,interval=1000):
    '''
    根据总列数，总行数，间隔值，计算需要加密的行列号，并返回
    :param cols: 栅格总列数
    :param rows: 栅格总行数
    :param interval: 间隔值，默认1000
    :return: 返回一个元组((col1,row1),(col2,row2),(col3,row3)......)
    '''
    col_row_list = []
    if cols % interval != 0:#获取最后一列的行列号
        for row in range(0,rows+1,interval):
            col_row_list.append((cols,row))
    if rows % interval != 0:#获取最后一行的行列号
        for col in range(0,cols+1,interval):
            col_row_list.append((col,rows))
    if rows % interval != 0 and cols % interval != 0:#获取（cols，rows）
        col_row_list.append((cols,rows))

    for i in range(0,rows+1,interval):
        for j in range(0,cols+1,interval):
            col_row_list.append((j,i))
    return tuple(col_row_list)

def caculate_xy_by_col_row(geotransform,col_row_tuple):
    '''
    根据行列号计算做对应行列号的坐标，像素左上角的坐标，不是像素中心的坐标
    :param geotransform:gdal获取的数据集六参数
    :param col_row_tuple:列号、行号元组((col1,row1),(col2,row2),(col3,row3)......)
    :return:返回对应行列号的xy元组((x1,y1),(x2,y2),(x3,y3)......)
    '''
    xy_list = []
    for i in range(len(col_row_tuple)):
        x = geotransform[0] + col_row_tuple[i][0] * abs(geotransform[1])
        y = geotransform[3] - col_row_tuple[i][1] * abs(geotransform[5])
        xy_list.append((x,y))
    return tuple(xy_list)

ds = gdal.Open(r"E:\HN_Image\sourse_clip.tif")
rows = ds.RasterYSize
cols = ds.RasterXSize
geotransform = ds.GetGeoTransform()

col_row_tuple = get_col_row(cols,rows)
print(col_row_tuple)
xy_tuple = caculate_xy_by_col_row(geotransform,col_row_tuple)
print(xy_tuple)