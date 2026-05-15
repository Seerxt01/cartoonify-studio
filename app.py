# ============================================================
# app.py — The BRAIN of your Flask web app
# ============================================================
# Flask is a lightweight web framework for Python.
# Think of it like this:
#   Browser (user) → sends a request → Flask receives it
#   Flask processes → sends back a response (HTML page or image)
# ============================================================

import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from cartoonify import cartoonify_image  # our image processing functions

# ── Create the Flask app ──────────────────────────────────────
# __name__ tells Flask: "this file is the starting point"
app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────
# Folders where we save uploaded and processed images
UPLOAD_FOLDER  = "static/uploads"
RESULTS_FOLDER = "static/results"

app.config["UPLOAD_FOLDER"]  = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER

# Allowed image file types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# Make sure the folders exist (create them if they don't)
os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


# ── Helper: check file type ───────────────────────────────────
def allowed_file(filename):
    """
    Returns True if the uploaded file has an allowed extension.
    e.g. "photo.jpg" → True    "virus.exe" → False
    """
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# ROUTE 1:  GET  /
# ============================================================
# A "route" is a URL path. When the browser visits "/",
# Flask calls this function and returns the HTML homepage.
# ============================================================
@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


# ============================================================
# ROUTE 2:  POST  /upload
# ============================================================
# The browser sends the image file here (via the upload form).
# We save it, then send back the saved filename as JSON.
# POST is used when you're *sending data* to the server.
# ============================================================
@app.route("/upload", methods=["POST"])
def upload():
    """Receive an uploaded image, save it, return its filename."""

    # 1. Check if a file was actually included in the request
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]  # grab the file object

    # 2. Check the file has a name and an allowed extension
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # 3. Give the file a unique name so uploads never overwrite each other
    #    uuid4() generates a random ID like: 3f2a1b9c-…
    ext      = file.filename.rsplit(".", 1)[1].lower()
    unique   = str(uuid.uuid4())[:8]          # short 8-char ID
    filename = f"{unique}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 4. Save the file to disk
    file.save(filepath)

    # 5. Return the filename to the browser as JSON
    #    The browser's JavaScript will use this to call /cartoonify next
    return jsonify({"filename": filename})


# ============================================================
# ROUTE 3:  POST  /cartoonify
# ============================================================
# The browser tells us: "here's the filename + which style".
# We apply the OpenCV effect and return the result filename.
# ============================================================
@app.route("/cartoonify", methods=["POST"])
def cartoonify():
    """Apply the chosen cartoon style and return result filename."""

    # request.json reads the JSON body the browser sent
    data     = request.json
    filename = data.get("filename")
    style    = data.get("style", "classic")   # default to classic

    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    input_path  = os.path.join(UPLOAD_FOLDER,  filename)
    result_name = f"result_{style}_{filename}"
    output_path = os.path.join(RESULTS_FOLDER, result_name)

    # Check the source file actually exists on disk
    if not os.path.exists(input_path):
        return jsonify({"error": "Source image not found"}), 404

    # Call our image-processing function (in cartoonify.py)
    success, message = cartoonify_image(input_path, output_path, style)

    if not success:
        return jsonify({"error": message}), 500

    return jsonify({"result_filename": result_name})


# ============================================================
# ROUTE 4:  GET  /download/<filename>
# ============================================================
# The browser hits this URL to download the processed image.
# <filename> is a *variable* part of the URL.
# e.g.  /download/result_classic_abc123.png
# ============================================================
@app.route("/download/<filename>")
def download(filename):
    """Send the processed image as a downloadable file."""
    filepath = os.path.join(RESULTS_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    # as_attachment=True → browser shows "Save As" dialog
    return send_file(filepath, as_attachment=True)


# ── Run the app ───────────────────────────────────────────────
# debug=True → Flask auto-restarts when you save changes (great for dev!)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)