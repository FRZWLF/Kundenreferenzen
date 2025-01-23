from pymongo import MongoClient

#Verbindung
client = MongoClient("mongodb://localhost:27017/")
db = client["intershop"]
collection = db["customers"]

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


if __name__ == "__main__":
    setup_db()

    #Verbindung schließen
    client.close()
    print("Verbindung zur MongoDB geschlossen.")