from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

MINECRAFT_PALETTE = [
    (63, 53, 46), (94, 73, 51), (122, 97, 62),
    (90, 130, 50), (60, 110, 40), (40, 80, 30),
    (130, 130, 130), (160, 160, 160), (90, 90, 90),
    (200, 180, 130), (230, 215, 170),
    (40, 70, 160), (70, 110, 200),
    (20, 20, 20), (245, 245, 245),
]


def build_palette_image(colors):
    pal_img = Image.new("P", (1, 1))
    flat = []
    for c in colors:
        flat.extend(c)
    flat += flat[:3] * ((768 - len(flat)) // 3)
    pal_img.putpalette(flat[:768])
    return pal_img


def pixelate_minecraft(
    image: Image.Image,
    block_size: int = 16,
    use_custom_palette: bool = True,
    contrast_boost: float = 1.15,
    saturation_boost: float = 1.2,
) -> Image.Image:
    image = image.convert("RGB")
    original_size = image.size

    image = ImageEnhance.Contrast(image).enhance(contrast_boost)
    image = ImageEnhance.Color(image).enhance(saturation_boost)
    image = image.filter(ImageFilter.GaussianBlur(radius=1))

    small_size = (
        max(1, original_size[0] // block_size),
        max(1, original_size[1] // block_size),
    )
    small = image.resize(small_size, resample=Image.NEAREST)

    if use_custom_palette:
        pal_img = build_palette_image(MINECRAFT_PALETTE)
        small = small.quantize(palette=pal_img, dither=Image.NONE).convert("RGB")
    else:
        small = small.convert("P", palette=Image.ADAPTIVE, colors=32, dither=Image.NONE).convert("RGB")

    result = small.resize(original_size, resample=Image.NEAREST)
    return result


def add_block_shading(image: Image.Image, block_size: int) -> Image.Image:
    arr = np.array(image).astype(np.float32)
    h, w, _ = arr.shape
    rng = np.random.default_rng(42)

    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            shade = rng.uniform(0.92, 1.08)
            arr[y:y + block_size, x:x + block_size] *= shade

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def full_pipeline(image: Image.Image, block_size: int = 16, use_custom_palette: bool = True) -> Image.Image:
    img = pixelate_minecraft(image, block_size=block_size, use_custom_palette=use_custom_palette)
    img = add_block_shading(img, block_size=block_size)
    return img
