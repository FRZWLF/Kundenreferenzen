import spacy
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

#Verbindung
client = MongoClient("mongodb://localhost:27017/")
db = client["intershop"]
collection = db["customers"]

#semantische Analyse
#model = SentenceTransformer('all-MiniLM-L6-v2')
#model = SentenceTransformer('all-MPNet-base-v2')

#Multilingual wegen Eingabe DE -> DB-Challenges EN
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

nlp = spacy.load("en_core_web_sm")

def setup_db():
    db.create_collection("customers")
    print("Collection 'customers' erfolgreich erstellt!")
    collection.create_index("customer_name", unique=True)
    print("Index auf 'customer_name' erstellt")

def save_to_db(customer_data):
    if not collection.find_one({"customer_name": customer_data["customer_name"]}):
        collection.insert_one(customer_data)
        print(f"Gespeichert: {customer_data["customer_name"]}")
    else:
        print(f"Kunde {customer_data['customer_name']} existiert bereits.")

def generate_embeddings_for_challenges():
    """
    Berechnet Embeddings für alle Challenges und speichert sie in der Datenbank.
    """
    for doc in collection.find():
        challenges = doc.get("challenges", [])
        # Berechne Embeddings für jede Challenge
        challenge_embeddings = model.encode(challenges, convert_to_tensor=False).tolist()
        # Embeddings in der Datenbank speichern
        collection.update_one({"_id": doc["_id"]}, {"$set": {"embeddings": challenge_embeddings}})
        print(f"Embeddings für {doc['customer_name']} gespeichert.")



if __name__ == "__main__":
    setup_db()

    #Verbindung schließen
    client.close()
    print("Verbindung zur MongoDB geschlossen.")