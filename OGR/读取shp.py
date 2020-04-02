#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/23 23:03
# version: python 

# -*- coding: cp936 -*-
try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError:
    import gdal
    import ogr

def ReadVectorFile():
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    strVectorFile = r"E:\HN_Image\test\boundary.shp"

    # 注册所有的驱动
    ogr.RegisterAll()

    # 打开数据
    ds = ogr.Open(strVectorFile, 0)
    if ds == None:
        print("打开文件【%s】失败！", strVectorFile)
        return

    print("打开文件【%s】成功！", strVectorFile)

    # 获取该数据源中的图层个数，一般shp数据图层只有一个，如果是mdb、dxf等图层就会有多个
    iLayerCount = ds.GetLayerCount()

    # 获取第一个图层
    oLayer = ds.GetLayerByIndex(0)
    if oLayer == None:
        print("获取第%d个图层失败！\n", 0)
        return

    # 对图层进行初始化，如果对图层进行了过滤操作，执行这句后，之前的过滤全部清空
    oLayer.ResetReading()

    # 通过属性表的SQL语句对图层中的要素进行筛选，这部分详细参考SQL查询章节内容
    #oLayer.SetAttributeFilter("\"NAME99\"LIKE \"北京市市辖区\"")

    # 通过指定的几何对象对图层中的要素进行筛选
    # oLayer.SetSpatialFilter()

    # 通过指定的四至范围对图层中的要素进行筛选
    # oLayer.SetSpatialFilterRect()

    # 获取图层中的属性表表头并输出
    print("属性表结构信息：")
    oDefn = oLayer.GetLayerDefn()
    iFieldCount = oDefn.GetFieldCount()
    print("字段个数 {0}".format(iFieldCount))
    for iAttr in range(iFieldCount):
        oField = oDefn.GetFieldDefn(iAttr)
        print(oField)
        '''
        print("%s: %s(%d.%d)" % ( \
            oField.GetNameRef(), \
            oField.GetFieldTypeName(oField.GetType()), \
            oField.GetWidth(), \
            oField.GetPrecision()))
        '''
    # 输出图层中的要素个数
    print("要素个数 = %d", oLayer.GetFeatureCount(0))

    oFeature = oLayer.GetNextFeature()
    # 下面开始遍历图层中的要素
    while oFeature is not None:
        print("当前处理第%d个: \n属性值：", oFeature.GetFID())
        # 获取要素中的属性表内容
        for iField in range(iFieldCount):
            oFieldDefn = oDefn.GetFieldDefn(iField)
            line = " %s (%s) = " % (oFieldDefn.GetNameRef(),ogr.GetFieldTypeName(oFieldDefn.GetType()))

            if oFeature.IsFieldSet(iField):
                line = line + "%s" % (oFeature.GetFieldAsString(iField))
            else:
                line = line + "(null)"

            print(line)

        # 获取要素中的几何体
        oGeometry = oFeature.GetGeometryRef()

        # 为了演示，只输出一个要素信息

    print("数据集关闭！")

ReadVectorFile()