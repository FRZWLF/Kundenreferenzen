function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
    document.getElementById(tabId).style.display = "block";
}

const form = document.getElementById("search")

form.addEventListener("submit", async (event) => {
    event.preventDefault()

    const challenge = document.getElementById("challenge").value
    const response = await fetch("/search", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({ challenge }),
    });

    const result = await response.json()
    const resultdiv = document.getElementById("results")
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
});


async function fetchCategoryData() {
    const response = await fetch("http://127.0.0.1:5000/categories");
    const data = await response.json();
    return data;
}


async function createChart() {
    const data = await fetchCategoryData();

    //Kategorie und Werte extrahieren
    const labels = data.map(item => item.category)
    const counts = data.map(item => item.count);

    //Chart generieren
    const ctx = document.getElementById("challengeChart").getContext("2d")
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: "Anzahl der Kundenreferenzen",
                data: counts,
                backgroundColor: "rgba(174,174,175,0.8)",
                borderColor: "rgb(192,75,130)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
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

// Diagramm erstellen
createChart();