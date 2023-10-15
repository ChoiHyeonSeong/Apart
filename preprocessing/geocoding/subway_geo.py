import csv
import requests
import pandas as pd
import time

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

# ----------------------------------

df = pd.read_csv('./data/국토교통부_아파트실거래가/apart_preprocessed.csv', encoding='utf-8')

temp_dict = {}
for i in df['시군구+도로명'].unique():
    x, y = request_geo(i)
    temp_list = [x, y]
    temp_dict[i] = temp_list

temp_list = []
for i in df['시군구+도로명']:
    temp_list.append(temp_dict[i])

df_preprocessed = pd.concat([df, pd.DataFrame(temp_list, columns=['경도', '위도'])], axis=1)

df_preprocessed.to_csv('./data/국토교통부_아파트실거래가/apart_geocoding.csv')

# ----------------------------------

subway = pd.read_csv('./data/지하철/국가철도공단_대구_지하철_주소데이터_20220916.csv', encoding='cp949')

temp_dict = {}
for i in subway['도로명주소'].unique():
    x, y = request_geo(i)
    temp_list = [x, y]
    temp_dict[i] = temp_list

temp_list = []
for i in subway['도로명주소']:
    temp_list.append(temp_dict[i])

subway_preprocessed = pd.concat([subway, pd.DataFrame(temp_list, columns=['경도', '위도'])], axis=1)

subway_preprocessed.to_csv('./data/지하철/subway_geocoding.csv')

# ----------------------------------

police = pd.read_csv('./data/경찰서/경찰청_경찰관서 위치 주소 현황_20220831.csv', encoding='cp949')
police = police.loc[police['지방청'] == '대구청'].reset_index(drop=True)

temp_dict = {}
for i in police['경찰_주소'].unique():
    x, y = request_geo(i)
    temp_list = [x, y]
    temp_dict[i] = temp_list

temp_list = []
for i in police['경찰_주소']:
    temp_list.append(temp_dict[i])

police_preprocessed = pd.concat([police, pd.DataFrame(temp_list, columns=['경도', '위도'])], axis=1)

police_preprocessed.to_csv('./data/경찰서/police_geocoding.csv')

# ----------------------------------

hospital = pd.read_excel('./data/의료기관/의료기관.xls')