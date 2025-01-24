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


def match_challenges_with_embeddings(user_input):
    """
    Berechnet die Ähnlichkeit zwischen der Nutzereingabe und den gespeicherten Challenges.
    """
    # Berechne das Embedding der Nutzereingabe
    user_embedding = model.encode(user_input, convert_to_tensor=True)

    # Alle Dokumente durchlaufen und Ähnlichkeit berechnen
    results = []
    for doc in collection.find():
        challenge_embeddings = doc.get("embeddings", [])
        challenges = doc.get("challenges", [])
        if not challenge_embeddings or not challenges:
            continue

        # Ähnlichkeit berechnen
        similarity_scores = util.cos_sim(user_embedding, challenge_embeddings)
        max_similarity_idx = similarity_scores[0].argmax().item()
        max_similarity = similarity_scores[0][max_similarity_idx].item()

        if max_similarity > 0.35:  # Threshold für Relevanz
            results.append({
                "customer_name": doc["customer_name"],
                "challenge": challenges[max_similarity_idx],
                "similarity": round(max_similarity, 2),
                "categorie": doc["categories"][max_similarity_idx],
                "url": doc.get("customer_url", "N/A")
            })

    # Ergebnisse nach Ähnlichkeit sortieren
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    return results


@app.route('/search', methods=['POST'])
def search_references():
    data = request.json
    user_input = data.get("challenge", "").lower()

    matched_challenges = match_challenges_with_embeddings(user_input)

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