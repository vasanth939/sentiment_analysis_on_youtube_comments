# 📊 AI-Powered YouTube Sentiment Analyzer
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)
![NLP](https://img.shields.io/badge/NLP-Sentiment%20Analysis-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)
A full-stack web application that leverages Natural Language Processing (NLP) and the YouTube Data API to analyze viewer sentiment on any YouTube video. By simply pasting a video URL, this tool extracts thousands of comments, processes them using AI, and presents a comprehensive visual dashboard of audience reception.
## ✨ Features
- **Deep Sentiment Analysis:** Classifies comments into Positive, Negative, or Neutral sentiments using an AI-driven NLP pipeline.
- **AI Narrative Summaries:** Automatically generates a textual summary explaining the overall sentiment and audience reaction.
- **Interactive Data Visualization:** Dynamic charts and graphs breaking down sentiment trends and engagement metrics.
- **Rich Video Metadata:** Fetches and displays view counts, likes, comment totals, and video transcripts.
- **Fast & Responsive Dashboard:** A clean user interface that updates seamlessly with the Python backend.
## 🛠️ Tech Stack
**Backend:**
- Python 3
- Flask (REST API)
- Natural Language Processing (NLP) algorithms
- YouTube Data API v3
**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Chart.js (for data visualization)
## 📸 Demo
*(Note: Add a screenshot of your dashboard here once you upload it to GitHub)*
> `![Dashboard Screenshot](link-to-your-image.png)`
## 🚀 Getting Started
Follow these instructions to set up the project locally on your machine.
### Prerequisites
- Python 3.8 or higher installed on your system.
- A Google Cloud Platform account to get a YouTube Data API key.
### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/youtube-sentiment-analyzer.git
   cd youtube-sentiment-analyzer
Install the required Python dependencies:

bash
pip install -r requirements.txt
Set up Environment Variables:

Create a file named .env in the root directory.
Add your YouTube Data API Key to the file:
env
YOUTUBE_API_KEY=your_api_key_here
Usage
Start the Python Backend: Open your terminal and run the Flask application:

bash
python app.py
(Keep this terminal running to serve the AI model and API requests).

Open the Frontend:

Open templates/index.html in your browser.
If using VS Code, right-click index.html and select "Open with Live Server".
Analyze a Video:

Copy any valid YouTube video URL.
Paste it into the search bar on the web interface and click "Analyze" to see the magic happen!
