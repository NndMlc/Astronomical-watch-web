const API_URL = "http://localhost:8000/api/time"; // Prilagodi po potrebi
const EXPLANATION_URL = "explanation.html";

function fetchTimeAndUpdateBanner() {
    fetch(API_URL)
        .then(resp => resp.json())
        .then(data => updateBanner(data))
        .catch(err => {
            updateBanner({
                dies: "--",
                milidies: "--",
                progress: 0
            });
        });
}

function updateBanner(data) {
    const banner = document.getElementById("astro-banner");
    if (!banner) return;

    banner.innerHTML = `
        <div class="banner-title">Astronomical Watch</div>
        <div class="astro-time">
            <span class="dies">${data.dies !== undefined ? data.dies : "--"}</span>
            <span class="astro-dot">&middot;</span>
            <span class="milidies">${data.milidies !== undefined ? String(data.milidies).padStart(3,"0") : "--"}</span>
        </div>
        <div class="labels">
            <span>Dies</span>
            <span>miliDies</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fg" style="width:${data.progress || 0}%"></div>
        </div>
    `;

    // Klik na baner otvara explanation stranicu u novom tabu
    banner.onclick = () => {
        window.open(EXPLANATION_URL, '_blank');
    }
}

// Prvo učitavanje
fetchTimeAndUpdateBanner();
// Periodično osvežavanje (npr. svakih 5 sekundi)
setInterval(fetchTimeAndUpdateBanner, 5000);
