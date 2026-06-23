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


def suggest_block_size(image: Image.Image, target_blocks_across: int = 90) -> int:
    """
    Auto-picks a sensible block size based on image resolution, so a default
    upload looks good without the user needing to fiddle with the slider.
    Smaller photos get smaller blocks; large photos get bigger ones, aiming
    for roughly the same number of blocks across the width either way.
    """
    width, _ = image.size
    suggested = max(4, round(width / target_blocks_across))
    return min(suggested, 64)


def pixelate_minecraft(
    image: Image.Image,
    block_size: int = 16,
    use_custom_palette: bool = False,
    palette_colors: int = 48,
    contrast_boost: float = 1.1,
    saturation_boost: float = 1.15,
    edge_sharpen: bool = True,
) -> Image.Image:
    image = image.convert("RGB")
    original_size = image.size

    image = ImageEnhance.Contrast(image).enhance(contrast_boost)
    image = ImageEnhance.Color(image).enhance(saturation_boost)

    if edge_sharpen:
        # Makes object boundaries (e.g. a mountain silhouette against the sky)
        # pop more clearly before they get averaged into blocks.
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))

    small_size = (
        max(1, original_size[0] // block_size),
        max(1, original_size[1] // block_size),
    )
    small = image.resize(small_size, resample=Image.LANCZOS)

    if use_custom_palette:
        pal_img = build_palette_image(MINECRAFT_PALETTE)
        small = small.quantize(palette=pal_img, dither=Image.NONE).convert("RGB")
    else:
        small = small.convert("P", palette=Image.ADAPTIVE, colors=palette_colors, dither=Image.NONE).convert("RGB")

    result = small.resize(original_size, resample=Image.NEAREST)
    return result


def add_block_bevel(image: Image.Image, block_size: int, strength: float = 1.0) -> Image.Image:
    """
    Adds a highlight on each block's top/left edge and a shadow on its
    bottom/right edge -- fakes a 3D 'cube face' look in pure 2D.
    Bevel strength is scaled relative to block size so it looks proportional
    whether blocks are tiny or huge.
    """
    if block_size < 4:
        return image

    # Bigger blocks can take a stronger bevel without looking noisy;
    # tiny blocks need a much lighter touch.
    base_amount = max(6, min(24, block_size))
    highlight = int(base_amount * strength)
    shadow = int(base_amount * strength)

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
    block_size: int = None,
    use_custom_palette: bool = False,
) -> Image.Image:
    if block_size is None:
        block_size = suggest_block_size(image)

    img = pixelate_minecraft(image, block_size=block_size, use_custom_palette=use_custom_palette)
    img = add_block_bevel(img, block_size=block_size)
    return img
