#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/4 17:36
# version: python 37

from osgeo import gdal,osr
import math,os,time,datetime,traceback

inpath = r"E:\HN_Image\test\test"
outpath = r"E:\HN_Image\result"

class CoordinateTransformation():
    def __init__(self):
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0
        self.pi = math.pi  # π
        self.ee = 0.00669342162296594323  # 偏心率平方
        #CGCS2000扁率0.00335281068118231893543414612613
        #wgs84扁率0.00335281066474748071984552861852‬
        self.a = 6378245.0  # 长半轴

    def _transformlat(self,lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 *
                math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 *
                math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformlng(self,lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 *
                math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 *
                math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def out_of_china(self,lng, lat):
        """
        判断是否在国内，不在国内不做偏移
        :param lng:
        :param lat:
        :return:
        """
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

    def wgs84_to_gcj02(self,lng, lat):
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        if self.out_of_china(lng, lat):  # 判断是否在国内
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]

    def gcj02_to_bd09(self,lng, lat):
        """
        火星坐标系(GCJ-02)转百度坐标系(BD-09)
        谷歌、高德——>百度
        :param lng:火星坐标经度
        :param lat:火星坐标纬度
        :return:
        """
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * self.x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * self.x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return [bd_lng, bd_lat]

    def wgs84_to_bd09(self,lon, lat):
        lon_gcj, lat_gcj = self.wgs84_to_gcj02(lon, lat)
        return self.gcj02_to_bd09(lon_gcj, lat_gcj)

class ImageOffset():
    def get_col_row(self, cols, rows, interval=1000):
        '''
        根据总列数，总行数，间隔值，计算需要加密的行列号，并返回
        :param cols: 栅格总列数
        :param rows: 栅格总行数
        :param interval: 间隔值，默认1000
        :return: 返回一个元组((col1,row1),(col2,row2),(col3,row3)......)
        '''
        col_row_list = []
        if cols % interval != 0:  # 获取最后一列的行列号
            for row in range(0, rows + 1, interval):
                col_row_list.append((cols, row))
        if rows % interval != 0:  # 获取最后一行的行列号
            for col in range(0, cols + 1, interval):
                col_row_list.append((col, rows))
        if rows % interval != 0 and cols % interval != 0:  # 获取（cols，rows）
            col_row_list.append((cols, rows))

        for i in range(0, rows + 1, interval):
            for j in range(0, cols + 1, interval):
                col_row_list.append((j, i))
        return tuple(col_row_list)

    def caculate_xy_by_col_row(self, geotransform, col_row_tuple):
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
            xy_list.append((x, y))
        return tuple(xy_list)

    def offset_image(self, inImage, outImage, list_col_row, list_xy):
        '''
        根据影像的行列号及对应坐标，对影像进行偏移
        :param inImage: 输入影像路径
        :param outImage: 输入影像路径
        :param list_col_row: 行列号的列表（元组）
        :param list_xy: xy坐标的列表（元组
        :return: 无返回值
        '''
        #gdal.GCP()是gdal中地面控制点的数据结构，顺序依次是：空间位置x,y,z,影像列号，行号
        coordlist = []
        if len(list_col_row) == len(list_xy):
            print("构建GCPs列表......")
            for i in range(len(list_col_row)):
                coordlist.append(gdal.GCP(list_xy[i][0], list_xy[i][1], 0, list_col_row[i][0], list_col_row[i][1]))

            # 根据脚点坐标进行配准
            print("为影像写入GCPs......")
            gdal.Translate("TempOut1.tif",inImage, GCPs=coordlist)
            print("终极变换！")
            gdal.Warp(outImage,"TempOut1.tif", format="GTiff",srcNodata=0.0, dstNodata=0.0, dstSRS="EPSG:4326")
        else:
            print("行列号与xy坐标对数量不匹配，请检查！")

    def read_image(self, inImage):
        ds = gdal.Open(inImage)
        sr = ds.GetProjectionRef()
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        geotransform = ds.GetGeoTransform()
        return ds,sr,rows,cols,geotransform

    def main(self, inImage, outImage, out_wgs84_image):
        '''

        :param inImage:
        :return:
        '''
        class_coord_trans = CoordinateTransformation()
        ds,sr,rows,cols,geotransform = self.read_image(inImage)

        osr_ds_obj = osr.SpatialReference()
        osr_ds_obj.ImportFromWkt(sr)

        osr_wgs84_obj = osr.SpatialReference()
        osr_wgs84_obj.SetWellKnownGeogCS("WGS84")
        judge = osr_wgs84_obj.IsSame(osr_ds_obj)
        #print(judge)
        if judge == 1:
            print("坐标统一！")
            col_row_list = self.get_col_row(cols,rows)
            WGS84_xy_list = self.caculate_xy_by_col_row(geotransform,col_row_list)
            GCJ02_xy_list = []
            for i in range(len(WGS84_xy_list)):
                GCJ02_xy_list.append(tuple(class_coord_trans.wgs84_to_gcj02(WGS84_xy_list[i][0], WGS84_xy_list[i][1])))
            self.offset_image(ds, outImage, col_row_list, GCJ02_xy_list)
        else:
            print("坐标不统一！需要坐标转换！")
            WGS84_Image_root,filename = os.path.split(out_wgs84_image)
            if not os.path.exists(WGS84_Image_root):
                os.makedirs(WGS84_Image_root)
            gdal.Warp(out_wgs84_image, ds, format="GTiff", srcSRS=sr, dstSRS="EPSG:4326")
            ds2,sr2,rows2,cols2,geotransform2 = self.read_image(out_wgs84_image)
            col_row_list2 = self.get_col_row(cols2, rows2)
            WGS84_xy_list2 = self.caculate_xy_by_col_row(geotransform2, col_row_list2)
            GCJ02_xy_list2 = []
            for i in range(len(WGS84_xy_list2)):
                GCJ02_xy_list2.append(tuple(class_coord_trans.wgs84_to_gcj02(WGS84_xy_list2[i][0], WGS84_xy_list2[i][1])))
            self.offset_image(ds, outImage, col_row_list2, GCJ02_xy_list2)

def main(inFolder,outFolder):
    class_ImageOffset = ImageOffset()
    for root, dirs, files in os.walk(inFolder):
        # print(root)
        for file in files:
            if file[-3:].lower() == "img" or file[-3:].lower() == "tif":
                print(file)
                start = time.time()
                try:
                    in_raster = os.path.join(root, file)
                    new_root = root.replace(inFolder, outFolder, 1)
                    if not os.path.exists(new_root):
                        os.makedirs(new_root)
                    out_raster = os.path.join(new_root, file)

                    WGS84_Image_root = root.replace(inFolder, outFolder + "/WGS84_Image", 1)
                    WGS84_raster = os.path.join(WGS84_Image_root, file[:-3] + "tif")

                    class_ImageOffset.main(in_raster, out_raster, WGS84_raster)
                    end = time.time()
                    print("Time: ", end - start)
                    with open('report.txt', 'a') as log:
                        log.write(in_raster + " Time: " + str(end - start) + "\n")
                except:
                    with open('Error.log', 'a') as log:
                        log.write("TIME: " + str(datetime.datetime.now()) + "\n")
                        log.write(os.path.join(root, file) + "\n")
                        traceback.print_exc(file=log)

if __name__ == '__main__':
    start_time = time.time()
    with open('report.txt', 'a') as log:
        log.write("TIME: " + str(datetime.datetime.now()) + "\n")
        log.write("本次计算输入数据路径为: " + inpath +"\n")
        log.write("本次计算输出数据路径为: " + outpath + "\n")
    print("starting......")
    main(inpath,outpath)
    print("End!!!")
    end_time = time.time()
    print("总计用时：",(end_time-start_time)/3600," h")
    with open('report.txt', 'a') as log:
        log.write("TIME: " + str(datetime.datetime.now()) + "\n")
        log.write("本次计算总计用时："+str((end_time-start_time)/3600)+" h"+ "\n\n")