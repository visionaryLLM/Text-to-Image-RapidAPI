# Text to Image v4

## Endpoints

### 1. /generate (GET)
Generate and upload an image using Gradio and Free Image Host APIs.

#### Parameters
- prompt (string): The prompt for generating the image.
- negative (string): The negative prompt for generating the image.
- useNegative (boolean): Whether to use the negative prompt or not.
- seed (integer): Seed for randomization (between 0 and 2147483647).
- width (integer): Width of the generated image (between 256 and 1536).
- height (integer): Height of the generated image (between 256 and 1536).
- scale (float): Guidance scale (between 0.1 and 20).
- randomSeed (boolean): Whether to randomize the seed or not.

#### Sample Request
```
GET /generate?prompt=cat&negative=ugle&useNegative=True&seed=0&width=256&height=256&scale=0.1&randomSeed=True
```

#### Sample Response
```json
{
    "imgURL": "http://freeimage.host/images/2014/06/04/example.png"
}
```

## Parameter Ranges
- `seed`: 0 to 2147483647
- `width`: 256 to 1536
- `height`: 256 to 1536
- `scale`: 0.1 to 20