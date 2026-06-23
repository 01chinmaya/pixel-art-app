import base64
import io
import os
import httpx
from PIL import Image

STABILITY_API_KEY = os.environ.get("STABILITY_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_MODEL = "gemini-2.5-flash-image"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

ENHANCE_PROMPT = (
    "Restyle this pixel art image to look like an authentic Minecraft voxel "
    "render: blocky cube textures, ambient occlusion shading on each block face, "
    "game-engine lighting. Preserve the exact composition, layout, and colors -- "
    "do not add or remove objects, do not change the scene."
)


async def _enhance_with_gemini(image: Image.Image) -> Image.Image:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")

    payload = {
        "contents": [{
            "parts": [
                {"text": ENHANCE_PROMPT},
                {"inline_data": {"mime_type": "image/png", "data": b64_image}},
            ]
        }]
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    for part in data["candidates"][0]["content"]["parts"]:
        if "inline_data" in part or "inlineData" in part:
            inline = part.get("inline_data") or part.get("inlineData")
            img_bytes = base64.b64decode(inline["data"])
            return Image.open(io.BytesIO(img_bytes))

    raise ValueError("Gemini response did not contain an image")


async def _enhance_with_stability(image: Image.Image) -> Image.Image:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

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


async def enhance_with_ai(image: Image.Image) -> Image.Image:
    """
    Tries Gemini first (free tier), falls back to Stability AI if a key is set,
    and falls back to returning the image unchanged if neither is configured
    or both fail. This keeps the app working with zero cost by default.
    """
    if GEMINI_API_KEY:
        try:
            return await _enhance_with_gemini(image)
        except Exception as e:
            print(f"Gemini enhancement failed, trying Stability fallback: {e}")

    if STABILITY_API_KEY:
        try:
            return await _enhance_with_stability(image)
        except Exception as e:
            print(f"Stability enhancement failed, returning base image: {e}")

    return image
