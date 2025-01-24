from bs4 import BeautifulSoup
import requests
from mongoDB import save_to_db

url = "https://www.intershop.com/en/customers-details"

def scrap_customer_data():
    customers_details = []
    counter = 0
    count = 0
    res = requests.get(url)
    #print(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup.prettify())

    customer_links = soup.find_all(class_="customer-list-item-link")
    for link in customer_links:
        if link.get('href').startswith("/en/customers-details"):
            st = link.get('href').split('/')
            customers_details.append(st[3])
            count += 1

    for l in customers_details:
        customer_url = url+'/'+l
        res = requests.get(customer_url)
        soup = BeautifulSoup(res.text, 'html.parser')

        #Kundenname
        try:
            customer = soup.find(class_="company-contact").find(class_="h3").text.strip()
        except:
            print(f"Fehler beim Scrappen des Kundennamens")

        #Challenges
        challenges = []
        try:
            challenge = soup.find(class_="challenge").find(class_="text").ul
            for li in challenge.stripped_strings:
                challenges.append(li)
        except:
            print(f"Keine Challenges gefunden für: {customer}")

        #Solutions
        results = []
        try:
            result = soup.find(class_="solution").find(class_="text").ul
            for li in result.stripped_strings:
                results.append(li)
        except:
            print(f"Keine Results gefunden für: {customer}")

        # #Keywords
        # all_keywords = []
        # for challenge in challenges:
        #     all_keywords.extend(extract_keywords(challenge))
        #
        # unique_keywords = list(set(all_keywords))

        #Daten erstellen
        customer_data = {
            "customer_name": customer,
            "customer_url": customer_url,
            "challenges": challenges,
            "solutions": results
        }

        save_to_db(customer_data)
        counter += 1

    print(f"Gespeicherte Kunden: {counter}/{count}")
    print("Scrapping abgeschlossen")
