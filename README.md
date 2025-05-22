# 🔐 Face and License Plate Detection & Blurring Tool (with EXIF Preservation)

This Python project detects **faces** and **license plates** from input images using **RetinaFace**, **YOLO**, and **OCR**—then automatically **blurs** them to protect privacy. It also ensures **EXIF metadata** (e.g., GPS, timestamp) is retained. Built with a **Tkinter GUI** for ease of use and supports **batch image processing**.

---

## ✨ Key Features

- 👁️ Detects and **blurs human faces** using **RetinaFace**
- 🚗 Detects and **blurs license plates** using **YOLO + Tesseract OCR**
- 📁 Supports **bulk image processing** in folders
- 📸 Preserves **EXIF metadata** (e.g., date, location) in output images
- 🖼️ GUI built using **Tkinter** for simple user interaction

---

## 🖼️ GUI Preview

> _(Insert screenshot of your Tkinter GUI here if available)_

---

## 🗂️ Project Structure

├── blurred.py # Main entry point for GUI and processing
├── face_blur/ # RetinaFace-based face detection & blurring
├── plate_blur/ # License plate detection + OCR-based blurring
├── exif_utils/ # Preserve and transfer EXIF data
├── requirements.txt # All required packages
└── README.md # Project documentation



---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/souran7/Face-and-lecense-plate-recognition.git
cd Face-and-lecense-plate-recognition
```



### 2. Create a Virtual Environment
```bash

python -m venv env
env\Scripts\activate     # On Windows
# OR
source env/bin/activate  # On Mac/Linux
```


### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python blurred.py
```

