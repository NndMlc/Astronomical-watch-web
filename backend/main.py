from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

# Import core funkcionalnosti (prilagodi putanju ako treba)
from astronomical_watch.core.timeframe import astronomical_time

app = FastAPI(
    title="Astronomical Watch Backend",
    description="API for providing astronomical time for the web widget/banner.",
    version="1.0.0"
)

# --- CORS omogućava frontend (widget) da pristupa API-ju sa bilo kog domena ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Za produkciju preporučuješ konkretne domene!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/time")
def get_time():
    """
    Vraća trenutno astronomsko vreme: dies, milidies i progres unutar milidiesa.
    """
    now = datetime.now(timezone.utc)
    dies, milidies = astronomical_time(now)

    # Koliko je prošlo kroz trenutni milidies (progres 0-100)
    seconds_in_day = 24 * 60 * 60
    seconds_now = now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6
    milidies_in_day = 1000
    milidies_float = seconds_now / seconds_in_day * milidies_in_day
    progress = int((milidies_float - int(milidies_float)) * 100)  # 0-99, stotinki milidiesa

    return {
        "dies": dies,
        "milidies": milidies,
        "progress": progress
    }

# --- (Po želji) API za explanation tekstove po jeziku ---
import json
import os

EXPLANATION_PATH = os.path.join(os.path.dirname(__file__), "explanation_texts.json")

def load_explanations():
    try:
        with open(EXPLANATION_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@app.get("/api/explanation")
def get_explanation(lang: str = "en"):
    """
    Vraća explanation tekst na traženom jeziku (ili engleski ako nema prevoda).
    """
    explanations = load_explanations()
    text = explanations.get(lang, explanations.get("en", "Explanation not available."))
    return {"lang": lang, "explanation": text}

# --- Health check endpoint ---
@app.get("/api/health")
def health():
    return {"status": "ok"}
