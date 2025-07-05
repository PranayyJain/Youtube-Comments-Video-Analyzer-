# 🎬 YouTube Sentiment Analysis Pro

> Beautiful glassmorphism UI for analyzing YouTube comment sentiment with AI

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)

---

## 🚀 Live Demo
[Try it here](https://your-app-name.streamlit.app) *(Replace with your actual deployed URL)*

---

## ✨ Features

- 🎨 **Beautiful Glassmorphism UI** – iPhone-inspired glass design  
- ⚡ **Lightning Fast Analysis** – No heavy model downloads  
- 📊 **Interactive Charts** – Real-time sentiment visualization  
- 🔄 **Bulk Processing** – Analyze up to 1200+ comments  
- 📱 **Mobile Responsive** – Works on all devices  
- 🎯 **Two Versions Available** – Lightweight and Advanced  

---

## 🎯 Choose Your Version

### ⚡ Fast Edition (Recommended)

- **File:** `app_lightweight.py`  
- **Perfect for:** Slower PCs, limited internet  
- **Analysis:** NLTK VADER + emoji processing  
- **Size:** ~100MB total  
- **Speed:** Lightning fast startup  

### 🧠 Advanced Edition

- **File:** `app.py`  
- **Perfect for:** Research, maximum accuracy  
- **Analysis:** BERT + RoBERTa + multilingual support  
- **Size:** ~2GB total  
- **Speed:** 2–5 minute startup  

---

## 🚀 Quick Start

### 🧪 Option 1: Fast Edition (Recommended)

```bash
git clone https://github.com/YourUsername/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
pip install -r requirements_lightweight.txt
streamlit run app_lightweight.py
```

### 🧪 Option 1: Fast Edition (Recommended)
```bash
git clone https://github.com/YourUsername/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
pip install -r requirements.txt
streamlit run app.py
```

### 🔧 Setup
1. Get YouTube API Key
    Visit Google Cloud Console
    Enable YouTube Data API v3
    Create an API key
# .streamlit/secrets.toml
YOUTUBE_API_KEY = "your_actual_api_key_here"

### Run the application
# Fast Edition
streamlit run app_lightweight.py
# Advanced Edition
streamlit run app.py

### 🛠️ Tech Stack

Backend: Python 3.13, Streamlit

APIs: YouTube Data API v3

Analysis: NLTK VADER, BERT, RoBERTa

Visualization: Plotly, Custom CSS

UI: Glassmorphism design, responsive layout


