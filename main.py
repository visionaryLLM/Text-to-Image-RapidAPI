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
        use_negative = request.args.get('useNegative')
        seed = request.args.get('seed')
        width = request.args.get('width')
        height = request.args.get('height')
        scale = request.args.get('scale')
        random_seed = request.args.get('randomSeed')

        if not (prompt and negative):
            return jsonify({"error": "Prompt and negative parameters are required"}), 400

        # Convert parameters to appropriate types, handling None values
        seed = int(seed) if seed is not None else None
        width = int(width) if width is not None else None
        height = int(height) if height is not None else None
        scale = float(scale) if scale is not None else None
        use_negative = use_negative.lower() == 'true' if use_negative is not None else None
        random_seed = random_seed.lower() == 'true' if random_seed is not None else None

        # Check parameter ranges
        if (seed is not None and not check_range(seed, 0, 2147483647)) or \
           (width is not None and not check_range(width, 256, 1536)) or \
           (height is not None and not check_range(height, 256, 1536)) or \
           (scale is not None and not check_range(scale, 0.1, 20)):
            return jsonify({"error": "Parameter out of range"}), 400

        # Check if GRADIO_URL is valid
        if GRADIO_URL is None or not GRADIO_URL.startswith('http'):
            return jsonify({"error": "Invalid Gradio URL"}), 500

        client = Client(GRADIO_URL)
        result = client.predict(prompt, negative, use_negative, seed, width, height, scale, random_seed, api_name="/run")

        image_url = GRADIO_URL + result['url']

        # Upload image to freeimage.host
        if image_url is not None:
            response = requests.get(FREEIMAGE_HOST_API_URL, params={'key': FREEIMAGE_API_KEY, 'source': image_url, 'format': 'json'})

            # Parse the response
            response_json = response.json()
            if response_json.get("status_code") == 200:
                img_url = response_json["image"]["url"]
                return jsonify({"imgURL": img_url}), 200
            else:
                return jsonify({"error": "Failed to upload image"}), 500
        else:
            return jsonify({"error": "Image URL is None"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🤷🏻‍♂️'

if __name__ == '__main__':
    app.run(debug=True)
