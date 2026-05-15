# ============================================================
# cartoonify.py — The IMAGE PROCESSING ENGINE
# ============================================================
# OpenCV (cv2) is a powerful library for working with images.
# Think of it like Photoshop, but controlled by Python code.
#
# Every digital image is just a 3D grid of numbers:
#   height × width × 3 color channels (Blue, Green, Red)
# OpenCV lets us read, edit, and save those numbers.
# ============================================================

import cv2       # OpenCV — image processing
import numpy as np  # NumPy — fast math on arrays (image = array)


def cartoonify_image(input_path, output_path, style):
    """
    Read an image from input_path, apply 'style', save to output_path.

    Returns: (True, "ok") on success
             (False, "error message") on failure
    """

    # ── Step 1: Read the image from disk ─────────────────────
    # cv2.imread returns a NumPy array (or None if file not found)
    img = cv2.imread(input_path)

    if img is None:
        return False, "Could not read image — unsupported format?"

    # ── Step 2: Resize for consistent processing ──────────────
    # Large images slow everything down; cap width at 900px
    h, w = img.shape[:2]          # shape → (height, width, channels)
    if w > 900:
        scale = 900 / w
        img = cv2.resize(img, (900, int(h * scale)),
                         interpolation=cv2.INTER_AREA)

    # ── Step 3: Route to the chosen style ─────────────────────
    style_map = {
        "classic": classic_cartoon,
        "sketch":  pencil_sketch,
        "anime":   anime_style,
        "comic":   comic_style,
        "bw":      bw_cartoon,
    }

    func = style_map.get(style, classic_cartoon)  # default = classic

    try:
        result = func(img)
    except Exception as e:
        return False, f"Processing error: {str(e)}"

    # ── Step 4: Save the result ───────────────────────────────
    cv2.imwrite(output_path, result)
    return True, "ok"


# ============================================================
# STYLE 1 — Classic Cartoon
# ============================================================
# Technique:
#   1. Smooth the image so colours merge into flat regions
#   2. Find edges (dark outlines)
#   3. Combine → cartoon look
# ============================================================
def classic_cartoon(img):
    """
    Classic cartoon effect: flat colours + bold black outlines.
    """

    # ── Bilateral filter: smooths colours but KEEPS edges sharp
    # Think of it as "blurring only the colours, not the outlines"
    #   d=9        → how many surrounding pixels to consider
    #   sigmaColor → how much colour difference is allowed in the blur
    #   sigmaSpace → how far away pixels can be to still influence each other
    smooth = cv2.bilateralFilter(img, d=9, sigmaColor=200, sigmaSpace=200)

    # Apply the filter twice for a stronger cartoon look
    smooth = cv2.bilateralFilter(smooth, d=9, sigmaColor=200, sigmaSpace=200)

    # ── Edge detection with adaptive thresholding
    # Convert to grayscale first (edges are easier to find in grey)
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # medianBlur reduces noise so we don't get too many fake edges
    gray  = cv2.medianBlur(gray, 7)

    # adaptiveThreshold draws black where there's an edge, white elsewhere
    edges = cv2.adaptiveThreshold(
        gray,
        255,                              # max value (white)
        cv2.ADAPTIVE_THRESH_MEAN_C,       # compare each pixel to local mean
        cv2.THRESH_BINARY,                # result: black or white only
        blockSize=9,                      # size of the local area
        C=2                               # constant subtracted from mean
    )

    # ── Combine: apply edges (dark lines) over smooth colours
    # Convert edges to 3-channel so it matches the colour image
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # bitwise_and keeps colour where edges are white, blacks where edge is black
    cartoon = cv2.bitwise_and(smooth, edges_colored)

    return cartoon


# ============================================================
# STYLE 2 — Pencil Sketch
# ============================================================
# Technique:
#   1. Convert to grayscale
#   2. Invert it (negative)
#   3. Blur the negative
#   4. Blend original grey + blurred negative → pencil lines appear
# ============================================================
def pencil_sketch(img):
    """
    Pencil sketch effect: grey, hand-drawn looking.
    """

    # Convert colour image → grey (single channel)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Invert: dark pixels become bright, bright become dark
    inverted = cv2.bitwise_not(gray)

    # Gaussian blur softens the inverted image
    # ksize=(21,21) → 21×21 pixel kernel; must be odd numbers
    blurred = cv2.GaussianBlur(inverted, (21, 21), sigmaX=0)

    # Dodge blend: divides the grey by (255 - blurred) pixel-by-pixel
    # This creates the pencil-line illusion
    sketch = cv2.divide(gray, 255 - blurred, scale=256.0)

    # Convert single-channel back to 3-channel (BGR) for saving
    sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    return sketch_bgr


# ============================================================
# STYLE 3 — Anime Style
# ============================================================
# Technique:
#   Anime has soft pastel colours + crisp outlines.
#   We boost saturation (vivid colours) + thin dark edges.
# ============================================================
def anime_style(img):
    """
    Anime effect: vivid colours, smooth shading, clean outlines.
    """

    # ── Strong bilateral filter for the anime "cel-shaded" look
    smooth = img.copy()
    for _ in range(3):   # apply 3 times for maximum smoothing
        smooth = cv2.bilateralFilter(smooth, d=9, sigmaColor=150, sigmaSpace=150)

    # ── Boost colour saturation in HSV colour space
    # HSV = Hue (colour), Saturation (intensity), Value (brightness)
    # Much easier to boost colour in HSV than in BGR
    hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV)

    # Multiply saturation channel by 1.5 (50% more vivid)
    # np.clip ensures values stay in [0, 255] range
    hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.float32) * 1.5, 0, 255).astype(np.uint8)

    smooth = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # ── Thin, crisp outlines using Canny edge detector
    # Canny finds edges by looking for sudden brightness changes
    # threshold1, threshold2 control edge sensitivity
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=80, threshold2=160)

    # Dilate (thicken) edges slightly so they're visible
    kernel = np.ones((2, 2), np.uint8)
    edges  = cv2.dilate(edges, kernel, iterations=1)

    # Invert edges: we want black lines, not white
    edges_inv = cv2.bitwise_not(edges)
    edges_bgr = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

    anime = cv2.bitwise_and(smooth, edges_bgr)

    return anime


# ============================================================
# STYLE 4 — Comic Style
# ============================================================
# Technique:
#   Comics have punchy high-contrast colours + thick bold lines.
#   We use strong edge thickening + colour quantization.
# ============================================================
def comic_style(img):
    """
    Comic book effect: high contrast colours, thick bold outlines.
    """

    # ── Quantize colours → reduces the number of distinct colours
    #    making it look like a printed comic
    #    We use k-means clustering to group similar colours
    Z = img.reshape((-1, 3)).astype(np.float32)   # flatten to list of pixels
    K = 8                                           # keep only 8 colour groups
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers  = np.uint8(centers)
    result   = centers[labels.flatten()].reshape(img.shape)

    # ── Boost contrast with a CLAHE-like approach
    # Add strong bilateral filter on top for clean flat regions
    result = cv2.bilateralFilter(result, d=9, sigmaColor=150, sigmaSpace=150)

    # ── Thick bold edges (signature comic style)
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 120)

    # Dilate makes lines thicker — the comic "ink" effect
    kernel = np.ones((3, 3), np.uint8)
    edges  = cv2.dilate(edges, kernel, iterations=2)

    # Apply edges as black outlines over quantized colour image
    edges_inv = cv2.bitwise_not(edges)
    edges_bgr = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
    comic     = cv2.bitwise_and(result, edges_bgr)

    return comic


# ============================================================
# STYLE 5 — Black & White Cartoon
# ============================================================
# Technique:
#   Grayscale + soft smoothing + strong edge outlines.
#   Classic newspaper cartoon / old animation feel.
# ============================================================
def bw_cartoon(img):
    """
    Black & white cartoon: smooth grey tones + clear dark outlines.
    """

    # Convert to greyscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Bilateral filter on greyscale for smooth tones
    smooth = cv2.bilateralFilter(gray, d=9, sigmaColor=100, sigmaSpace=100)
    smooth = cv2.bilateralFilter(smooth, d=9, sigmaColor=100, sigmaSpace=100)

    # Edge detection
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=7,
        C=3
    )

    # Combine smooth grey + edges (black where edge, smooth otherwise)
    bw = cv2.bitwise_and(smooth, edges)

    # Return as 3-channel image so it saves properly
    return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
