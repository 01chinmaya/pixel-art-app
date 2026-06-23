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

    image = ImageEnhance.Contrast(image).enhance(contrast_boost)
    image = ImageEnhance.Color(image).enhance(saturation_boost)

    small_size = (
        max(1, original_size[0] // block_size),
        max(1, original_size[1] // block_size),
    )
    # LANCZOS here keeps edges/detail sharper going into the downscale than a plain
    # box average would, which matters once we quantize to a limited palette next.
    small = image.resize(small_size, resample=Image.LANCZOS)

    if use_custom_palette:
        pal_img = build_palette_image(MINECRAFT_PALETTE)
        small = small.quantize(palette=pal_img, dither=Image.NONE).convert("RGB")
    else:
        small = small.convert("P", palette=Image.ADAPTIVE, colors=palette_colors, dither=Image.NONE).convert("RGB")

    result = small.resize(original_size, resample=Image.NEAREST)
    return result


def add_block_bevel(image: Image.Image, block_size: int, highlight: int = 16, shadow: int = 16) -> Image.Image:
    """
    Adds a subtle highlight on each block's top/left edge and a shadow on its
    bottom/right edge -- a classic 2D trick for faking a 3D 'cube face' look.
    This is what makes blocks read as individual voxels instead of flat color
    patches, without needing any real 3D rendering.
    """
    if block_size < 4:
        return image  # bevel isn't meaningful on blocks this small

    arr = np.array(image).astype(np.int16)
    h, w, _ = arr.shape

    for y in range(0, h, block_size):
        arr[y:y + 1, :, :] += highlight
    for x in range(0, w, block_size):
        arr[:, x:x + 1, :] += highlight
    for y in range(block_size - 1, h, block_size):
        arr[y:y + 1, :, :] -= shadow
    for x in range(block_size - 1, w, block_size):
        arr[:, x:x + 1, :] -= shadow

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def full_pipeline(
    image: Image.Image,
    block_size: int = 16,
    use_custom_palette: bool = False,
) -> Image.Image:
    img = pixelate_minecraft(image, block_size=block_size, use_custom_palette=use_custom_palette)
    img = add_block_bevel(img, block_size=block_size, highlight=16, shadow=16)
    return img
