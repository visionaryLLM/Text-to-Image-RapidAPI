import os
from flask import Flask, jsonify, request
from gradio_client import Client

app = Flask(__name__)

GRADIO_URL = os.environ.get('GRADIO_URL')

def check_range(param, min_val, max_val):
    return min_val <= param <= max_val

@app.route('/generate', methods=['GET'])
def generate_image():
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

        seed = float(seed) if seed is not None else None
        width = int(width) if width is not None else None
        height = int(height) if height is not None else None
        scale = float(scale) if scale is not None else None
        use_negative = use_negative.lower() == 'true' if use_negative is not None else None
        random_seed = random_seed.lower() == 'true' if random_seed is not None else None

        if (seed is not None and not check_range(seed, 0, 2147483647)) or \
           (width is not None and not check_range(width, 256, 1536)) or \
           (height is not None and not check_range(height, 256, 1536)) or \
           (scale is not None and not check_range(scale, 0.1, 20)):
            return jsonify({"error": "Parameter out of range"}), 400

        if GRADIO_URL is None or not GRADIO_URL.startswith('http'):
            return jsonify({"error": "Invalid Gradio URL"}), 500

        client = Client(GRADIO_URL)
        result = client.predict(prompt, negative, use_negative, seed, width, height, scale, random_seed, api_name="/run")

        if isinstance(result, tuple) and len(result) == 2:
            if isinstance(result[0], str):
                image_url = GRADIO_URL + result[0]
            else:
                return jsonify({"error": "Unexpected result format"}), 500
            seed = result[1]
        else:
            return jsonify({"error": "Unexpected result format"}), 500

        return jsonify({"imgURL": image_url, "seed": seed}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🤷🏻‍♂️'

if __name__ == '__main__':
    app.run(debug=True)
