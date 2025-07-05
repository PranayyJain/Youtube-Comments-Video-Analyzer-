# 🎬 YouTube Sentiment Analysis Pro

> Beautiful glassmorphism UI for analyzing YouTube comment sentiment with AI

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)

## 🚀 Live Demo
[Try it here](https://your-app-name.streamlit.app) *(Replace with your actual deployed URL)*

## ✨ Features

- 🎨 **Beautiful Glassmorphism UI** - iPhone-inspired glass design  
- ⚡ **Lightning Fast Analysis** - No heavy model downloads  
- 📊 **Interactive Charts** - Real-time sentiment visualization  
- 🔄 **Bulk Processing** - Analyze up to 1200+ comments  
- 📱 **Mobile Responsive** - Works on all devices  
- 🎯 **Two Versions Available** - Lightweight and Advanced  

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

## 🚀 Quick Start

### Option 1: Fast Edition (Recommended)
```bash
git clone https://github.com/YourUsername/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
pip install -r requirements_lightweight.txt
streamlit run app_lightweight.py

Option 2: Advanced Edition
bash
Copy
Edit
git clone https://github.com/YourUsername/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
pip install -r requirements.txt
streamlit run app.py
🔧 Setup
Get YouTube API Key:

Go to Google Cloud Console

Enable YouTube Data API v3

Create API key credentials

Configure API Key:

toml
Copy
Edit
# .streamlit/secrets.toml
YOUTUBE_API_KEY = "your_actual_api_key_here"
Run the Application:

bash
Copy
Edit
# Fast Edition
streamlit run app_lightweight.py

# Advanced Edition
streamlit run app.py
📊 Performance Comparison
Feature	Fast Edition	Advanced Edition
Startup Time	10–30 seconds	2–5 minutes
Memory Usage	200–500MB	2–4GB
Model Downloads	None	1GB+
Accuracy	Good	Excellent
Languages	English	100+ languages
System Requirements	Low	High

🛠️ Tech Stack
Backend: Python 3.13, Streamlit

APIs: YouTube Data API v3

Analysis: NLTK VADER, BERT, RoBERTa (advanced)

Visualization: Plotly, Custom CSS

UI: Glassmorphism design, responsive layout

🎨 Screenshots
Coming soon – Add screenshots of your deployed app

📦 Project Structure
bash
Copy
Edit
youtube-sentiment-analysis/
├── app_lightweight.py          # Fast edition main app
├── app.py                      # Advanced edition main app
├── Senti_lightweight.py        # Lightweight sentiment analysis
├── Senti.py                    # Advanced sentiment analysis
├── YoutubeCommentScrapper.py   # YouTube API integration
├── file_manager.py             # File handling utilities
├── requirements_lightweight.txt # Minimal dependencies
├── requirements.txt            # Full dependencies
├── .streamlit/
│   └── secrets.toml            # API configuration
├── run_fast.bat               # Windows launcher
├── README.md                  # This file
└── DEPLOYMENT_GUIDE.md        # Deployment instructions
🚀 Deployment
This project is ready for deployment on:

Streamlit Cloud (Recommended)

Heroku

Railway

DigitalOcean

See DEPLOYMENT_GUIDE.md for detailed instructions.

🎯 Use Cases
📊 Content Creators – Analyze video reception

🎬 Marketers – Understand audience sentiment

📚 Researchers – Study social media trends

🎓 Students – Learn sentiment analysis

🏢 Businesses – Monitor brand mentions

🔧 Advanced Features
Fast Edition
✅ NLTK VADER sentiment analysis

✅ Basic emoji processing

✅ Interactive charts

✅ CSV export

✅ Responsive design

Advanced Edition
✅ All Fast Edition features

✅ BERT multilingual analysis

✅ RoBERTa social media model

✅ 100+ language support

✅ Advanced emoji intelligence

✅ Confidence scoring

📈 Analytics
Comment Processing: Up to 1200+ comments per video

Languages Supported: 100+ (Advanced edition)

Sentiment Categories: Positive, Negative, Neutral

Export Formats: CSV, interactive charts

🤝 Contributing
Fork the repository

Create a feature branch

Make your changes

Submit a pull request

📝 License
This project is licensed under the MIT License – see the LICENSE file for details.

🙏 Acknowledgments
YouTube Data API v3 for comment data

NLTK for sentiment analysis

Hugging Face for transformer models

Streamlit for the web framework

Plotly for interactive charts

<div align="center"> <strong>Made with ❤️ for the YouTube community</strong> <br> <em>Analyze sentiment, understand your audience</em> </div> ```
