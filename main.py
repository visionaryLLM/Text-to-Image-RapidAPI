import os
from flask import Flask, jsonify, request
from gradio_client import Client

app = Flask(__name__)

GRADIO_URL = "https://playgroundai-playground-v2-5.hf.space/--replicas/bdj8s/"

def check_range(param, min_val, max_val):
    return min_val <= param <= max_val

def get_missing_params(params):
    missing_params = []
    if not params.get('prompt'):
        missing_params.append("prompt")
    if not params.get('negative'):
        missing_params.append("negative")
    return missing_params

def fix_param_range(param, min_val, max_val):
    if param < min_val:
        return f"Value should be greater than or equal to {min_val}"
    elif param > max_val:
        return f"Value should be less than or equal to {max_val}"
    else:
        return None

@app.route('/generate', methods=['GET'])
def generate_image():
    try:
        params = {
            'prompt': request.args.get('prompt'),
            'negative': request.args.get('negative'),
            'useNegative': request.args.get('useNegative'),
            'seed': request.args.get('seed'),
            'width': request.args.get('width'),
            'height': request.args.get('height'),
            'scale': request.args.get('scale'),
            'randomSeed': request.args.get('randomSeed')
        }

        missing_params = get_missing_params(params)
        if missing_params:
            return jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}), 400

        seed = float(params['seed']) if params['seed'] is not None else None
        width = int(params['width']) if params['width'] is not None else None
        height = int(params['height']) if params['height'] is not None else None
        scale = float(params['scale']) if params['scale'] is not None else None
        use_negative = params['useNegative'].lower() == 'true' if params['useNegative'] is not None else None
        random_seed = params['randomSeed'].lower() == 'true' if params['randomSeed'] is not None else None

        errors = {}
        if (seed is not None):
            error = fix_param_range(seed, 0, 2147483647)
            if error:
                errors['seed'] = error

        if (width is not None):
            error = fix_param_range(width, 256, 1536)
            if error:
                errors['width'] = error

        if (height is not None):
            error = fix_param_range(height, 256, 1536)
            if error:
                errors['height'] = error

        if (scale is not None):
            error = fix_param_range(scale, 0.1, 20)
            if error:
                errors['scale'] = error

        if errors:
            return jsonify({"error": "Parameter out of range", "details": errors}), 400

        if GRADIO_URL is None or not GRADIO_URL.startswith('http'):
            return jsonify({"error": "Invalid Gradio URL"}), 500

        client = Client(GRADIO_URL)
        result = client.predict(params['prompt'], params['negative'], use_negative, seed, width, height, scale, random_seed, api_name="/run")

        if isinstance(result, tuple) and len(result) == 2:
            if isinstance(result[0], str):
                images = [{"image": result[0], "caption": None}]
            else:
                images = result[0]
            seed = result[1]
        else:
            return jsonify({"error": "Unexpected result format"}), 500

        image_url = "https://playgroundai-playground-v2-5.hf.space/--replicas/bdj8s/file=" + images[0]["image"]

        return jsonify({"imgURL": image_url, "seed": seed}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error: " + str(e)}), 500

@app.route('/')
def home():
    return '🤷🏻‍♂️'

if __name__ == '__main__':
    app.run(debug=True)
