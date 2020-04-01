#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Uncle Xiang"
# Email: tuxgis@126.com
# Time: 2020/3/4 19:30
# version: python 

from urllib.request import urlopen
import json


def wgs84tobaidu(x, y):
    data = str(x) + ',' + str(y)
    output = 'json'
    url = 'http://api.map.baidu.com/geoconv/v1/?coords=' + data + '&from=1&to=5&output=' + output + '&ak=ruXEFRLtTaNikRDAprT5hNGdTYjU3cwz'
    req = urlopen(url)
    res = req.read().decode()
    temp = json.loads(res)
    baidu_x = 0
    baidu_y = 0
    if temp['status'] == 0:
        baidu_x = temp['result'][0]['x']
        baidu_y = temp['result'][0]['y']

    return baidu_x, baidu_y

baidu_x, baidu_y = wgs84tobaidu(111.0160537, 24.2794623)
print(baidu_x, baidu_y)