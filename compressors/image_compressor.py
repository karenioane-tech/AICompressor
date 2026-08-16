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

    image = Image.open(
        input_path
    ).convert("RGB")


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


    # ======================================================
    # CONVERT TO NUMPY
    # ======================================================

    image_array = np.array(
        image
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

    kmeans = KMeans(

        n_clusters=colors,

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


    # ======================================================
    # SAVE WEBP
    # ======================================================

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
            colors,

        "sampled_pixels":
            len(sample_pixels)

    }