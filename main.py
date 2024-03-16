from flask import Flask, request, jsonify

from gradio_client import Client

app = Flask(__name__)

@app.route('/imagine', methods=['GET'])
def predict():
    try:
        prompt = request.args.get('prompt')
        negative_prompt = request.args.get('negative_prompt')
        use_negative_prompt = request.args.get('use_negative_prompt')
        seed = request.args.get('seed')
        width = request.args.get('width')
        height = request.args.get('height')
        guidance_scale = request.args.get('guidance_scale')
        randomize_seed = request.args.get('randomize_seed')

        if None in [prompt, negative_prompt, use_negative_prompt, seed, width, height, guidance_scale, randomize_seed]:
            return jsonify({"error": "Incomplete parameters"}), 400

        prompt = str(prompt)
        negative_prompt = str(negative_prompt)
        use_negative_prompt = bool(use_negative_prompt)
        seed = float(seed)
        width = float(width)
        height = float(height)
        guidance_scale = float(guidance_scale)
        randomize_seed = bool(randomize_seed)

        client = Client("https://playgroundai-playground-v2-5.hf.space/--replicas/lohn0/")
        result = client.predict(
            prompt,
            negative_prompt,
            use_negative_prompt,
            seed,
            width,
            height,
            guidance_scale,
            randomize_seed,
            api_name="/run"
        )

        # Sample response structure
        response = {
            "images": result[0],  # List[Dict(image: filepath, caption: str | None)]
            "seed": result[1]  # Seed
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
