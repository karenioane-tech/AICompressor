import gzip
import shutil


def compress_data(
    input_path,
    output_path
):
    """
    Compress text/data files
    using Gzip / DEFLATE.
    """

    with open(
        input_path,
        "rb"
    ) as source:

        with gzip.open(
            output_path,
            "wb"
        ) as destination:

            shutil.copyfileobj(

                source,

                destination

            )


    return {

        "algorithm":
            "Gzip / DEFLATE"

    }