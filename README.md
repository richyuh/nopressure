# No Pressure

A lightweight Streamlit app for tracking blood pressure readings, monitoring trends, and generating personalized AI-powered guidance.

## Features

- Log blood pressure readings (systolic, diastolic, heart rate)
- View recent readings and trends
- Generate personalized guidance using AI
- Track symptoms and notes with each reading

## Setup

1. **Install dependencies** (using `uv`):
   ```bash
   uv sync
   ```

2. **Set up OpenAI API key**:
   ```bash
   export PERSONAL_OAI_API_KEY=your_api_key_here
   ```

## Running the App

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

## Requirements

- Python >= 3.13
- OpenAI API key

