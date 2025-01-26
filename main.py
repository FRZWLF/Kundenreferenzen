from sentence_transformers import util
from clustering import save_challenge_categories_to_db
from mongoDB import generate_embeddings_for_field, setup_db
from scrap_data import scrap_customer_data, scrap_product_data
from flask import Flask, render_template, request, jsonify

from shared import model, db, client

#Flask initialisieren
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# def extract_phrases(user_input):
#     """
#     Extrahiert relevante Phrasen aus der Nutzereingabe.
#     """
#     doc = nlp(user_input.lower())  # Eingabe zu Kleinbuchstaben konvertieren
#     phrases = []
#
#     # Wichtige Wortarten (NOUN, ADJ) kombinieren
#     for token in doc:
#         if token.pos_ in {"NOUN", "ADJ"} and not token.is_stop:  # Relevante Wörter
#             phrases.append(token.text)
#
#     # Phrasen kombinieren
#     if len(phrases) > 1:
#         combined_phrases = [" ".join(phrases[i:i+2]) for i in range(len(phrases) - 1)]
#         print(f"Combined Phrases: {combined_phrases}")
#         return combined_phrases
#     return phrases


def match_challenges_with_embeddings(user_input, data, selected_category, similarity_threshold):
    """
    Berechnet die Ähnlichkeit zwischen der Nutzereingabe und den gespeicherten Challenges.
    """
    # Embedding der Nutzereingabe berechnen
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
    collection = db["customers"]

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

def match_solutions_with_embeddings(input, data):
    user_embedding = model.encode(input, convert_to_tensor=True)

    results = []
    for entry in data:
        descriptions = entry.get("description", [])
        embeddings = entry.get("embeddings", [])

        # Ähnlichkeit berechnen
        similarity_scores = util.cos_sim(user_embedding, embeddings)
        for idx, score in enumerate(similarity_scores[0]):
            if score > 0.35:  # Threshold für Relevanz
                results.append({
                    "product_name": entry["product_name"],
                    "description": descriptions,
                    "similarity": round(score.item(), 2),
                    "url": entry.get("product_url", "N/A")
                })

    # Ergebnisse nach Ähnlichkeit sortieren
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    return results


@app.route("/solutions", methods=["POST"])
def search_solutions():
    data = request.json
    user_input = data.get("challenge", "").lower()
    collection = db["products"]

    data = list(collection.find())

    matched_solutions = match_solutions_with_embeddings(user_input, data)

    for match in matched_solutions:
        print(f"Product: {match['product_name']}, Ähnlichkeit: {match['similarity']:.2f}, Hit: {match['description']}, URL: {match['url']}")

    return jsonify(matched_solutions)


@app.route("/categories", methods=["GET"])
def get_categories_data():
    # Zähle die Anzahl der Referenzen pro Kategorie
    pipeline = [
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    collection = db["customers"]
    data = list(collection.aggregate(pipeline))

    # Formatieren für das Frontend
    result = [{"category": item["_id"], "count": item["count"]} for item in data]
    return jsonify(result)


@app.route("/rescrap", methods=["GET"])
def rescrap_data():
    print("Rescrap-Route wurde aufgerufen")
    scrap_product_data()
    scrap_customer_data()
    generate_embeddings_for_field("products", "description")
    generate_embeddings_for_field("customers", "challenges")
    save_challenge_categories_to_db()
    return '', 200


def is_db_initialized(collection_name):
    return db[collection_name].estimated_document_count() > 0


if __name__ == "__main__":
    #Initialer Setup beim erstmaligem Ausführen
    if not is_db_initialized("products") or not is_db_initialized("customers"):
        print("Initialisiere die Datenbank...")
        setup_db("products")
        setup_db("customers")
        scrap_product_data()
        scrap_customer_data()
        generate_embeddings_for_field("products", "description")
        generate_embeddings_for_field("customers", "challenges")
        save_challenge_categories_to_db()
    else:
        print("Datenbank bereits initialisiert. Starte nur die App...")

    try:
        print("Starte die Anwendung.")
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("Beende die Anwendung")
    finally:
        client.close()
        print("Verbindung zur MongoDB geschlossen.")