import math
from haversine import haversine
import pandas as pd
import numpy as np
import os

# ----------------------------------

def cal_latitude(meter):
    lat1_dis2km = round(6371 * 1 * (math.pi / 180),3) # 지구반지름 * 위도 1도 * 라디안
    lat1_dis2meter = lat1_dis2km * 1000 # 미터화
    result = meter / lat1_dis2meter
    return round(result, 5)

def cal_longitude(meter, latitude):
    lon1_dis2km = round(6371 * 1 * math.cos(latitude) * (math.pi / 180), 3) # 지구반지름 * 경도 1도 * cos(위도) * 라디안
    lon1_dis2meter = lon1_dis2km * 1000
    result = meter / lon1_dis2meter
    return round(result, 5)

def cal_lat_lon(input_lat, input_lon, meter):
    a = cal_latitude(meter)
    b = cal_longitude(meter, input_lat)
    lat_1 = input_lat - a
    lat_2 = input_lat + a
    lon_1 = input_lon - b
    lon_2 = input_lon + b
    
    temp_list_1 = []
    temp_list_2 = []
    if lat_1 > lat_2:
        temp_list_1.append(lat_2)
        temp_list_1.append(lat_1)
    elif lat_1 < lat_2:
        temp_list_1.append(lat_1)
        temp_list_1.append(lat_2)

    if lon_1 > lon_2:
        temp_list_2.append(lon_2)
        temp_list_2.append(lon_1)
    elif lon_1 < lon_2:
        temp_list_2.append(lon_1)
        temp_list_2.append(lon_2)

    result = {'lat' : temp_list_1, 'lon' : temp_list_2}
    return result

def get_dict(input_lat, input_lon, meter, check_dict):
    dict_min_max = cal_lat_lon(input_lat, input_lon, meter)
    temp_dict = {}
    key_list = list(check_dict.keys())
    for a in key_list:
        if check_dict[a][0] >= dict_min_max['lat'][0]:
            if check_dict[a][0] <= dict_min_max['lat'][1]:
                if check_dict[a][1] >= dict_min_max['lon'][0]:
                    if check_dict[a][1] <= dict_min_max['lon'][1]:
                        temp_dict[a] = [check_dict[a][0], check_dict[a][1]]
    return temp_dict

def count_distance(input_lat, input_lon, meter, check_dict):
    marker = (input_lat, input_lon)
    temp_list = []
    temp_list_2 = []
    key_list = list(check_dict.keys())
    for a in key_list:
        check_marker = (check_dict[a][0], check_dict[a][1])
        distance = haversine(marker, check_marker) * 1000
        if distance <= meter:
            temp_list.append(check_dict[a])
            temp_list_2.append(a)
    result = len(temp_list)
    return result, temp_list_2

def calculation_all(lat, lon, meter, check_dict):
    temp = get_dict(lat, lon, meter, check_dict)
    count, name_list = count_distance(lat, lon, meter, temp)
    return count, name_list

# ----------------------------------

def data_to_dict(data, id_col, lat='위도', lon='경도'):
    temp_dict = {}
    for i in data[id_col]:
        temp_dict[i] = [data.loc[data[id_col] == i][lat].values[0], data.loc[data[id_col] == i][lon].values[0]]
    return temp_dict