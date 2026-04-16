# Sentiment Analysis for YouTube Comments using AI

Advanced Sentiment Analysis & Transcript Intelligence for YouTube, powered by Python and AI.

## Features
- **Video Metadata**: Fetches views, likes, and comment counts.
- **Sentiment Analysis**: Classifies comments as Positive, Negative, or Neutral.
- **AI Narrative**: Generates a text summary of the overall sentiment.
- **Transcript**: Fetches and displays the video transcript.
- **Visualizations**: Interactive charts and data breakdown.

## Installation

1.  **Clone the repository** (or download the zip).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Setup**:
    - Create a `.env` file in the root directory.
    - Add your YouTube Data API Key (if required by the code logic).

## Usage (Live Server Method)

Since this project uses a Python backend for AI and an HTML frontend:

### Step 1: Start the "Brain" (Backend)
Open your terminal and run:
```bash
python app.py
```
*Keep this terminal window open!*

### Step 2: Start the Interface
1.  Open `templates/index.html` in VS Code.
2.  Click **"Go Live"** (Live Server extension) at the bottom right.
3.  The app will open in your browser and connect to the Python backend automatically.

## Requirements
- Python 3.8+
- VS Code "Live Server" Extension
