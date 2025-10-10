const API_URL = "http://localhost:8000/api/explanation";

// Detektovanje jezika browsera, vraća 'en', 'de', 'es', ...
function detectBrowserLang(supported) {
    const langRaw = navigator.language || navigator.userLanguage || "en";
    const langShort = langRaw.slice(0,2).toLowerCase();
    if (supported.includes(langShort)) return langShort;
    return "en";
}

// Lista jezika za koje imaš prevod
const SUPPORTED_LANGS = ["en", "es", "de", "fr", "ru", "zh", "ar", "pt", "it", "nl", "sr", "pl", "el", "tr", "ja", "hi", "fa", "id", "sw", "ha"];

function fetchExplanation(lang) {
    fetch(`${API_URL}?lang=${lang}`)
        .then(resp => resp.json())
        .then(data => {
            document.getElementById("explanation-content").textContent = data.explanation;
        })
        .catch(() => {
            document.getElementById("explanation-content").textContent = "Explanation not available.";
        });
}

// On page load:
const lang = detectBrowserLang(SUPPORTED_LANGS);
fetchExplanation(lang);
