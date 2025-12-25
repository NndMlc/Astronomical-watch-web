# Copilot Instructions for Astronomical Watch Web

## Project Overview
- **Purpose:** Provides a web widget and backend API for displaying astronomical time (Dies/miliDies) and explanations in 20+ languages.
- **Architecture:**
  - **Frontend:** Vanilla JS widget and explanation page in `frontend/public/`. Integrates with backend via HTTP API.
  - **Backend:** FastAPI app in `backend/main.py` serving `/api/time` and explanation endpoints. Core astronomical logic and translations in `backend/src/astronomical_watch/`.
  - **Translations:** Python files in `src/astronomical_watch/lang/` are exported to JSON for frontend via `generate_explanation_json.py`.

## Key Workflows
- **Start backend server:**
  - `uvicorn backend.main:app --reload`
- **Install backend dependencies:**
  - `pip install -r backend/requirements.txt`
- **Generate frontend translation JSON:**
  - `python generate_explanation_json.py` (outputs to `backend/explanation_texts.json`)

## Patterns & Conventions
- **Frontend:**
  - All widget logic in `banner.js`, explanation logic in `explanation.js`.
  - Multilingual support via `explanation_texts.json` loaded dynamically.
  - Minimal dependencies; pure JS/HTML/CSS.
- **Backend:**
  - API endpoints defined in `backend/src/astronomical_watch/routes/`.
  - Astronomical calculations in `backend/src/astronomical_watch/core/` and `solar/`.
  - Caching handled in `offline/cache.py` (default: `~/.astronomical_watch/equinox_cache.json`).
  - Translations loaded from Python files, not PO/MO or JSON.
- **Testing:** No explicit test suite detected; validate changes by running backend and checking widget output.
- **Licensing:** Core logic under custom license, web/widget under MIT.

## Integration Points
- **Frontend <-> Backend:**
  - Widget fetches time data from `/api/time` and explanations from generated JSON.
- **External:**
  - No third-party APIs; all astronomical logic is local.

## Examples
- To add a new language: create `explanation_xx_card.py` in `src/astronomical_watch/lang/`, then run `generate_explanation_json.py`.
- To add a new API route: implement in `backend/src/astronomical_watch/routes/`, register in `main.py`.

## References
- See `README.md` for integration and setup details.
- See `backend/CORE_FILES.md` and `SPEC.md` for deeper backend logic documentation.

---
**If any section is unclear or missing, please provide feedback for further refinement.**
