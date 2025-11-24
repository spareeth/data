import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sample_data.csv"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def load_catalog():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"CSV file not found at {DATA_FILE}")
    return pd.read_csv(DATA_FILE)


def find_relevant_rows(df: pd.DataFrame, query: str, limit: int = 4) -> pd.DataFrame:
    if not query:
        return df.head(limit)

    normalized_query = query.strip().lower()
    matches = df[df.apply(lambda row: normalized_query in row.to_string().lower(), axis=1)]
    if matches.empty:
        return df.head(limit)
    return matches.head(limit)


def build_prompt(context_rows: pd.DataFrame, user_message: str) -> list:
    context = context_rows.to_dict(orient="records")
    system_prompt = (
        "You are a helpful retail product assistant. Use the provided catalog rows to answer "
        "questions. If the question is unrelated to the catalog, politely steer the user back to the products." 
        "Respond concisely with product names and details when relevant."
    )
    context_prompt = (
        "Relevant catalog entries: " + 
        "\n".join([f"- {row['name']} (ID {row['product_id']}): {row['description']} [Category: {row['category']}, Price: ${row['price']}]" for row in context])
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Catalog context:\n{context_prompt}\n\nUser question: {user_message}"},
    ]


@app.route("/", methods=["GET"])
def index():
    session.setdefault("history", [])
    return render_template("index.html", history=session["history"])


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message", "").strip()
    if not user_message:
        return redirect(url_for("index"))

    df = load_catalog()
    relevant_rows = find_relevant_rows(df, user_message)

    if client.api_key:
        messages = build_prompt(relevant_rows, user_message)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        bot_reply = completion.choices[0].message.content
    else:
        bot_reply = (
            "OpenAI API key is missing. Set the OPENAI_API_KEY environment variable to enable the chatbot."
        )

    session.setdefault("history", [])
    session["history"].append({"user": user_message, "bot": bot_reply})
    session.modified = True
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
