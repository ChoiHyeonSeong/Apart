import csv
import requests
import pandas as pd
import time

url = 'http://api.vworld.kr/req/address?'
params = 'service=address&request=getcoord&version=2.0&crs=epsg:4326&refine=true&simple=false&format=json&type='
road_type = 'ROAD'  # 도로명 주소
address_param = '&address='
keys_param = '&key='
primary_key = '3501CCAA-42B7-3454-9287-D27D77E1EE32'

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

df = pd.read_csv('input.csv', encoding='cp949')

with open('input.csv', 'r', encoding='cp949') as input_file, open('output.csv', 'w', newline='') as output_file:
    reader = csv.DictReader(input_file)
    headers = reader.fieldnames + ['x', 'y']  # Add 'x' and 'y' as new headers
    writer = csv.DictWriter(output_file, fieldnames=headers)
    writer.writeheader()

    for row in reader:
        address = row['도로명주소']  # Replace '주소' with the actual column name from your CSV file
        if isinstance(address, str):  # Check if address is a string
            x, y = request_geo(address)
            row['x'] = x
            row['y'] = y
        writer.writerow(row)
        print(row)

print("CSV file processing complete.")