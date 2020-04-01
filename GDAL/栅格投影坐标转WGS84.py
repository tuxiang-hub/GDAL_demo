#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/17 18:48
# version: python 37

from osgeo import gdal
import re,os,time,datetime,traceback

inpath = r"E:\HN_Image\test\test"
outpath = r"E:\HN_Image\result"

def string_replace(string):
    m = re.findall('"([^"]+)"', string)
    #print(m)
    return string.replace(m[0], "CGCS2000_PRJ", 1)

def coords_transform(inImage, outImage):
    '''
    :param inImage:
    :return:
    '''
    ds = gdal.Open(inImage)
    sr = ds.GetProjectionRef()
    try:
        gdal.Warp(outImage, ds, format="GTiff", srcSRS=sr, dstSRS="EPSG:4326")
    except:
        new_sr = string_replace(sr)
        gdal.Warp(outImage, ds, format="GTiff", srcSRS=new_sr, dstSRS="EPSG:4326")

def main(inFolder,outFolder):
    for root, dirs, files in os.walk(inFolder):
        #print(root)
        for file in files:
            if file[-3:].lower() == "img" or file[-3:].lower() == "tif":
                print(file)
                start = time.time()
                try:
                    in_raster = os.path.join(root, file)
                    new_root = root.replace(inFolder,outFolder,1)
                    if not os.path.exists(new_root):
                        os.makedirs(new_root)
                    out_raster = os.path.join(new_root, file[:-3]+"tif")
                    coords_transform(in_raster,out_raster)
                    end = time.time()
                    print("Time: ", end - start)
                    with open('report.txt', 'a') as log:
                        log.write(in_raster + "\nTime: "+str(end-start)+"\n")
                except:
                    with open('Error.log', 'a') as log:
                        log.write("TIME: " + str(datetime.datetime.now()) + "\n")
                        log.write(os.path.join(root, file)+"\n")
                        traceback.print_exc(file=log)

if __name__ == '__main__':
    main(inpath,outpath)