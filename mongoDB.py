from shared import db, model


def setup_db(collection_name):
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' erfolgreich erstellt!")
    collection = db[collection_name]
    if collection_name == "products":
        collection.create_index("product_name", unique=True)
        print(f"Index auf 'product_name' in '{collection_name}' erstellt.")
    else:
        collection.create_index("customer_name", unique=True)
        print(f"Index auf 'customer_name' in '{collection_name}' erstellt.")
    return collection

def save_to_db(data, collection_name):
    collection = db[collection_name]
    key_name = "product_name" if collection_name == "products" else "customer_name"

    if collection_name == "products":
        existing_entry = collection.find_one({"product_url": data["product_url"]})
    else:
        existing_entry = collection.find_one({key_name: data.get(key_name)})
    if not existing_entry:
        collection.insert_one(data)
        print(f"Gespeichert: {data[key_name]}")
    else:
        update_fields = {k: v for k, v in data.items() if k != "_id"}
        collection.update_one(
            {key_name: data[key_name]},
            {"$set": update_fields}
        )
        print(f"{key_name} {data[key_name]} aktualisiert.")

def generate_embeddings_for_field(collection_name, field_name):
    """
    Berechnet Embeddings speichert sie in der Datenbank.
    """
    collection = db[collection_name]
    key_name = "product_name" if collection_name == "products" else "customer_name"
    for doc in collection.find():
        items = doc.get(field_name, [])
        if not items:
            identifier = doc.get(key_name, "Unbekannt")
            print(f"Keine Daten im Feld '{field_name}' für {identifier}.")
            continue
        # Berechne Embeddings für jedes item
        embeddings = model.encode(items, convert_to_tensor=False).tolist()
        # Embeddings in der Datenbank speichern
        collection.update_one({"_id": doc["_id"]}, {"$set": {f"embeddings": embeddings}})
        identifier = doc.get(key_name, "Unbekannt")
        print(f"Embeddings für {identifier} in '{collection_name}' gespeichert.")