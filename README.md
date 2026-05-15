# 🎨 Cartoonify Studio

> Transform any photo into cartoon art — built with Python, Flask & OpenCV.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-orange)

---

## ✨ Features

| Feature | Details |
|---|---|
| 5 Cartoon Styles | Classic, Pencil Sketch, Anime, Comic, B&W |
| Drag & Drop Upload | With live preview |
| Side-by-side Compare | Original vs. Cartoon |
| One-click Download | Saves processed image |
| Dark UI | Responsive, modern design |

---

## 🗂 Project Structure

```
cartoonify_studio/
│
├── app.py              ← Flask server (routes & logic)
├── cartoonify.py       ← OpenCV image processing
├── requirements.txt    ← Python dependencies
│
├── templates/
│   └── index.html      ← Main HTML page
│
└── static/
    ├── css/style.css   ← Custom styles
    ├── js/main.js      ← Browser-side JavaScript
    ├── uploads/        ← Uploaded images saved here
    └── results/        ← Processed images saved here
```

---

## 🚀 How to Run (VS Code)

### Step 1 — Clone or download the project

```bash
git clone https://github.com/YOUR_USERNAME/cartoonify-studio.git
cd cartoonify-studio
```

### Step 2 — Create a virtual environment

A virtual environment keeps your project's packages separate from your system Python.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` in your terminal — that means it's active.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, OpenCV, and NumPy.

### Step 4 — Run the server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 5 — Open in browser

Go to: **http://127.0.0.1:5000**

Upload a photo, pick a style, hit Cartoonify! 🎉

---

## 🧠 How It Works

```
Browser → POST /upload  → Flask saves image to static/uploads/
Browser → POST /cartoonify → Flask calls OpenCV → saves to static/results/
Browser → GET /download/<file> → Flask sends file for download
```

### OpenCV Techniques Used

| Style | Technique |
|---|---|
| Classic Cartoon | Bilateral filter + Adaptive Threshold edges |
| Pencil Sketch | Grayscale + Dodge blend |
| Anime | Triple bilateral filter + HSV saturation boost + Canny edges |
| Comic | K-means colour quantization + thick dilated edges |
| B&W Cartoon | Grayscale bilateral filter + Adaptive Threshold |

---

## 📦 Tech Stack

- **Python** — Server-side language
- **Flask** — Lightweight web framework
- **OpenCV** — Computer vision & image processing
- **NumPy** — Array math for image data
- **Tailwind CSS** — Utility-first CSS framework
- **Vanilla JavaScript** — Fetch API for AJAX calls

---

## 💬 Interview Q&A

**Q: What is Flask and why did you use it?**
Flask is a micro web framework for Python. I used it because it's simple to learn, has minimal boilerplate, and is perfect for small-to-medium projects like this one.

**Q: What is OpenCV?**
OpenCV (Open Source Computer Vision Library) is a library for real-time image processing. It provides functions like bilateral filters, edge detection, and colour space conversions.

**Q: What is a bilateral filter?**
A bilateral filter blurs an image while preserving edges. It considers both the spatial distance and the colour difference between pixels — unlike Gaussian blur which blurs everything uniformly.

**Q: How does the pencil sketch effect work?**
1. Convert image to grayscale
2. Invert the grayscale image
3. Apply Gaussian blur to the inverted image
4. Divide the original grey by (255 - blurred) → creates a dodge blend that looks like pencil lines

**Q: What is the request/response cycle?**
The browser sends an HTTP request (GET or POST) to a Flask route. Flask processes it (reads files, runs code) and sends back a response (HTML, JSON, or a file).

---

## 🤝 Contributing

Pull requests welcome! Feel free to add more cartoon styles.

---

## 📄 License

MIT License — free to use and modify.
