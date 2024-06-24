import json
import os
from companyDataExtract import getCompanyDataJson

from kafka import KafkaConsumer
from dotenv import load_dotenv
import requests
import json
import re

import warnings
warnings.filterwarnings('ignore')

load_dotenv()

consumer = KafkaConsumer(
    'getCompanyData',
    bootstrap_servers=[os.getenv('KAFKA_BROKER_HOST')],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='consumer-1',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    print(message.value)
    data = message.value
    extractData = getCompanyDataJson(data['description'])
    print(extractData)
    try:
        jsonData = json.loads(extractData)
    except:
        jsonData = {}
    requests.post('http://localhost:3000/api/company/addExtractData', json={"companyId": data['id'], "data":jsonData})
    # Отправка результата по нужному адресу, если необходимо