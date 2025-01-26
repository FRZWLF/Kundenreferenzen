from sentence_transformers import util
from shared import db, model

collection = db["customers"]

categories = {
    "Customer Experience": "Improving customer satisfaction, loyalty, and retention.",
    "E-Commerce Optimization": "Optimizing online stores, platforms, and sales strategies.",
    "Product Data Management": "Managing large catalogs, standardizing data, and handling SKUs.",
    "Internationalization": "Expanding platforms to multiple countries, languages, and regions.",
    "Omnichannel Solutions": "Integrating multiple sales channels and devices.",
    "Pricing and Revenue": "Improving pricing strategies, revenue growth, and profitability.",
    "Operational Efficiency": "Streamlining operations, automating processes, and reducing complexity.",
    "Digital Transformation": "Modernizing and digitizing business processes and platforms."
}

# Überkategorien und Beschreibungen in Embeddings umwandeln
category_embeddings = {cat: model.encode(desc) for cat, desc in categories.items()}

def assign_challenges_to_categories(challenges):
    """
    Ordnet Herausforderungen basierend auf semantischer Ähnlichkeit den Überkategorien zu.
    """
    assigned_categories = []
    for challenge in challenges:
        challenge_embedding = model.encode(challenge)
        # Berechne die Ähnlichkeit mit allen Kategorien
        similarities = {cat: util.cos_sim(challenge_embedding, emb).item() for cat, emb in category_embeddings.items()}
        # Beste Kategorie auswählen
        best_category = max(similarities, key=similarities.get)
        assigned_categories.append(best_category)
    return assigned_categories

def save_challenge_categories_to_db():
    """
    Speichert die Cluster-Labels und Namen in der Datenbank.
    """
    for customer in collection.find():
        challenges = customer.get("challenges", [])
        if not challenges:
            continue

        categories = assign_challenges_to_categories(challenges)
        collection.update_one(
            {"_id": customer["_id"]},
            {"$set": {"categories": categories}}
        )
        print(f"Kategorien für {customer['customer_name']} erfolgreich gespeichert.")