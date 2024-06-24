import json
import os
from companyCombineConditions import getCompanyCombineCondition

from kafka import KafkaConsumer
from dotenv import load_dotenv
import requests

import warnings
warnings.filterwarnings('ignore')

load_dotenv()

consumer = KafkaConsumer(
    'checkCondition',
    bootstrap_servers=[os.getenv('KAFKA_BROKER_HOST')],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='consumer-1',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    # print(message.value)
    data = message.value
    try:
        answear = getCompanyCombineCondition(data['company']['data'], data['condition']['data'])
        print(answear)
        if 'true' in answear.lower():
            requests.post('http://localhost:3000/api/company/addCondition', json={"companyId": data['company']['id'], "conditionId":data['condition']['id']})
    except: 
        continue

    
    # Отправка результата по нужному адресу, если необходимо