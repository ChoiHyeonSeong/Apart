import pandas as pd
import numpy as np
import os
import csv
import requests
import pandas as pd
import time

file_list = os.listdir('./data/국토교통부_아파트실거래가')
file_list
file_path = []
for i in file_list:
    file_path.append('./data/국토교통부_아파트실거래가/' + i)

apart_data_list = [pd.read_csv(i, encoding='cp949', engine='python', skiprows=15) for i in file_path]
apart_data = pd.concat([apart_data_list[i] for i in range(len(apart_data_list))]).reset_index(drop=True)

# 주소지 전처리
apart_data['시군구+도로명+면적'] = apart_data['시군구'] + ' ' + apart_data['도로명'] + ' ' + apart_data['전용면적(㎡)'].astype('str')
apart_data['시군구+도로명'] = apart_data['시군구'] + ' ' + apart_data['도로명']

# 계약일 전처리
def day_preprocessing(data):
    if data < 10:
        result = '0' + str(data)
    else:
        result = str(data)
    return result
apart_data['계약일'] = apart_data['계약일'].apply(day_preprocessing)
apart_data['계약년월일'] = (apart_data['계약년월'].astype('str') + apart_data['계약일']).astype('int64')
apart_data['계약일'] = apart_data['계약일'].astype('int64')

# 데이터 정렬
apart_data = apart_data.sort_values(by=['시군구+도로명+면적']).reset_index(drop=True)

# 아파트별 가장 최근 거래기록 추출
index_list = []
for i in apart_data['시군구+도로명+면적'].unique():
    temp_df = apart_data.loc[apart_data['시군구+도로명+면적'] == i]
    index_num = temp_df.loc[temp_df['계약년월일'] == temp_df['계약년월일'].max()].index
    index_list.extend(list(index_num))
apart_data = apart_data.iloc[index_list].reset_index(drop=True)
apart_data
# 지오코딩

url = 'http://api.vworld.kr/req/address?'
params = 'service=address&request=getcoord&version=2.0&crs=epsg:4326&refine=true&simple=false&format=json&type='
road_type = 'ROAD'  # 도로명 주소
address_param = '&address='
keys_param = '&key='
primary_key = 'AC90E7A7-B403-3E7D-8228-F3C0E90A7823'

def request_geo(road):
    page = requests.get(url + params + road_type + address_param + road + keys_param + primary_key)
    json_data = page.json()
    if json_data['response']['status'] == 'OK':
        x = json_data['response']['result']['point']['x']
        y = json_data['response']['result']['point']['y']
        return x, y
    else:
        x = 0
        y = 0
        return x, y

temp_dict = {}
for i in apart_data['시군구+도로명'].unique():
    x, y = request_geo(i)
    temp_list = [x, y]
    temp_dict[i] = temp_list

temp_list = []
for i in apart_data['시군구+도로명']:
    temp_list.append(temp_dict[i])

apart_data_geocoded = pd.concat([apart_data, pd.DataFrame(temp_list, columns=['경도', '위도'])], axis=1)

apart_data_geocoded.to_csv('./data/preprocessed/아파트_위도경도포함.csv')