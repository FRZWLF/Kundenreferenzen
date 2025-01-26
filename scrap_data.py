from bs4 import BeautifulSoup
import requests
from mongoDB import save_to_db


def scrap_customer_data():
    url = "https://www.intershop.com/en/customers-details"
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

        save_to_db(customer_data, "customers")
        counter += 1

    print(f"Gespeicherte Kunden: {counter}/{count}")
    print("Scrapping abgeschlossen")


def scrap_product_data():
    url = "https://www.intershop.com/en/e-commerce-solutions"
    product_details = []
    forbidden_links = ["en/contact-overview","en/request-demo"]
    counter = 0
    count = 0
    res = requests.get(url)
    #print(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup.prettify())

    product_links = soup.find(class_="content-boxes").find_all('a')
    for link in product_links:
        print("https://www.intershop.com/" + link.get('href'))
        product_details.append("https://www.intershop.com/" + link.get('href'))
        count += 1

    for l in product_details:
        res = requests.get(l)
        soup = BeautifulSoup(res.text, 'html.parser')

        link_elements = soup.find_all(class_="linklist")
        for linklist in link_elements:
            if linklist.find('a').get('href').startswith("en/") and linklist.find('a').get('href') not in forbidden_links:
                #Produktname
                try:
                    product = linklist.find('a').text.strip()
                except:
                    print(f"Fehler beim Scrappen des Products")

                #Description
                try:
                    ce_text = linklist.find_previous(class_="ce_text")
                    description = ce_text.find('p').find('span').text.strip()
                except:
                    print(f"Keine Beschreibung gefunden für: {product}")

                #Daten erstellen
                product_data = {
                    "product_name": product,
                    "product_url": "https://www.intershop.com/" + linklist.find('a').get('href'),
                    "description": description,
                }
                #print("Zu speichernde Daten:", product_data)

                save_to_db(product_data, "products")
                counter += 1

    print("Scrapping abgeschlossen")