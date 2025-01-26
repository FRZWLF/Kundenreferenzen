import re
import spacy
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
from scrap_data import scrap_customer_data
from flask import Flask, render_template, request, jsonify

#Flask initialisieren
app = Flask(__name__)

#semantische Analyse
#model = SentenceTransformer('all-MiniLM-L6-v2')
#model = SentenceTransformer('all-MPNet-base-v2')
#Multilingual
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

nlp = spacy.load("en_core_web_sm")

# Verbindung herstellen
client = MongoClient("mongodb://localhost:27017/")
db = client["intershop"]
collection = db["customers"]


@app.route('/')
def index():
    return render_template('index.html')


def extract_phrases(user_input):
    """
    Extrahiert relevante Phrasen aus der Nutzereingabe.
    """
    doc = nlp(user_input.lower())  # Eingabe zu Kleinbuchstaben konvertieren
    phrases = []

    # Wichtige Wortarten (NOUN, ADJ) kombinieren
    for token in doc:
        if token.pos_ in {"NOUN", "ADJ"} and not token.is_stop:  # Relevante Wörter
            phrases.append(token.text)

    # Phrasen kombinieren
    if len(phrases) > 1:
        combined_phrases = [" ".join(phrases[i:i+2]) for i in range(len(phrases) - 1)]
        print(f"Combined Phrases: {combined_phrases}")
        return combined_phrases
    return phrases


def match_challenges_with_embeddings(user_input, data, selected_category, similarity_threshold):
    """
    Berechnet die Ähnlichkeit zwischen der Nutzereingabe und den gespeicherten Challenges.
    """
    # Berechne das Embedding der Nutzereingabe
    user_embedding = model.encode(user_input, convert_to_tensor=True)

    results = []
    for entry in data:
        challenges = entry.get("challenges", [])
        categories = entry.get("categories", [])
        embeddings = entry.get("embeddings", [])

        if selected_category:
            filtered_indices = [i for i, category in enumerate(categories) if category == selected_category]
            challenges = [challenges[i] for i in filtered_indices]
            embeddings = [embeddings[i] for i in filtered_indices]
            categories = [categories[i] for i in filtered_indices]

        if not challenges or not embeddings:
            continue

        # Ähnlichkeit berechnen
        similarity_scores = util.cos_sim(user_embedding, embeddings)
        for idx, score in enumerate(similarity_scores[0]):
            if score > similarity_threshold:  # Threshold für Relevanz
                results.append({
                    "customer_name": entry["customer_name"],
                    "challenge": challenges[idx],
                    "similarity": round(score.item(), 2),
                    "categorie": categories[idx],
                    "url": entry.get("customer_url", "N/A")
                })

    # Ergebnisse nach Ähnlichkeit sortieren
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    return results


@app.route('/search', methods=['POST'])
def search_references():
    data = request.json
    user_input = data.get("challenge", "").lower()
    selected_category = data.get("category", "")
    similarity_threshold = float(data.get("similarity", 0.35))

    data = list(collection.find())

    matched_challenges = match_challenges_with_embeddings(user_input, data, selected_category, similarity_threshold)

    for match in matched_challenges:
        print(f"Kunde: {match['customer_name']}, Ähnlichkeit: {match['similarity']:.2f}, Hit: {match['challenge']}, URL: {match['url']}")

    return jsonify(matched_challenges)

    # #Matchmaking mit regex pattern
    # phrases = extract_phrases(user_input)
    # regex_pattern = "|".join(phrases)  # Erstelle ein Regex-Muster
    # regex = re.compile(regex_pattern, re.IGNORECASE)
    #
    # results = []
    # for doc in collection.find():
    #     for challenge in doc.get("challenges", []):
    #         if regex.search(challenge):
    #             results.append({
    #                 "customer_name": doc["customer_name"],
    #                 "challenge": challenge,
    #                 "url": doc["customer_url"]
    #             })
    #
    # for match in results:
    #     print(f"Kunde: {match['customer_name']}, Challenge: {match['challenge']}, URL: {match['url']}")
    #
    # # #Ergebnisse sortieren nach Ähnlichkeit
    # # results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    #
    # return jsonify(results)


@app.route("/categories", methods=["GET"])
def get_categories_data():
    """
    Liefert die Anzahl der Kundenreferenzen pro Kategorie als JSON.
    """
    # Zähle die Anzahl der Referenzen pro Kategorie
    pipeline = [
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    data = list(collection.aggregate(pipeline))

    # Formatieren für das Frontend
    result = [{"category": item["_id"], "count": item["count"]} for item in data]
    return jsonify(result)



if __name__ == "__main__":
    #scrap_customer_data()
    # generate_embeddings_for_challenges()
    app.run(debug=True)

    try:
        app.run(debug=True)
    finally:
        # Verbindung schließen
        client.close()
        print("Verbindung zur MongoDB geschlossen.")