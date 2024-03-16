import os
from flask import Flask, jsonify, request
from gradio_client import Client

app = Flask(__name__)

BASE_URL = "https://playgroundai-playground-v2-5.hf.space/--replicas/lohn0/file="

def check_range(param, min_val, max_val):
    return min_val <= param <= max_val

@app.route('/generate', methods=['GET'])
def generate_image():
    try:
        prompt = request.args.get('prompt')
        negative = request.args.get('negative')
        use_negative = request.args.get('useNegative', type=bool)
        seed = request.args.get('seed', type=float)
        width = request.args.get('width', type=int)
        height = request.args.get('height', type=int)
        scale = request.args.get('scale', type=float)
        random_seed = request.args.get('randomSeed', type=bool)

        if not (prompt and negative):
            return jsonify({"error": "Prompt and negative parameters are required"}), 400

        if not all(check_range(arg, *limits) for arg, limits in ((seed, (0, 2147483647)), 
                                                                (width, (256, 1536)), 
                                                                (height, (256, 1536)), 
                                                                (scale, (0.1, 20)))):
            return jsonify({"error": "Parameter out of range"}), 400

        client = Client(BASE_URL)
        result = client.predict(prompt, negative, use_negative, seed, width, height, scale, random_seed, api_name="/run")

        if isinstance(result, tuple) and len(result) == 2:
            images = result[0]
            seed = result[1]
            if images:
                image_path = images[0]["image"]
                image_url = f"{BASE_URL}{image_path}"
            else:
                image_url = None

            return jsonify({"imgURL": image_url, "seed": seed}), 200
        else:
            return jsonify({"error": "Unexpected result format"}), 500

    except Exception as e:
        # If an exception occurs, return the raw response content
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return '🤷🏻‍♂️'

if __name__ == '__main__':
    app.run(debug=True)
