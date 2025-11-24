# CSV-grounded Chatbot

A lightweight Flask web app that answers questions about a CSV-based product catalog using the OpenAI API.

## Features
- Uses the `sample_data.csv` catalog for grounded responses.
- Simple web UI with running chat history stored in the user session.
- Safe prompts that encourage product-focused answers.

## Getting started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your API key:
   ```bash
   export OPENAI_API_KEY=your_key_here
   # Optional: export SECRET_KEY=your_session_secret
   ```
3. Run the server:
   ```bash
   flask --app app run --host 0.0.0.0 --port 5000
   ```
4. Open `http://localhost:5000` and ask about the catalog (e.g., "Do you have a backpack for hikes?").

## Notes
- The app reads from `sample_data.csv`; update that file with your own catalog rows to change the knowledge base.
- If no API key is present, the bot will remind you to set `OPENAI_API_KEY` instead of calling the API.
