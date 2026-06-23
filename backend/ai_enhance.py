import io
import os
import httpx
from PIL import Image

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY", "")


async def enhance_with_ai(image: Image.Image) -> Image.Image:
    """
    If no API key is configured, this safely returns the image unchanged
    instead of crashing the request. Drop your key into the STABILITY_API_KEY
    env var on Render (or .env locally) to activate this step -- no code
    changes needed.
    """
    if not STABILITY_API_KEY:
        return image

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.stability.ai/v2beta/stable-image/control/style",
                headers={"authorization": f"Bearer {STABILITY_API_KEY}"},
                files={"image": ("input.png", buf, "image/png")},
                data={
                    "prompt": "minecraft voxel block art style, sharp pixel edges, game texture, vibrant blocky shading",
                    "negative_prompt": "blurry, smooth gradients, realistic photo",
                    "fidelity": 0.4,
                    "output_format": "png",
                },
            )
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
    except Exception as e:
        # Fail gracefully -- return the pixelated base image rather than erroring out
        print(f"AI enhancement failed, returning base pixelated image: {e}")
        return image
