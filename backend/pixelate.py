from PIL import Image, ImageEnhance
import numpy as np

# Optional curated palette -- kept for anyone who wants the literal "limited Minecraft
# block colors" look later, but it is OFF by default because it destroys most of the
# original photo's color information.
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
    use_custom_palette: bool = False,
    palette_colors: int = 48,
    contrast_boost: float = 1.1,
    saturation_boost: float = 1.15,
) -> Image.Image:
    image = image.convert("RGB")
    original_size = image.size

    # Mild punch-up only -- enough to read as "stylized", not enough to wash out detail
    image = ImageEnhance.Contrast(image).enhance(contrast_boost)
    image = ImageEnhance.Color(image).enhance(saturation_boost)

    # Downscale with a high-quality filter first so each block represents a clean
    # average of that region (instead of NEAREST picking one random source pixel,
    # which is what caused the "confetti" look).
    small_size = (
        max(1, original_size[0] // block_size),
        max(1, original_size[1] // block_size),
    )
    small = image.resize(small_size, resample=Image.BOX)

    if use_custom_palette:
        pal_img = build_palette_image(MINECRAFT_PALETTE)
        small = small.quantize(palette=pal_img, dither=Image.NONE).convert("RGB")
    else:
        # A generous adaptive palette keeps the photo recognizable while still
        # giving that "limited color" game-art feel.
        small = small.convert("P", palette=Image.ADAPTIVE, colors=palette_colors, dither=Image.NONE).convert("RGB")

    # Upscale back with NEAREST -- this is what gives the hard, crisp block edges.
    result = small.resize(original_size, resample=Image.NEAREST)
    return result


def add_block_shading(image: Image.Image, block_size: int, intensity: float = 0.04) -> Image.Image:
    """Very subtle per-block brightness variance so blocks don't look perfectly flat.
    Kept low-intensity on purpose -- too much turns into visual noise."""
    arr = np.array(image).astype(np.float32)
    h, w, _ = arr.shape
    rng = np.random.default_rng(42)

    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            shade = rng.uniform(1 - intensity, 1 + intensity)
            arr[y:y + block_size, x:x + block_size] *= shade

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def full_pipeline(
    image: Image.Image,
    block_size: int = 16,
    use_custom_palette: bool = False,
) -> Image.Image:
    img = pixelate_minecraft(image, block_size=block_size, use_custom_palette=use_custom_palette)
    img = add_block_shading(img, block_size=block_size, intensity=0.04)
    return img
