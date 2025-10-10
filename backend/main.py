from fastapi import FastAPI
from datetime import datetime, timezone
from core.timeframe import astronomical_time  # koristiš svoj core kod
from lang.translation import tr

app = FastAPI()

@app.get("/api/time")
def get_time(lang: str = "en"):
    now = datetime.now(timezone.utc)
    dies, milidies = astronomical_time(now)
    return {
        "dies": dies,
        "milidies": milidies,
        "countdown_label": tr("countdown_label", lang, dies=dies, milidies=milidies)
    }
