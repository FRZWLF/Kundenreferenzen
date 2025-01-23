from pymongo import MongoClient
from scrap_data import scrap_customer_data
from flask import Flask, render_template, request, jsonify

#Flask initialisieren
app = Flask(__name__)

# Verbindung herstellen
client = MongoClient("mongodb://localhost:27017/")
db = client["intershop"]
collection = db["customers"]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_references():
    data = request.json
    user_input = data.get("challenge", "").lower()

    #Matchmaking
    results = []
    for col in collection.find():
        for challenge in col.get("challenges", []):
            similarity = fuzz.token_sort_ratio(user_input, challenge.lower())
            if similarity >= 90:
                results.append({
                    "customer_name": col["customer_name"],
                    "challenge": challenge,
                    "similarity": similarity,
                    "results": col["results"],
                    "url": col["customer_url"]
                })

    # Ergebnisse sortieren nach Ähnlichkeit
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)

    return jsonify(results)



if __name__ == "__main__":
    #scrap_customer_data()
    app.run(debug=True)

    try:
        app.run(debug=True)
    finally:
        # Verbindung schließen
        client.close()
        print("Verbindung zur MongoDB geschlossen.")