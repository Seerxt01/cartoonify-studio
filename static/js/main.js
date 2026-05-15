// ============================================================
// main.js — The BROWSER-SIDE logic for Cartoonify Studio
// ============================================================
// This file runs INSIDE the browser (not on the server).
// It handles:
//   1. Drag & drop file upload
//   2. Sending the image to Flask via fetch() (AJAX)
//   3. Displaying the result images
//   4. Download button
// ============================================================

// ── Global state ─────────────────────────────────────────────
let uploadedFilename = null;   // stores the filename after upload
let resultFilename   = null;   // stores the processed filename
let selectedStyle    = "classic"; // currently selected cartoon style

// ── Grab DOM elements ─────────────────────────────────────────
const dropZone      = document.getElementById("drop-zone");
const fileInput     = document.getElementById("file-input");
const progressWrap  = document.getElementById("progress-wrap");
const progressBar   = document.getElementById("progress-bar");
const progressLabel = document.getElementById("progress-label");
const styleCard     = document.getElementById("style-card");
const resultCard    = document.getElementById("result-card");
const originalImg   = document.getElementById("original-img");
const resultImg     = document.getElementById("result-img");
const downloadBtn   = document.getElementById("download-btn");
const cartoonifyBtn = document.getElementById("cartoonify-btn");
const btnText       = document.getElementById("btn-text");
const btnSpinner    = document.getElementById("btn-spinner");
const toast         = document.getElementById("toast");


// ============================================================
// DRAG & DROP EVENTS
// ============================================================
// When a user drags a file over the drop zone, we highlight it.
// When they release (drop), we read the file.
// ============================================================

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();                        // needed to allow dropping
  dropZone.classList.add("drag-over");       // visual highlight
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");   // remove highlight
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");

  const file = e.dataTransfer.files[0];      // grab the dropped file
  if (file) handleFile(file);
});

// Regular click-to-browse also uses handleFile
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) handleFile(file);
});


// ============================================================
// handleFile(file)
// ============================================================
// Called whenever a file is chosen (drag or browse).
// Validates the file type, shows a preview, then uploads it.
// ============================================================
function handleFile(file) {

  // Check it's an image
  if (!file.type.startsWith("image/")) {
    showToast("Please upload an image file (JPG, PNG, WEBP)");
    return;
  }

  // Show a local preview immediately (before the upload finishes)
  const localUrl = URL.createObjectURL(file);  // creates a temporary local URL
  originalImg.src = localUrl;

  // Show the progress bar
  progressWrap.classList.remove("hidden");
  animateProgress(0, 70, 600);  // animate from 0% → 70% to show activity

  // Upload the file to Flask
  uploadFile(file);
}


// ============================================================
// uploadFile(file)
// ============================================================
// Sends the image file to Flask's /upload route using FormData.
// FormData is a built-in way to send files via fetch().
// ============================================================
async function uploadFile(file) {

  const formData = new FormData();
  formData.append("file", file);   // "file" must match request.files["file"] in Flask

  try {
    // fetch() sends an HTTP request — here we POST to /upload
    const response = await fetch("/upload", {
      method: "POST",
      body:   formData,
      // NOTE: Don't set Content-Type header; browser sets it automatically for FormData
    });

    const data = await response.json();  // parse the JSON Flask sends back

    if (data.error) {
      showToast(data.error);
      resetProgressBar();
      return;
    }

    // Store the filename so we can use it in /cartoonify next
    uploadedFilename = data.filename;

    // Finish the progress animation to 100%
    animateProgress(70, 100, 300);

    setTimeout(() => {
      progressLabel.textContent = "Upload complete! ✓";
      // Enable the style picker card
      unlockStyleCard();
    }, 350);

  } catch (err) {
    showToast("Upload failed. Is the Flask server running?");
    resetProgressBar();
    console.error(err);
  }
}


// ============================================================
// runCartoonify()
// ============================================================
// Called when the user clicks "Cartoonify!".
// Tells Flask: "take this file, apply this style, give me result."
// ============================================================
async function runCartoonify() {

  if (!uploadedFilename) {
    showToast("Please upload an image first");
    return;
  }

  // Show loading spinner on button
  setButtonLoading(true);

  try {
    // POST JSON data to /cartoonify
    const response = await fetch("/cartoonify", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },  // tell Flask we're sending JSON
      body: JSON.stringify({
        filename: uploadedFilename,
        style:    selectedStyle,
      }),
    });

    const data = await response.json();

    if (data.error) {
      showToast(data.error);
      setButtonLoading(false);
      return;
    }

    resultFilename = data.result_filename;

    // Display the processed image
    // We load it from the /static/results/ folder that Flask serves automatically
    resultImg.src = `/static/results/${resultFilename}?t=${Date.now()}`;
    // ?t=Date.now() is a cache-buster so the browser always loads the fresh image

    // Show the result card with a small animation delay
    resultCard.classList.remove("hidden");
    setTimeout(() => resultCard.scrollIntoView({ behavior: "smooth" }), 100);

    // Wire up the download button
    downloadBtn.onclick = () => {
      window.location.href = `/download/${resultFilename}`;
    };

  } catch (err) {
    showToast("Processing failed. Check the Flask console for errors.");
    console.error(err);
  }

  setButtonLoading(false);
}


// ============================================================
// STYLE BUTTON SELECTION
// ============================================================
// When the user clicks a style button, we mark it active
// and update selectedStyle so runCartoonify() knows which to use.
// ============================================================
document.querySelectorAll(".style-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    // Remove active class from all buttons
    document.querySelectorAll(".style-btn").forEach(b => b.classList.remove("active"));
    // Add active to the clicked one
    btn.classList.add("active");
    // Update the global variable
    selectedStyle = btn.dataset.style;  // reads the data-style="classic" attribute
  });
});


// ============================================================
// resetAll()
// ============================================================
// Resets the page back to the upload state.
// ============================================================
function resetAll() {
  uploadedFilename = null;
  resultFilename   = null;
  selectedStyle    = "classic";

  fileInput.value  = "";
  originalImg.src  = "";
  resultImg.src    = "";

  progressWrap.classList.add("hidden");
  progressBar.style.width = "0%";
  progressLabel.textContent = "Uploading…";

  resultCard.classList.add("hidden");

  // Re-lock the style card
  styleCard.classList.add("opacity-40", "pointer-events-none");

  // Reset style buttons
  document.querySelectorAll(".style-btn").forEach(b => b.classList.remove("active"));
  document.querySelector('[data-style="classic"]').classList.add("active");

  window.scrollTo({ top: 0, behavior: "smooth" });
}


// ── Helper functions ──────────────────────────────────────────

function unlockStyleCard() {
  styleCard.classList.remove("opacity-40", "pointer-events-none");
  styleCard.scrollIntoView({ behavior: "smooth" });
}

function setButtonLoading(isLoading) {
  cartoonifyBtn.disabled = isLoading;
  btnText.classList.toggle("hidden", isLoading);
  btnSpinner.classList.toggle("hidden", !isLoading);
}

function animateProgress(from, to, duration) {
  const steps = 20;
  const stepTime = duration / steps;
  const increment = (to - from) / steps;
  let current = from;

  const interval = setInterval(() => {
    current += increment;
    progressBar.style.width = `${Math.min(current, 100)}%`;
    if (current >= to) clearInterval(interval);
  }, stepTime);
}

function resetProgressBar() {
  progressWrap.classList.add("hidden");
  progressBar.style.width = "0%";
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3500);
}
