#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/11 15:25
# version: python 37

from osgeo import gdal
import time
import numpy as np

start = time.time()
class DataProcessing():
    def read_image(self, input_file):
        """
        读取影像
        :param input_file:输入影像
        :return:波段数据，仿射变换参数，投影信息、行数、列数、波段数
        """
        dataset = gdal.Open(input_file)
        proj = dataset.GetProjection()
        geo = dataset.GetGeoTransform()
        temp = "temp.tif"
        if proj == '' and geo[0]==0.0 and geo[1]==1.0:
            print("数据没有坐标系")
            gdal.Warp(temp, dataset, format="GTiff",dstNodata=0.0)
            #del dataset
            dataset = gdal.Open(temp)
            proj = dataset.GetProjection()
        else:
            pass
        rows = dataset.RasterYSize
        cols = dataset.RasterXSize
        couts = dataset.RasterCount
        array_data = np.zeros((couts, rows, cols))
        hist_list = []
        bin_list = []
        for i in range(couts):
            band = dataset.GetRasterBand(i + 1)#波段编号从1开始的
            array_data[i, :, :] = band.ReadAsArray()
            min_max = band.ComputeRasterMinMax(False)
            min = int(min_max[0])
            max = int(min_max[1]+1)
            #min = int(band.GetMinimum())#获取的最小值一般是0，而0一般是nodata值，因此统计从1开始

            hist = band.GetHistogram(min, max, max - min, False, False)#间隔为1获取直方图
            bin = range(min,max)
            hist_list.append(hist)#把每个波段的直方图统计的列表写入hist_list，hist_list中有couts个列表
            bin_list.append(bin)#把每个波段的横坐标栅格区间值的列表写入bin_list，bin_list中有couts个列表
        return array_data, geo, proj, rows, cols, couts, hist_list, bin_list

    def write_image(self, output_file, array_data, rows, cols, counts, geo, proj):
        Driver = gdal.GetDriverByName("Gtiff")
        dataset = Driver.Create(output_file, cols, rows, counts, gdal.GDT_Byte)

        dataset.SetGeoTransform(geo)
        dataset.SetProjection(proj)

        for i in range(counts):
            band = dataset.GetRasterBand(i + 1)
            band.WriteArray(array_data[i, :, :])  # 波段写入顺序调整可以改变图像颜色，思路i改为2-i
        del dataset

    def cumulative_histogram(self,inValueList,inHistList):
        '''
        根据频率统计列表，计算累计频率,然后按照2％和98％进行截断
        :param inValueList: 横坐标的值，列表
        :param inHistList: 纵坐标的频率值，列表
        :return:百分比截断后的的波段最小值和最大值
        '''
        cumulative_hist_list = []
        cell_counts = sum(inHistList)
        count_percent2 = cell_counts * 0.02
        count_percent98 = cell_counts * 0.98
        index_percent2 = 0
        index_percent98 = 0
        for i in range(len(inHistList)):
            if i == 0:
                cumulative_hist_list.append(inHistList[i])
            else:
                cumulative_hist_list.append(inHistList[i]+cumulative_hist_list[i-1])
                #当累计频率达到2％时，取其下标索引值
                if count_percent2 <= cumulative_hist_list[i] and count_percent2 >= cumulative_hist_list[i-1]:
                    index_percent2 = i
                # 当累计频率达到98％时，取其下标索引值
                if count_percent98 <= cumulative_hist_list[i] and count_percent98 >= cumulative_hist_list[i-1]:
                    index_percent98 = i-1
        if index_percent2 == 0 and index_percent98 == 0:
            return False
        else:
            cut_min = inValueList[index_percent2]
            cut_max = inValueList[index_percent98]
            return (cut_min,cut_max)

    def compress(self, origin_16, output_8):
        '''
        输入16bit（或者更高bit影像），拉伸为8bit
        :param origin_16: 输入16bit影像
        :param output_8: 输出8bit影像
        :return: 无
        '''
        array_data, geo, proj, rows, cols, couts, hist_list, bin_list = self.read_image(origin_16)
        compress_data = np.zeros((couts, rows, cols))
        for i in range(couts):
            cutmin, cutmax = self.cumulative_histogram(bin_list[i],hist_list[i])
            compress_scale = (cutmax - cutmin) / 255#转换到8bit
            temp = np.array(array_data[i, :, :])
            temp[temp > cutmax] = cutmax
            temp[temp < cutmin] = cutmin
            compress_data[i, :, :] = (temp - cutmin) / compress_scale
        self.write_image(output_8, compress_data, rows, cols, couts, geo, proj)

classDataProcessing =DataProcessing()
classDataProcessing.compress(r"E:\HN_Image\test\16\quick\GF6_PMS_E114.4_N27.6_20190123_L1A1119841901-MUX_quick.PNG",r"E:\HN_Image\test\16\test2.tif")
end = time.time()
print(end-start)