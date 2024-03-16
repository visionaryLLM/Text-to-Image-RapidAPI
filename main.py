import os
import requests
from flask import Flask, jsonify, request
from gradio_client import Client

app = Flask(__name__)

GRADIO_URL = os.environ.get('GRADIO_URL')
FREEIMAGE_API_KEY = os.environ.get('FREEIMAGE_API_KEY')
FREEIMAGE_HOST_API_URL = "http://freeimage.host/api/1/upload/"

# Helper function to check if parameter is within range
def check_range(param, min_val, max_val):
    return min_val <= param <= max_val

@app.route('/generate', methods=['GET'])
def generate_and_upload_image():
    try:
        prompt = request.args.get('prompt')
        negative = request.args.get('negative')
        use_negative = bool(request.args.get('useNegative'))
        seed = int(request.args.get('seed'))
        width = int(request.args.get('width'))
        height = int(request.args.get('height'))
        scale = float(request.args.get('scale'))
        random_seed = bool(request.args.get('randomSeed'))

        if not (prompt and negative):
            return jsonify({"error": "Prompt and negative parameters are required"}), 400

        if not check_range(seed, 0, 2147483647) or not check_range(width, 256, 1536) or \
           not check_range(height, 256, 1536) or not check_range(scale, 0.1, 20):
            return jsonify({"error": "Parameter out of range"}), 400

        client = Client(GRADIO_URL)
        result = client.predict(prompt, negative, use_negative, seed, width, height, scale, random_seed, api_name="/run")

        image_url = GRADIO_URL + result['url']

        # Upload image to freeimage.host
        response = requests.get(FREEIMAGE_HOST_API_URL, params={'key': FREEIMAGE_API_KEY, 'source': image_url, 'format': 'json'})

        # Parse the response
        response_json = response.json()
        if response_json.get("status_code") == 200:
            uploaded_image_url = response_json["image"]["url"]
            return jsonify({"uploaded_image_url": uploaded_image_url}), 200
        else:
            return jsonify({"error": "Failed to upload image"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🤷🏻‍♂️'

if __name__ == '__main__':
    app.run(debug=True)
