import json
import os
from ConditionalsSearchModule import getConditionals
from ConditionalsExistModule import isConditions

from kafka import KafkaConsumer
from dotenv import load_dotenv
import requests

load_dotenv()

consumer = KafkaConsumer(
    'getConditionsToProgram',
    bootstrap_servers=[os.getenv('KAFKA_BROKER_HOST')],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='consumer-1',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    print(message.value)
    data = message.value
    isProgramInfo = isConditions(data['file'])
    conditions = []
    if 'true' in isProgramInfo.lower():
        conditions = getConditionals(data['file'])
    print(conditions)
    requests.post('http://localhost:3000/api/stateProgram/addConditions', json={"programId": data['id'], "conditions":conditions})
    # Отправка результата по нужному адресу, если необходимо