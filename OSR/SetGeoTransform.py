#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/16 14:47
# version: python 37

from osgeo import gdal,osr
import math,os,time,datetime,traceback

inpath = r"E:\HN_Image\430182_ZY3_ZY302_GF1_2MDOM"
outpath = r"E:\HN_Image\aaa"

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
    def main(self, inImage, outImage):
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
        # print(judge)
        if judge == 1:
            print("坐标统一！")
            trans_form = ds.GetGeoTransform()
            GCJ02_xy = class_coord_trans.wgs84_to_gcj02(trans_form[0], trans_form[3])
            GCJ02_trans_form = (GCJ02_xy[0], trans_form[1], trans_form[2], GCJ02_xy[1], trans_form[4], trans_form[5])
            driver = gdal.GetDriverByName('GTiff')
            dst_ds = driver.CreateCopy(outImage, ds)
            dst_ds.SetGeoTransform(GCJ02_trans_form)
        else:
            print("坐标不统一！需要坐标转换！")
            gdal.Warp("wgs84_temp.tif", ds, format="GTiff", srcSRS=sr, dstSRS="EPSG:4326")
            ds = gdal.Open("wgs84_temp.tif")
            trans_form = ds.GetGeoTransform()
            GCJ02_xy = class_coord_trans.wgs84_to_gcj02(trans_form[0], trans_form[3])
            GCJ02_trans_form = (GCJ02_xy[0], trans_form[1], trans_form[2], GCJ02_xy[1], trans_form[4], trans_form[5])
            driver = gdal.GetDriverByName('GTiff')
            dst_ds = driver.CreateCopy(outImage, ds)
            dst_ds.SetGeoTransform(GCJ02_trans_form)

def main(inFolder, outFolder):
    class_ImageOffset = ImageOffset()
    for root, dirs, files in os.walk(inFolder):
        for file in files:
            if file[-3:].lower() == "img":
                print(file)
                start = time.time()
                try:
                    in_raster = os.path.join(root, file)
                    new_root = root.replace(inFolder, outFolder, 1)
                    if not os.path.exists(new_root):
                        os.makedirs(new_root)
                    out_raster = os.path.join(new_root, file[:-3]+"tif")
                    class_ImageOffset.main(in_raster, out_raster)
                    end = time.time()
                    print("Time: ", end - start)
                    with open('report.txt', 'a') as log:
                        log.write(in_raster + "\nTime: " + str(end - start) + "\n")
                except:
                    with open('Error.log', 'a') as log:
                        log.write("TIME: " + str(datetime.datetime.now()) + "\n")
                        log.write(os.path.join(root, file) + "\n")
                        traceback.print_exc(file=log)

if __name__ == '__main__':
    main(inpath, outpath)
