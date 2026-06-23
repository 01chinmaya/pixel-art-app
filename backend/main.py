import io
import os

from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image

from pixelate import full_pipeline
from ai_enhance import enhance_with_ai, STABILITY_API_KEY

app = FastAPI()

# Allow the frontend (different Render service/domain) to call this API.
# Restrict this to your actual frontend URL once deployed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "ai_enabled": bool(STABILITY_API_KEY)}


@app.post("/api/pixelate")
async def pixelate(image: UploadFile, use_ai: bool = Form(False), block_size: int = Form(16)):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    block_size = max(4, min(block_size, 64))  # clamp to sane range
    result = full_pipeline(img, block_size=block_size)

    if use_ai:
        result = await enhance_with_ai(result)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
