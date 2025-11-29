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

2. **Configure environment variables** in `.env.local`:
   ```bash
   OPENAI_API_KEY=<your-openai-api-key>
   DB_URL=postgresql://<username>@localhost:5432/nopressure
   ```
   Replace `<your-openai-api-key>` with your actual API key and `<username>` with your database user.

3. **Initialize the database** (local development only):
   ```bash
   bash database/init_db.sh
   ```
   
   Note: On Streamlit Cloud, tables are auto-created on first startup.

## Running the App

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

## Requirements

- Python >= 3.13
- PostgreSQL database
- OpenAI API key

