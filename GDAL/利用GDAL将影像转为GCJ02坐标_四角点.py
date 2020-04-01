#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/4 17:36
# version: python 37

from osgeo import gdal,osr
import math,os,time

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
    def get_image_coner(self,inRaster):
        '''
        获取影像数据的四个脚点行列号及角点坐标
        :param inRaster:输入影像路径
        '''
        raster_info = gdal.Info(inRaster,format='json')
        # 获取影像四个脚点的行列号
        cols_rows = raster_info["size"]
        cols = cols_rows[0]
        rows = cols_rows[1]
        upperLeft_col_row = (0, 0)
        lowerLeft_col_row = (0, rows)
        lowerRight_col_row = (cols, rows)
        upperRight_col_row = (cols, 0)
        coner_col_row = (upperLeft_col_row, lowerLeft_col_row, lowerRight_col_row, upperRight_col_row)

        #获取影像四个脚点的坐标
        x_y = raster_info["cornerCoordinates"]
        upperLeft_xy = tuple(x_y['upperLeft'])
        lowerLeft_xy = tuple(x_y['lowerLeft'])
        lowerRight_xy = tuple(x_y['lowerRight'])
        upperRight_xy = tuple(x_y['upperRight'])
        coner_coord = (upperLeft_xy, lowerLeft_xy, lowerRight_xy, upperRight_xy)
        return coner_coord,coner_col_row

    def offset_image(self,inImage,outImage,coner_col_row,coner_coord):
        '''
        根据影像的脚点行列号及坐标，对影像进行偏移（配准）
        :param inImage:输入影像路径
        :param coner_col_row:元组，(upperLeft_col_row, lowerLeft_col_row, lowerRight_col_row, upperRight_col_row)
        :param coner_coord:元组，(upperLeft_xy, lowerLeft_xy, lowerRight_xy, upperRight_xy)
        '''
        #gdal.GCP()是gdal中地面控制点的数据结构，顺序依次是：空间位置x,y,z,影像列号，行号
        coordlist = [gdal.GCP(coner_coord[0][0], coner_coord[0][1], 0, coner_col_row[0][0], coner_col_row[0][1]),
                     gdal.GCP(coner_coord[1][0], coner_coord[1][1], 0, coner_col_row[1][0], coner_col_row[1][1]),
                     gdal.GCP(coner_coord[2][0], coner_coord[2][1], 0, coner_col_row[2][0], coner_col_row[2][1]),
                     gdal.GCP(coner_coord[3][0], coner_coord[3][1], 0, coner_col_row[3][0], coner_col_row[3][1])]

        # 根据脚点坐标进行配准
        gdal.Translate("TempOut1.tif",inImage, GCPs=coordlist)
        gdal.Warp(outImage,"TempOut1.tif", format="GTiff",srcNodata=0.0, dstNodata=0.0, dstSRS="EPSG:4326")

    def main(self,inImage,outImage):
        '''

        :param inImage:
        :return:
        '''
        class_coord_trans = CoordinateTransformation()
        ds = gdal.Open(inImage)
        sr = ds.GetProjectionRef()
        osr_ds_obj = osr.SpatialReference()
        osr_ds_obj.ImportFromWkt(sr)

        osr_wgs84_obj = osr.SpatialReference()
        osr_wgs84_obj.SetWellKnownGeogCS("WGS84")
        judge = osr_wgs84_obj.IsSame(osr_ds_obj)
        #print(judge)
        if judge == 1:
            print("坐标统一！")
            coner_coord,coner_col_row = self.get_image_coner(ds)
            upperLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[0][0],coner_coord[0][1]))
            lowerLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[1][0],coner_coord[1][1]))
            lowerRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[2][0],coner_coord[2][1]))
            upperRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[3][0],coner_coord[3][1]))
            coner_coord_gcj02 = (upperLeft_xy, lowerLeft_xy, lowerRight_xy, upperRight_xy)
            print(coner_coord_gcj02)
            self.offset_image(ds,outImage,coner_col_row,coner_coord_gcj02)
        else:
            print("坐标不统一！需要坐标转换！")
            gdal.Warp("wgs84_temp.tif", ds, format="GTiff", srcSRS=sr, dstSRS="EPSG:4326")
            ds2 = gdal.Open("wgs84_temp.tif")
            #sr = ds.GetProjectionRef()

            coner_coord, coner_col_row = self.get_image_coner(ds2)
            upperLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[0][0], coner_coord[0][1]))
            lowerLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[1][0], coner_coord[1][1]))
            lowerRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[2][0], coner_coord[2][1]))
            upperRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(coner_coord[3][0], coner_coord[3][1]))
            '''
            coner_coord,coner_col_row = self.get_image_coner(ds)
            ct = osr.CoordinateTransformation(osr_ds_obj, osr_wgs84_obj)
            upperLeft_coords_geos = ct.TransformPoint(coner_coord[0][0],coner_coord[0][1])#xy转换后结果是纬度、经度、高程
            upperLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(upperLeft_coords_geos[1],upperLeft_coords_geos[0]))
            
            lowerLeft_coords_geos = ct.TransformPoint(coner_coord[1][0], coner_coord[1][1])  # xy转换后结果是纬度、经度、高程
            lowerLeft_xy = tuple(class_coord_trans.wgs84_to_gcj02(lowerLeft_coords_geos[1], lowerLeft_coords_geos[0]))

            lowerRight_coords_geos = ct.TransformPoint(coner_coord[2][0], coner_coord[2][1])  # xy转换后结果是纬度、经度、高程
            lowerRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(lowerRight_coords_geos[1], lowerRight_coords_geos[0]))

            upperRight_coords_geos = ct.TransformPoint(coner_coord[3][0], coner_coord[3][1])  # xy转换后结果是纬度、经度、高程
            upperRight_xy = tuple(class_coord_trans.wgs84_to_gcj02(upperRight_coords_geos[1], upperRight_coords_geos[0]))
            '''
            coner_coord_gcj02 = (upperLeft_xy, lowerLeft_xy, lowerRight_xy, upperRight_xy)
            print(coner_coord_gcj02)
            self.offset_image(ds, outImage, coner_col_row, coner_coord_gcj02)

def main(inFolder,outFolder):
    class_ImageOffset = ImageOffset()
    for root, dirs, files in os.walk(inFolder):
        for file in files:
            if file[-3:].lower() == "tif":
                print(file)
                start = time.time()
                in_raster = os.path.join(root, file)
                new_root = root.replace(inFolder,outFolder,1)
                if not os.path.exists(new_root):
                    os.makedirs(new_root)
                out_raster = os.path.join(new_root, file)
                class_ImageOffset.main(in_raster,out_raster)
                end = time.time()
                print("Time: ",end-start)
                with open('report.txt', 'a') as log:
                    log.write(in_raster + "\nTime: "+str(end-start)+"\n")

if __name__ == '__main__':
    main(inpath,outpath)