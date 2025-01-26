document.addEventListener("DOMContentLoaded", () => {
    const searchButton = document.getElementById("search-btn");
    const filterButton = document.getElementById("filter-btn");
    const searchInput = document.getElementById("challenge");
    const reverFilterButton = document.getElementById("revert-filter")

    // Buttons standardmäßig deaktivieren
    searchButton.disabled = true;
    filterButton.disabled = true;
    reverFilterButton.classList.add("disabled");

    showTab('results')

    // Aktiviere Buttons, wenn die Suchleiste nicht leer ist
    searchInput.addEventListener("input", () => {
        const isSearchEmpty = !searchInput.value.trim();
        searchButton.disabled = isSearchEmpty;
        filterButton.disabled = isSearchEmpty;
        if (isSearchEmpty){
            reverFilterButton.classList.add("disabled");
        } else {
            reverFilterButton.classList.remove("disabled");
        }
    });
});


const rangeInput = document.getElementById('similarity-filter');
const rangeDisplay = document.getElementById('range-display');
const form = document.getElementById("search")
const filter = document.getElementById("filter")
const rescrapBtn = document.getElementById("rescrap-btn")
const notification = document.getElementById("notification")


function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    document.getElementById(tabId).style.display = "block";

    document.querySelectorAll('.tabs button').forEach(button => button.classList.remove('active'));
    document.querySelector(`#tab-${tabId}`).classList.add('active');

    const filterContainer = document.getElementById('filter');
    if (tabId === 'results') {
        filterContainer.style.display = "flex"
    } else {
        filterContainer.style.display = "none"
    }
}


function getFilterValues() {
    const selectedCategory = document.getElementById('category-filter').value || "";
    const selectedSimilarity = parseFloat(document.getElementById('similarity-filter').value).toFixed(2);
    return { selectedCategory, selectedSimilarity };
}


function resetFilters() {
    document.getElementById('category-filter').value = "";
    document.getElementById('similarity-filter').value = 0.35;
    document.getElementById('range-display').textContent = parseFloat(0.35).toFixed(2);
    const challenge = document.getElementById("challenge").value;
    document.getElementById('references').focus()

    if (!challenge) {
        return;
    }

    fetchAndDisplayReferences(challenge)
}

async function fetchAndDisplayReferences(challenge="", category="", similarity= 0.35) {
    try {
        const response = await fetch("/search", {
            method: "POST",
            headers: {"Content-Type": "application/json" },
            body: JSON.stringify({ challenge, category, similarity }),
        });

        const result = await response.json()
        const resultdiv = document.getElementById("results")
        if (!result || !Array.isArray(result) || result.length === 0) {
            resultdiv.innerHTML = `
                <div class="empty">
                    <h2>Keine Referenzen für die Suchanfrage oder Filterung vorhanden.</h2>
                    <p>Passe deine Suche oder die Filterung an, um Referenzen zu erhalten.</p>
                </div>
            `;
        } else {
            resultdiv.innerHTML = result.map(result => `
                <div class="customer">
                    <h2>${result.customer_name}</h2>
                    <div class="box-content">
                        <div>
                            <p><strong>Challenge:</strong><br> <span class="value">${result.challenge}</span></p>
                        </div>
                        <div>
                            <p><strong>Ähnlichkeit:</strong> ${result.similarity}</p>
                            <p><strong>Kategorie:</strong> ${result.categorie}</p>
                        </div>
                    </div>
                    <a href="${result.url}">Mehr erfahren</a>
                </div>
            `).join("");
        }
    } catch (error) {
        console.error("Fehler beim Abrufen der Ergebnisse:", error);
    }
}


async function fetchAndDisplaySolutions(challenge="") {
    try {
        const response = await fetch("/solutions", {
            method: "POST",
            headers: {"Content-Type": "application/json" },
            body: JSON.stringify({ challenge }),
        });

        const result = await response.json()
        const resultdiv = document.getElementById("solutions")
        if (!result || !Array.isArray(result) || result.length === 0) {
            resultdiv.innerHTML = `
                <div class="empty">
                    <h2>Keine Lösungen für die Suchanfrage gefunden.</h2>
                    <p>Passe deine Suche an, um Produktvorschläge zu erhalten.</p>
                </div>
            `;
        } else {
            resultdiv.innerHTML = result.map(result => `
                <div class="customer">
                    <h2>${result.product_name}</h2>
                    <div class="box-content">
                        <div>
                            <p><strong>Beschreibung:</strong><br> <span class="value">${result.description}</span></p>
                        </div>
                        <div>
                            <p><strong>Ähnlichkeit:</strong> ${result.similarity}</p>
                        </div>
                    </div>
                    <a href="${result.url}">Mehr erfahren</a>
                </div>
            `).join("");
        }
    } catch (error) {
        console.error("Fehler beim Abrufen der Ergebnisse:", error);
    }
}


rangeInput.addEventListener('input', () => {
    rangeDisplay.textContent = parseFloat(rangeInput.value).toFixed(2);
});


filter.addEventListener("submit", async (event) => {
    event.preventDefault()
    const challenge = document.getElementById("challenge").value;
    const { selectedCategory, selectedSimilarity } = getFilterValues();

    if (!challenge) {
        return;
    }

    fetchAndDisplayReferences(challenge, selectedCategory, selectedSimilarity);
});


form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const challenge = document.getElementById("challenge").value;
    const { selectedCategory, selectedSimilarity } = getFilterValues();

    fetchAndDisplayReferences(challenge, selectedCategory, selectedSimilarity);
    fetchAndDisplaySolutions(challenge);
    showTab('results');
});


rescrapBtn.addEventListener("click", async () => {
    try {
        rescrapBtn.classList.add("running");
        const response = await fetch("http://127.0.0.1:5000/rescrap");

        if (response.ok) {
            rescrapBtn.classList.remove("running");

            notification.classList.add("visible");

            setTimeout(() => {
                notification.classList.remove("visible")
            }, 5000);
        } else {
            throw new Error("Fehler beim scrappen.");
        }
    } catch (error) {
        console.error(error);
    } finally {
        rescrapBtn.classList.remove("running");
    }
})


async function fetchCategoryData() {
    const response = await fetch("http://127.0.0.1:5000/categories");
    const data = await response.json();
    return data;
}

let chartInstance;
async function createChart() {
    const data = await fetchCategoryData();

    //Kategorie und Werte extrahieren
    const labels = data.map(item => item.category);
    const counts = data.map(item => item.count);

    //Chart generieren
    const ctx = document.getElementById("challengeChart").getContext("2d")
    if (chartInstance) {
        chartInstance.destroy();
    }
    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: "Anzahl der Kundenreferenzen",
                data: counts,
                backgroundColor: "#d33333",
                borderColor: "none",
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

createChart();

window.addEventListener('resize', () => {
    chartInstance.resize();
});