from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

#nlp = spacy.load("en_core_web_sm")

#semantische Analyse
#model = SentenceTransformer('all-MiniLM-L6-v2')
#model = SentenceTransformer('all-MPNet-base-v2')
#Multilingual wegen Eingabe DE -> DB-Challenges EN
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Verbindung herstellen
client = MongoClient("mongodb://localhost:27017/")
db = client["intershop2"]