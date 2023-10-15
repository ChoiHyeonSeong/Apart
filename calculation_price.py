import pandas as pd
import numpy as np
import os
import math

file_list = os.listdir('./data/국토교통부_아파트실거래가')
file_list
file_path = []
for i in file_list:
    file_path.append('./data/국토교통부_아파트실거래가/' + i)

apart_data_list = [pd.read_csv(i, encoding='cp949', engine='python', skiprows=15) for i in file_path]
apart = pd.concat([apart_data_list[i] for i in range(len(apart_data_list))]).reset_index(drop=True)

price = pd.read_excel('./data/월간_매매가격지수_아파트.xlsx')

def change_date_format(a):
    a = a[:4] + a[6:8]
    return int(a)

def get_city(a):
    a = a.split(' ')
    a = a[1]
    return a

price['시간'] = price['시간'].apply(change_date_format)
apart['시군구_new'] = apart['시군구'].apply(get_city) 
apart = apart.loc[apart['계약년월'] >= 201801].reset_index(drop=True)

result_list = []
for i in range(len(apart)):
    temp_date = apart.iloc[i]['계약년월']
    temp_city = apart.iloc[i]['시군구_new']
    temp_value = price[temp_city].loc[price['시간'] == temp_date].values[0]
    result_list.append(temp_value)

apart['매매물가지수'] = pd.DataFrame(result_list)

def delete_comma(a):
    a = a.replace(',', '')
    return int(a)
apart['거래금액(만원)'] = apart['거래금액(만원)'].apply(delete_comma)

def index_value_round(a):
    a = round(a, 2)
    return a
apart['매매물가지수'] = apart['매매물가지수'].apply(index_value_round)

unique_list = list(apart['단지명'].unique())
temp_list = []
for i in unique_list:
    try:
        temp = apart.loc[apart['단지명'] == i]
        unique_temp = list(temp['전용면적(㎡)'].unique())
        for a in unique_temp:
            temp = temp.loc[temp['전용면적(㎡)'] == a]
            temp = temp.groupby('계약년월')[['거래금액(만원)', '매매물가지수']].mean().reset_index()
            temp = temp.sort_values('계약년월', ascending=False).reset_index(drop=True)
            value_1_1 = temp.iloc[0]['매매물가지수']
            value_1_2 = temp.iloc[0]['거래금액(만원)'] 
            value_2_1 = temp.iloc[1]['매매물가지수'] 
            value_2_2 = temp.iloc[1]['거래금액(만원)']
            index_value = value_2_1 - value_1_1 
            price_value = value_2_2 - value_1_2
            temp_1 = 0.01 / index_value
            temp_2 = price_value * temp_1
            if temp_2 != 0:
                if temp_2 != math.nan:
                    temp_list.append(temp_2)
    except:
        continue
math.nan
total_value = sum(temp_list)/len(temp_list)
total_value
temp_list
print(total_value)
# 아파트매매물가지수 0.01 당 0.28원 