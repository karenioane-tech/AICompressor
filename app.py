import os
import time
import uuid
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from compressors.image_compressor import compress_image
from compressors.data_compressor import compress_data
from compressors.pdf_compressor import compress_pdf


# Load environment variables from .env file (local development)
load_dotenv()

app = Flask(__name__)


# ==========================================================
# CONFIGURATION
# ==========================================================

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
COMPRESSED_FOLDER = os.getenv("COMPRESSED_FOLDER", "compressed")
FILE_RETENTION_SECONDS = int(os.getenv("FILE_RETENTION_SECONDS", "3600"))  # 1 hour default
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50 MB default
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["COMPRESSED_FOLDER"] = COMPRESSED_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    COMPRESSED_FOLDER,
    exist_ok=True
)


# ==========================================================
# CLEANUP
# ==========================================================
# Files here are only ever meant to live for the duration of a
# single upload -> compress -> download cycle. Nothing about this
# app depends on them sticking around, so we purge aggressively
# rather than let uploads/ and compressed/ grow forever (and rather
# than leave people's original files sitting on disk indefinitely).

def purge_stale_files(folder, max_age_seconds=FILE_RETENTION_SECONDS):

    now = time.time()

    try:
        entries = os.listdir(folder)
    except FileNotFoundError:
        return

    for name in entries:

        if name == ".gitkeep":
            continue

        path = os.path.join(folder, name)

        try:
            if os.path.isfile(path) and (now - os.path.getmtime(path)) > max_age_seconds:
                os.remove(path)
        except OSError:
            pass


@app.before_request
def cleanup_old_files():
    purge_stale_files(UPLOAD_FOLDER)
    purge_stale_files(COMPRESSED_FOLDER)


# ==========================================================
# SUPPORTED FILE TYPES
# ==========================================================

IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

DATA_EXTENSIONS = {
    "txt",
    "csv",
    "json",
    "xml",
    "log"
}

PDF_EXTENSIONS = {
    "pdf"
}


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def index():
    return render_template("splash.html")


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# ==========================================================
# COMPRESS
# ==========================================================

@app.route("/compress", methods=["POST"])
def compress():

    # ------------------------------------------------------
    # Check uploaded file
    # ------------------------------------------------------

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "error": "No file uploaded."
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "success": False,
            "error": "No file selected."
        }), 400


    # ------------------------------------------------------
    # Secure filename
    # ------------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )


    # ------------------------------------------------------
    # Determine extension
    # ------------------------------------------------------

    extension = os.path.splitext(
        original_filename
    )[1].lower().replace(
        ".",
        ""
    )


    # ------------------------------------------------------
    # Unique ID
    # ------------------------------------------------------

    unique_id = uuid.uuid4().hex


    uploaded_filename = (
        f"{unique_id}_{original_filename}"
    )


    input_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_filename
    )


    # ------------------------------------------------------
    # Save upload
    # ------------------------------------------------------

    file.save(input_path)


    original_size = os.path.getsize(
        input_path
    )


    # ======================================================
    # IMAGE
    # ======================================================

    if extension in IMAGE_EXTENSIONS:

        output_filename = (
            f"{unique_id}_compressed.webp"
        )


        output_path = os.path.join(
            COMPRESSED_FOLDER,
            output_filename
        )


        # Get quality from frontend
        quality = request.form.get(
            "quality",
            "balanced"
        )


        quality_settings = {

            "fast": 16,

            "balanced": 32,

            "high": 64

        }


        colors = quality_settings.get(
            quality,
            32
        )


        compression_info = compress_image(

            input_path,

            output_path,

            colors=colors

        )


        engine = (
            "K-Means AI Color Quantization"
        )


    # ======================================================
    # TEXT / DATA
    # ======================================================

    elif extension in DATA_EXTENSIONS:

        output_filename = (
            f"{unique_id}_compressed.gz"
        )


        output_path = os.path.join(
            COMPRESSED_FOLDER,
            output_filename
        )


        compression_info = compress_data(

            input_path,

            output_path

        )


        engine = (
            "Gzip / DEFLATE"
        )


    # ======================================================
    # PDF
    # ======================================================

    elif extension in PDF_EXTENSIONS:

        output_filename = (
            f"{unique_id}_compressed.pdf"
        )


        output_path = os.path.join(
            COMPRESSED_FOLDER,
            output_filename
        )


        compression_info = compress_pdf(

            input_path,

            output_path

        )


        engine = (
            "PDF Content Stream Optimization"
        )


    # ======================================================
    # UNSUPPORTED
    # ======================================================

    else:

        if os.path.exists(input_path):

            os.remove(input_path)


        return jsonify({

            "success": False,

            "error": (
                "Unsupported file type. "
                "Use JPG, PNG, WEBP, PDF, TXT, "
                "CSV, JSON, XML or LOG."
            )

        }), 400


    # ======================================================
    # COMPRESSED SIZE
    # ======================================================

    compressed_size = os.path.getsize(
        output_path
    )


    # ======================================================
    # DISCARD THE ORIGINAL UPLOAD
    # ======================================================
    # Only the compressed output is ever downloaded — no reason to
    # keep the raw upload sitting on disk once we're done with it.

    if os.path.exists(input_path):
        os.remove(input_path)


    # ======================================================
    # STATISTICS
    # ======================================================

    if original_size > 0:

        saved_percentage = (

            (
                original_size
                - compressed_size
            )
            /
            original_size

        ) * 100


        if compressed_size > 0:

            compression_ratio = (
                original_size
                /
                compressed_size
            )

        else:

            compression_ratio = 0

    else:

        saved_percentage = 0

        compression_ratio = 0


    # ======================================================
    # RESPONSE
    # ======================================================

    return jsonify({

        "success": True,

        "original_filename":
            original_filename,

        "original_size":
            original_size,

        "compressed_size":
            compressed_size,

        "saved_percentage":
            round(
                saved_percentage,
                2
            ),

        "compression_ratio":
            round(
                compression_ratio,
                2
            ),

        "engine":
            engine,

        "download_url":
            f"/download/{output_filename}",

        "compression_info":
            compression_info

    })


# ==========================================================
# DOWNLOAD
# ==========================================================

@app.route("/download/<filename>")
def download(filename):

    return send_from_directory(

        COMPRESSED_FOLDER,

        filename,

        as_attachment=True

    )


# ==========================================================
# FILE TOO LARGE
# ==========================================================

@app.errorhandler(
    RequestEntityTooLarge
)
def handle_file_too_large(error):

    return jsonify({

        "success": False,

        "error":
            "File is too large. "
            "Maximum allowed size is 50 MB."

    }), 413


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    port = int(os.getenv("PORT", "5000"))
    
    app.run(

        host="0.0.0.0",

        port=port,

        debug=DEBUG

    )