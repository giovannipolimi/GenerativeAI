'''
# 0. Load Libraries
import requests
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
# 1. Define token & Headers

# TODO: migrate to vault
with open('/home/g.palazzo/api_config/access_token.json') as f:
    acces_json = json.load(f)
    ACCESS_TOKEN = acces_json['token']
    CLIENT_ID = acces_json['CLIENT_ID']
    CLIENT_SECRET = acces_json['CLIENT_SECRET']
    JWT_URL = acces_json['JWT_URL']

# We can use this URL to get our global company id
DISCOVERY_URL = 'https://analytics.adobe.io/discovery/me'
DISCOVERY_HEADER = {
    'Accept':'application/json',
    'Authorization':f'Bearer {ACCESS_TOKEN}',
    'x-api-key':f'{CLIENT_ID}',
}

# Reset proxies
for i in ['https_proxy', 'http_proxy', 'proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    if i in os.environ:
        print(f'removing {i}')
        del os.environ[i]

# TODO: migrate to vault
vault_path = '/home/g.palazzo/UNIPOL-Digital-Lab/.config/vault'
load_dotenv(vault_path)
proxy_servers = {
   'http': os.getenv("proxy"),
   'https': os.getenv("proxy")
}

response1 = requests.get(url=DISCOVERY_URL, headers=DISCOVERY_HEADER, proxies=proxy_servers, verify=False)
# 1.1 Get Company ID:
GLOBAL_COMPANY_ID = response1.json()['imsOrgs'][0]['companies'][0]['globalCompanyId']
# 1.2 Define Base URL
DISCOVERY_HEADER['x-proxy-global-company-id'] = GLOBAL_COMPANY_ID
# all of the reports stem from this URL
BASE_URL = f'https://analytics.adobe.io/api/{GLOBAL_COMPANY_ID}/'
# find URLs to use here: https://adobedocs.github.io/analytics-2.0-apis/#/

# TODO: manage
REPORT_SUITE_NAME = 'unipolsai.app.prod'

FIND_RSID_URL = BASE_URL + 'collections/suites' + f'?rsids={REPORT_SUITE_NAME}'

response2 = requests.get(url=FIND_RSID_URL, headers=DISCOVERY_HEADER, proxies=proxy_servers, verify=False)
RSID = response2.json()['content'][0]['rsid']

# 2.1 Get segments
# Change the search word to browse segments we might want to use
# TODO: manage
FIND_SEGMENT = 'APP - Utenti che hanno rinnovato la polizza online'
FIND_SEGMENT = FIND_SEGMENT.replace(" ", "%20")

EXPANSION = 'reportSuiteName,ownerFullName,definition'

DISCOVERY_URL = BASE_URL + 'segments' + f'?rsids={RSID}' + f'&name={FIND_SEGMENT}&filterByPublishedSegments=all&expansion={EXPANSION}&includeType=all'

response4 = requests.get(url=DISCOVERY_URL, headers=DISCOVERY_HEADER, proxies=proxy_servers, verify=False)
json_object = json.dumps(response4.json()['content'][0], indent = 1)

SEGMENT_ID = response4.json()['content'][0]['id']
# 2.2 Get Dimensions
DISCOVERY_URL = BASE_URL + 'dimensions' + f'?rsid={RSID}'
response5 = requests.get(url=DISCOVERY_URL, headers=DISCOVERY_HEADER, proxies=proxy_servers, verify=False)

# Change the search word to browse dimensions we might want to use
# TODO: manage
DIM_SEARCH_WORD = 'CRM ID'

df_dims= pd.DataFrame(response5.json())

DIM = df_dims[df_dims['name'].str.contains(DIM_SEARCH_WORD, case=False)]['id'].values[0]

df_dims[df_dims['name'].str.contains(DIM_SEARCH_WORD, case=False)]
# 2.3 Get Metrics
DISCOVERY_URL = BASE_URL + 'metrics' + f'?rsid={RSID}'
response6 = requests.get(url=DISCOVERY_URL, headers=DISCOVERY_HEADER, proxies=proxy_servers, verify=False)

# Change the search word to browse metrics we might want to use
# TODO: manage
MET_SEARCH_WORD = ['Unique Visitors']

df_mets = pd.DataFrame(response6.json())

# - Extract metrics for start and end flows:
METS = df_mets[df_mets['name'].str.contains('event108|event109')]['id']

METS_OBJ = [{'id':x} for x in METS]
# 3. Post
# - defining Post Body
POST_REPORT_URL = BASE_URL + 'reports' + f'?rsid={RSID}'

# TODO: manage
START_DATE = '2022-12-01'
END_DATE = '2023-01-31'
TIME_START = 'T00:00:00.000'
TIME_END = 'T23:59:59.999999'
DATE_RANGE = START_DATE + TIME_START + '/' + END_DATE + TIME_END

# TODO: manage
# with the date range, metrics and dimension in the body
with open("/home/g.palazzo/api_config/report_body.json") as report_body:
   REPORT_BODY = json.loads(report_body)
   
   REPORT_BODY['rsid'] = RSID
   REPORT_BODY['dateRange'] = DATE_RANGE
   REPORT_BODY['metrics'] = METS_OBJ
   REPORT_BODY['segmentId'] = SEGMENT_ID
   REPORT_BODY['dimension'] = DIM


# Init empty dataframe
df_6 = pd.DataFrame(columns=['itemId','value','data'])

# Page incrementer
i = 0
# Row incrementer
nrow = 1

while nrow != 0:
    REPORT_BODY['settings']['page'] = i
    response5 = requests.post(url=POST_REPORT_URL, headers=DISCOVERY_HEADER, json=REPORT_BODY)
    df_tmp = pd.DataFrame(response5.json()['rows'])

    nrow = len(df_tmp)
    print(f"Page {i}: loaded {nrow} rows")
    df_6 = pd.concat([df_6, df_tmp])

    i += 1

# refine dataframe:
# set the column names
df_6.columns = [DIM+'_key',DIM,'data']
# unnest the 'data' column into another dataframe
df5a = pd.DataFrame(df_6['data'].to_list()).reset_index(drop=True)
# set the column names
df5a.columns = METS
# concatenate the two dataframes by the column axis and remove the 'data' column from the raw output
df_final = pd.concat([df_6.iloc[:,:-1].reset_index(drop=True),df5a],axis='columns')
'''