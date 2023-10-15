import pandas as pd
import numpy as np
import calculation_distance as ca
import math
import warnings
warnings.filterwarnings(action='ignore')

apart = pd.read_csv('./data/preprocessed/아파트_위도경도포함.csv', index_col=0)
police = pd.read_csv('./data/preprocessed/경찰서_위도경도포함.csv', encoding='cp949')
hospital = pd.read_csv('./data/preprocessed/병원_위도경도포함.csv', encoding='cp949')
subway = pd.read_csv('./data/preprocessed/지하철_위도경도포함.csv', index_col=0)
school = pd.read_csv('./data/preprocessed/학교_위도경도포함.csv', encoding='cp949')
bus = pd.read_csv('./data/preprocessed/버스정류장_위도경도포함.csv')
naver_apart = pd.read_csv('./data/네이버크롤링_아파트/대구시_아파트.csv', encoding='cp949', index_col=0)
naver_apart.reset_index(drop=True, inplace=True)
price = pd.read_excel('./data/매매가격지수/월간_매매가격지수_아파트.xlsx')

# 인근 학교 서울대, 카이스트 입학자 수
school_loc = ca.data_to_dict(school, '학교명', 'x', 'y')
result_list = []
for i in range(len(apart)):
    lat = apart.iloc[i]['위도']
    lon = apart.iloc[i]['경도']
    _, school_list = ca.calculation_all(lat, lon, 1000, school_loc)
    
    temp = []
    for a in school_list:
        temp.append(int(school.loc[school['학교명'] == a]['주요대학합격자수'].iloc[0]))
    result_list.append(sum(temp))
school_value = pd.DataFrame(result_list, columns=['학교수'])



# 경찰서 유무
police_loc = ca.data_to_dict(police, '경찰서이름', 'y', 'x')
result_list = []
for i in range(len(apart)):
    lat = apart.iloc[i]['위도']
    lon = apart.iloc[i]['경도']
    police_count, _ = ca.calculation_all(lat, lon, 1000, police_loc)
    if police_count > 0:
        result_list.append(1)
    elif police_count == 0:
        result_list.append(0)
    else:
        result_list.append(999)
police_value = pd.DataFrame(result_list, columns=['경찰서유무'])



# 병원 수
hospital_1 = hospital[hospital['종별'].isin(['치과의원', '치과병원', '한의원', '한방병원', '의원'])].reset_index(drop=True)
hospital_2 = hospital[hospital['종별'].isin(['요양병원'])].reset_index(drop=True)

hospital_1_loc = ca.data_to_dict(hospital_1, '명칭', 'y', 'x')
hospital_2_loc = ca.data_to_dict(hospital_2, '명칭', 'y', 'x')

result_list_1 = []
result_list_2 = []
for i in range(len(apart)):
    lat = apart.iloc[i]['위도']
    lon = apart.iloc[i]['경도']
    hospital_1_count, _ = ca.calculation_all(lat, lon, 500, hospital_1_loc)
    hospital_2_count, _ = ca.calculation_all(lat, lon, 500, hospital_2_loc)

    result_list_1.append(hospital_1_count)

    if hospital_2_count > 0:
        result_list_2.append(1)
    elif hospital_2_count == 0:
        result_list_2.append(0)
    else:
        result_list_2.append(999)
clinic_value = pd.DataFrame(result_list_1, columns=['의원수'])
nursing_value = pd.DataFrame(result_list_2, columns=['요양병원유무'])



# 지하철 유무 [0 - 역세권아님 / 1 - 간접역세권 / 2 - 직접역세권]
subway_loc = ca.data_to_dict(subway, '역명')
result_list = []
for i in range(len(apart)):
    lat = apart.iloc[i]['위도']
    lon = apart.iloc[i]['경도']
    
    subway_direct, _ = ca.calculation_all(lat, lon, 500, subway_loc)
    subway_indirect, _ = ca.calculation_all(lat, lon, 1500, subway_loc)
    subway_indirect = subway_indirect - subway_direct
    
    if subway_direct > 0:
        result_list.append(2)
    elif subway_direct == 0:
        if subway_indirect > 0:
            result_list.append(1)
        elif subway_indirect == 0:
            result_list.append(0)
    else:
        result_list.append(999)
subway_value = pd.DataFrame(result_list, columns=['역세권'])



# 버스정류장 수
bus_loc = ca.data_to_dict(bus, '정류장명')
result_list = []
for i in range(len(apart)):
    lat = apart.iloc[i]['위도']
    lon = apart.iloc[i]['경도']
    
    bus_count, _ = ca.calculation_all(lat, lon, 500, bus_loc)
    result_list.append(bus_count)
bus_value = pd.DataFrame(result_list, columns=['버스정류장수'])



# 네이버 크롤링
def to_floor(a):
    return round(a)
result_list = []
for a in range(len(apart)):
    splited_value = apart['시군구+도로명'][a].split(' ')
    splited_value[0] = splited_value[0][:2] + splited_value[0][4]
    apart_value = ' '.join((splited_value[:2] + splited_value[3:]))
    naver_compare = naver_apart.loc[naver_apart['도로명주소'] == apart_value]
    naver_compare['전용면적'] = naver_compare['전용면적'].apply(to_floor)
    naver_compare = naver_compare.loc[naver_compare['전용면적'] == round(apart['전용면적(㎡)'][a])]
    naver_compare.reset_index(drop=True, inplace=True)
    try:
        result_list.append(naver_compare[['세대수', '주차대수', '욕실수', '방수', '최고층', '건설사']].iloc[0].tolist())
    except:
        result_list.append(['도로명주소 매칭불가'])
naver_value = pd.DataFrame(result_list, columns=['세대수', '주차대수', '욕실수', '방수', '최고층', '건설사'])



# 데이터 합치기
final_data = pd.concat([apart, subway_value, clinic_value, nursing_value, police_value, school_value, bus_value, naver_value], axis=1)

# 기타 전처리
def road_address(a):
    splited_value = a.split(' ')
    return ' '.join((splited_value[:2] + splited_value[3:]))
final_data['시군구+도로명'] = final_data['시군구+도로명'].apply(road_address)

drop_index = final_data.loc[final_data['위도'] == 0].index
final_data = final_data.drop(drop_index).reset_index(drop=True)
drop_index = final_data.loc[final_data['세대수'] == '도로명주소 매칭불가'].index
final_data = final_data.drop(drop_index).reset_index(drop=True)
use_columns = ['시군구+도로명', '단지명', '전용면적(㎡)', '계약년월', '계약일', '거래금액(만원)',
                '건축년도', '계약년월일', '경도', '위도', '역세권', '의원수', '요양병원유무', '경찰서유무',
                '학교수', '버스정류장수', '세대수', '주차대수', '욕실수', '방수', '최고층', '건설사']
final_data = final_data[use_columns]
final_data['건축년도'].loc[final_data['건축년도'].isnull()] = 2021
final_data['건설사'] = final_data['건설사'].fillna('Null')

def construction(a):
    temp_list = ['삼성물산', '현대건설', '대림', '포스코', '지에스', '대우건설', '롯데건설', '디엘', '호반', '현대산업']
    compare_list = []
    for i in temp_list:
        if i in a:
            compare_list.append(1)
        else:
            compare_list.append(0)
    compare_value = sum(compare_list)
    if compare_value > 0:
        return 1
    else:
        return 0
final_data['건설사'] = final_data['건설사'].apply(construction)

def get_address(a):
    a = a.split(' ')
    return a[1]
final_data['시군구'] = final_data['시군구+도로명'].apply(get_address)

def change_date_format(a):
    a = a[:4] + a[6:8]
    return int(a)
price['시간'] = price['시간'].apply(change_date_format)

result_list = []
for i in range(len(final_data)):
    temp_date = final_data.iloc[i]['계약년월']
    temp_city = final_data.iloc[i]['시군구']
    temp_value = price[temp_city].loc[price['시간'] == temp_date].values[0]
    result_list.append(round(temp_value, 3))
final_data['매매물가지수'] = pd.DataFrame(result_list)

final_data.to_csv('./data/최종통합본/dataset.csv')