from flask import Flask, request, jsonify
import os
import requests
import json
from dotenv import load_dotenv
from indexPrograms import indexDoc
from kafka import KafkaProducer
import time
from requests.exceptions import ReadTimeout, ConnectionError, RequestException

# Загрузка переменных окружения из .env файла
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=[os.getenv('KAFKA_BROKER_HOST')],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

app = Flask(__name__)

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file, filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def download_file(url, filename, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=60)  # Увеличьте время ожидания до 60 секунд
            if response.status_code == 200:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return filepath
            else:
                raise Exception(f"Failed to download file from {url}, status code: {response.status_code}")
        except (ReadTimeout, ConnectionError) as e:
            if i < retries - 1:
                time.sleep(5)  # Подождите перед повторной попыткой
                continue
            else:
                raise Exception(f"Failed to download file from {url} after {retries} attempts. Error: {e}")
        except RequestException as e:
            raise Exception(f"An error occurred while requesting {url}: {e}")

@app.route("/conditions", methods=['POST'])
def handle_conditions():
    app.logger.debug('Расчет требований для госпрограммы')
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        filepath = save_file(file, filename)
        app.logger.debug('Получен файл. Начало индексации данных')
        try:
            producer.send('getConditionsToProgram', value={"id": request.form['stateProgramId'], "file": filepath})
        except Exception as e:
            app.logger.error(f"Ошибка при отправке задачи в Celery: {e}")
        return jsonify({'message': 'ok'})

    elif 'fileUrl' in request.form:
        url = request.form['fileUrl']
        filename = url.split('/')[-1]
        try:
            filepath = download_file(url, filename)
            producer.send('getConditionsToProgram', value={"id": request.form['stateProgramId'], "file": filepath})
            return jsonify({'message': 'ok'})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    else:
        return jsonify({"error": "No file or URL provided"}), 400

@app.route("/extractData", methods=['POST'])
def handle_extract_data():
    if 'description' in request.json:
        producer.send('getCompanyData', value={"id": request.json['companyId'], "description": request.json['description']})
        return jsonify({'message': 'ok'})

    else:
        return jsonify({"error": "Описание не предоставлено"}), 400
    
@app.route("/chekCondition", methods=['POST'])
def handle_check_condition():
    if 'company' in request.json and 'condition' in request.json:
        producer.send('checkCondition', value={"company": { 'id' : request.json['company']['id'], 'data': request.json['company']['data']}, "condition": { 'id' : request.json['condition']['id'], 'data': request.json['condition']['condition']}})
        return jsonify({'message': 'ok'})

    else:
        return jsonify({"error": "Описание не предоставлено"}), 400


if __name__ == '__main__':
    app.run(debug=True)