# Astronomical Watch Web Widget

This repository contains a web banner (widget) and its backend API for displaying astronomical time in Dies and miliDies format, along with a progress bar indicating the fraction of the day that has passed. The widget is designed for easy embedding on any website. Clicking the banner opens a detailed explanation page in the user's language, with links to install desktop and mobile applications.

---

## Contents

- **Frontend:** Lightweight, embeddable widget (Vanilla JS) and explanation page with multilingual support.
- **Backend:** FastAPI service providing current astronomical time data and explanation texts.
- **Translations:** All translations are maintained in Python files; the frontend uses an automatically generated JSON.
- **Easy integration:** Just copy two files to your server or use a hosted version from this repository.

---

## How to Use the Widget on Your Website

1. **Copy and paste the following HTML snippet** wherever you want the banner to appear:

```html
<!-- Astronomical Watch Banner BEGIN -->
<link rel="stylesheet" href="https://your-domain/widget/style.css">
<div id="astro-banner"></div>
<script src="https://your-domain/widget/banner.js"></script>
<!-- Astronomical Watch Banner END -->
```
> **Note:** Replace `https://your-domain/widget/` with the actual URL where you host `style.css` and `banner.js` from the `frontend/public` folder of this repository.

2. **Backend API** (e.g., FastAPI) must be accessible at the URL specified in `banner.js` (default: `http://localhost:8000/api/time` or your deployment URL).

---

## Widget Features

- **Displays the current astronomical time** in Dies . miliDies format.
- **Visual progress bar** shows the fraction of the day passed within the current miliDies.
- **Multilingual support:** The explanation page automatically selects the user's language (20 languages supported), falling back to English if needed.
- **Clicking the banner** opens the explanation page with detailed information and app installation links.

---

## Backend Setup

1. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Run the FastAPI server**:

    ```bash
    uvicorn backend.main:app --reload
    ```

3. (Optional) **Generate explanation_texts.json**:

    ```bash
    python generate_explanation_json.py
    ```

---

## Generating Translations for the Frontend

Translations are maintained in Python files (`src/astronomical_watch/lang/explanation_xx_card.py`).  
For the frontend, they are automatically exported to `backend/explanation_texts.json` using the `generate_explanation_json.py` script.

---

## Customization & Development

- **Frontend code** is in `frontend/public`.
- **Backend code** is in `backend/`.
- **Core logic and translations** are in `src/astronomical_watch/`.

---

## Application Installation Links

The explanation page includes buttons to download the desktop and mobile versions of the application.  
Update the URLs in `explanation.html` with the actual links to your official pages or repositories.

---

## Licenses

- **Core part** (astronomical logic and translations): see `LICENCE.CORE`.
- **Web part** (widget, backend, frontend): [MIT License](LICENSE).
- For more details, see the accompanying license files in the repository.

---

## Example

### Widget Preview

![Banner Example](docs/widget-preview.png)

---

## Contact

For questions, suggestions, or bug reports, please open an issue on this repository or contact us via the email provided in the project.


# Astronomical Watch Web Widget

Ovaj repozitorijum sadrži web baner (widget) i prateći backend API za prikaz astronomskog vremena u vidu Dies i miliDies formata, kao i progres bara koji pokazuje deo dana koji je protekao. Widget je namenjen za lako postavljanje na bilo koji web sajt, a klikom na baner korisnik dobija detaljno objašnjenje koncepta na svom jeziku, sa linkovima za instalaciju desktop i mobilnih aplikacija.

---

## Sadržaj

- **Frontend:** Jednostavan, lagan widget/baner (Vanilla JS) i explanation stranica sa višejezičnom podrškom.
- **Backend:** FastAPI servis koji isporučuje podatke o trenutnom astronomskom vremenu i explanation tekstove.
- **Prevodi:** Svi prevodi čuvaju se u Python fajlovima, a frontend koristi automatski generisani JSON.
- **Jednostavna integracija:** Dovoljno je da kopirate dva fajla na svoj server ili koristite hosting ovog repozitorijuma.

---

## Kako koristiti widget na svom sajtu

1. **Iskopirajte sledeći HTML snippet** na mesto gde želite da se prikaže baner:

```html
<!-- Astronomical Watch Banner BEGIN -->
<link rel="stylesheet" href="https://tvoj-domen/widget/style.css">
<div id="astro-banner"></div>
<script src="https://tvoj-domen/widget/banner.js"></script>
<!-- Astronomical Watch Banner END -->
```
> **Napomena:** Zamenite `https://tvoj-domen/widget/` stvarnim URL-om gde hostujete fajlove `style.css` i `banner.js` iz `frontend/public` foldera ovog repozitorijuma.

2. **Backend API** (npr. FastAPI) mora biti dostupan na URL-u koji je podešen u `banner.js` (default: `http://localhost:8000/api/time` ili prema vašem deploymentu).

---

## Funkcionalnosti widgeta

- **Prikaz aktuelnog astronomskog vremena** u formatu Dies . miliDies.
- **Vizuelni progres bar** prikazuje koliko je dana proteklo unutar trenutnog miliDies-a.
- **Višejezična podrška**: explanation stranica automatski bira jezik korisnika (20 jezika), fallback na engleski.
- **Klik na baner** otvara explanation stranicu sa detaljnim objašnjenjem i linkovima za aplikacije.

---

## Postavljanje backend-a

1. **Instalirajte zavisnosti**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Pokrenite FastAPI server**:

    ```bash
    uvicorn backend.main:app --reload
    ```

3. (Opcionalno) **Generišite explanation_texts.json**:

    ```bash
    python generate_explanation_json.py
    ```

---

## Generisanje prevoda za frontend

Prevodi se održavaju u Python fajlovima (`src/astronomical_watch/lang/explanation_xx_card.py`).  
Za frontend se automatski generiše `backend/explanation_texts.json` skriptom `generate_explanation_json.py`.

---

## Prilagođavanje i razvoj

- **Frontend kod** nalazi se u `frontend/public`.
- **Backend kod** nalazi se u `backend/`.
- **Core logika i prevodi** su u `src/astronomical_watch/`.

---

## Linkovi za instalaciju aplikacije

Na explanation stranici se nalaze dugmad za preuzimanje desktop i mobilne verzije aplikacije. Ažurirajte URL-ove u `explanation.html` prema aktuelnim verzijama na vašim zvaničnim stranicama ili repozitorijumima.

---

## Licence

- **Core deo** (astronomska logika i prevodi): posebna licenca, vidi `LICENCE.CORE`.
- **Web deo** (widget, backend, frontend): [MIT License](LICENSE).
- Za više informacija pogledajte prateće licence u repozitorijumu.

---

## Primeri

### Izgled widgeta na stranici

![Primer banera](docs/widget-preview.png)

---

## Kontakt

Za pitanja, predloge i prijavu grešaka, otvorite issue na ovom repozitorijumu ili nas kontaktirajte putem emaila navedenog u projektu.
