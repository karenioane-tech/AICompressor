from pypdf import PdfReader, PdfWriter


def compress_pdf(input_path, output_path):
    """
    Compress a PDF by:
    1. Reading the original PDF
    2. Adding pages to a PdfWriter
    3. Compressing each page's content streams
    4. Removing duplicate objects where possible
    5. Writing the optimized PDF
    """

    reader = PdfReader(input_path)

    writer = PdfWriter()

    # Add pages FIRST.
    # The page must belong to the writer before
    # compress_content_streams() is called.
    for page in reader.pages:

        writer.add_page(page)

    # Now the pages belong to PdfWriter,
    # so content stream compression is safe.
    for page in writer.pages:

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
        "algorithm": "PDF Content Stream Optimization"
    }