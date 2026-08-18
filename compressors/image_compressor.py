from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def compress_image(
    input_path,
    output_path,
    colors=32
):
    """
    Compress an image using
    K-Means color quantization.

    colors:
        16 = fast
        32 = balanced
        64 = high quality
    """

    # ======================================================
    # OPEN IMAGE
    # ======================================================

    original = Image.open(
        input_path
    )


    # Detect transparency BEFORE any mode conversion,
    # since converting straight to RGB silently discards it.
    has_alpha = (

        original.mode in ("RGBA", "LA")

        or (
            original.mode == "P"
            and "transparency" in original.info
        )

    )


    if has_alpha:

        image = original.convert("RGBA")
        alpha_channel = image.split()[-1]

    else:

        image = original.convert("RGB")
        alpha_channel = None


    # ======================================================
    # RESIZE LARGE IMAGES
    # ======================================================

    max_dimension = 1200


    if max(image.size) > max_dimension:

        ratio = (
            max_dimension
            / max(image.size)
        )


        new_size = (

            int(
                image.width * ratio
            ),

            int(
                image.height * ratio
            )

        )


        image = image.resize(

            new_size,

            Image.Resampling.LANCZOS

        )


        if alpha_channel is not None:

            alpha_channel = alpha_channel.resize(

                new_size,

                Image.Resampling.LANCZOS

            )


    # ======================================================
    # CONVERT TO NUMPY (RGB only — alpha is handled separately)
    # ======================================================

    rgb_image = image.convert("RGB")

    image_array = np.array(
        rgb_image
    )


    height, width, channels = (
        image_array.shape
    )


    # Flatten pixels
    pixels = image_array.reshape(
        -1,
        3
    )


    # ======================================================
    # SAMPLE PIXELS
    # ======================================================

    max_samples = 20_000


    if len(pixels) > max_samples:

        rng = np.random.default_rng(
            42
        )


        sample_indices = rng.choice(

            len(pixels),

            max_samples,

            replace=False

        )


        sample_pixels = pixels[
            sample_indices
        ]

    else:

        sample_pixels = pixels


    # ======================================================
    # K-MEANS
    # ======================================================
    # A cluster count higher than the number of pixels being
    # clustered is invalid — guard against tiny/icon-sized images.

    effective_colors = max(
        1,
        min(
            colors,
            len(sample_pixels)
        )
    )


    kmeans = KMeans(

        n_clusters=effective_colors,

        random_state=42,

        n_init=3,

        max_iter=100

    )


    kmeans.fit(
        sample_pixels
    )


    # ======================================================
    # GET REPRESENTATIVE COLORS
    # ======================================================

    new_colors = (

        kmeans.cluster_centers_

        .astype(
            np.uint8
        )

    )


    # ======================================================
    # ASSIGN COLORS
    # ======================================================

    labels = kmeans.predict(
        pixels
    )


    compressed_pixels = (
        new_colors[labels]
    )


    # Restore image dimensions
    compressed_array = (

        compressed_pixels

        .reshape(
            height,
            width,
            3
        )

    )


    # ======================================================
    # CREATE IMAGE
    # ======================================================

    compressed_image = Image.fromarray(

        compressed_array

    )


    # Re-attach the original transparency, if any
    if alpha_channel is not None:

        compressed_image = compressed_image.convert("RGBA")
        compressed_image.putalpha(alpha_channel)


    # ======================================================
    # SAVE WEBP
    # ======================================================
    # WEBP supports alpha natively, so transparent images stay
    # transparent instead of getting a solid background baked in.

    compressed_image.save(

        output_path,

        "WEBP",

        quality=75,

        method=4

    )


    # ======================================================
    # RETURN INFORMATION
    # ======================================================

    return {

        "width":
            width,

        "height":
            height,

        "colors":
            effective_colors,

        "sampled_pixels":
            len(sample_pixels),

        "transparency_preserved":
            has_alpha

    }
