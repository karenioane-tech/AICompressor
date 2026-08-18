from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


def compress_pdf(input_path, output_path, image_quality=60):
    """
    Compress a PDF by:
    1. Reading the original PDF
    2. Adding pages to a PdfWriter
    3.Recompressing embedded images
    4. Compressing each page's content streams
    5. Removing duplicate objects where possible
    6. Writing the optimized PDF
    """

    try:
        reader = PdfReader(input_path)
    except PdfReadError as error:
        raise ValueError(
            "This PDF could not be read — it may be corrupted "
            "or password-protected."
        ) from error

    if reader.is_encrypted:
        raise ValueError(
            "This PDF is password-protected. Remove the "
            "password before compressing."
        )

    writer = PdfWriter()

    # Add pages FIRST.
    # The page must belong to the writer before
    # compress_content_streams() is called.
    for page in reader.pages:

        writer.add_page(page)

    images_compressed = 0

    for page in writer.pages:

        # Embedded images are usually the single biggest
        # contributor to PDF file size — recompress each one
        # as JPEG at a reduced quality before touching anything
        # else on the page.
        try:

            for img in page.images:

                try:
                    img.replace(img.image, quality=image_quality)
                    images_compressed += 1

                except Exception as error:
                    print(
                        f"Warning: Could not recompress image "
                        f"'{img.name}': {error}"
                    )

        except Exception as error:
            print(
                f"Warning: Could not access images on page: {error}"
            )

        # Now the pages belong to PdfWriter,
        # so content stream compression is safe.
        try:

            page.compress_content_streams()

        except Exception as error:

            # Some unusual PDF pages may not support
            # content stream compression.
            print(
                f"Warning: Could not compress page: {error}"
            )

    # Try to remove duplicate PDF objects.
    try:

        writer.compress_identical_objects(
            remove_identicals=True,
            remove_orphans=True
        )

    except Exception as error:

        print(
            f"Warning: Object optimization skipped: {error}"
        )

    # Write the final PDF
    with open(
        output_path,
        "wb"
    ) as output_file:

        writer.write(output_file)

    return {
        "pages": len(reader.pages),
        "images_compressed": images_compressed,
        "algorithm": "PDF Image + Content Stream Optimization"
    }
