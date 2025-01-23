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
        <div>
            <h2>${result.customer_name}</h2>
            <p><strong>Challenge:</strong> ${result.challenge}</p>
            <p><strong>Results:</strong> ${result.results.join(", ")}</p>
            <a href="${result.url}">Mehr erfahren</a>
        </div>
    `).join("");
});