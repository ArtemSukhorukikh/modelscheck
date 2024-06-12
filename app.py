from flask import Flask
import os
from flask import request
from flask import jsonify
import requests
from indexPrograms import indexDoc

app = Flask(__name__)

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file, filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filepath
    else:
        raise Exception(f"Failed to download file from {url}")

@app.route("/conditions", methods=['POST'])
def handle_conditions():
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        filepath = save_file(file, filename)
        response = indexDoc(filepath)
        return jsonify({'conditions': response})
        # return jsonify({"message": "File uploaded successfully", "filepath": filepath})

    elif 'url' in request.json:
        url = request.json['url']
        filename = url.split('/')[-1]
        try:
            filepath = download_file(url, filename)
            response = indexDoc(filepath)
            return jsonify({'conditions': response})
            # return jsonify({"message": "File downloaded successfully", "filepath": filepath})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    else:
        return jsonify({"error": "No file or URL provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)