import requests
import json
import tkinter as tk
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
from fake_useragent import UserAgent

def get_gtin():
    def submit():
        global gtin
        gtin = entry.get()
        root.destroy()

    root = tk.Tk()
    root.title("GTIN įvestis")
    tk.Label(root, text="Įveskite GTIN:").pack(pady=10)
    entry = tk.Entry(root, width=30)
    entry.pack(pady=5)
    tk.Button(root, text="Pateikti", command=submit).pack(pady=10)
    root.mainloop()
    return gtin
def load_cookies():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    return {cookie['name']: cookie['value'] for cookie in cookies}
def process_page(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"URL: {url}")
    print(f"Statusas: {response.status_code}")
    print("HTML fragmentas (pirmi 500 simbolių):")
    print(response.text[:500])
    product_count_tag = soup.find("h3", class_="mp0t_ji")
    if product_count_tag:
        print("Produktų skaičius: ", product_count_tag.text.strip())

    results = []
    gtin_tags = soup.find_all("span", {"data-testid": "gtinName"})
    name_tags = soup.find_all("strong", class_="mgn2_14")

    for gtin_tag, name_tag in zip(gtin_tags, name_tags):
        gtins = [x.strip() for x in gtin_tag.text.split(":")[1].split(",")]
        if gtins:
            selected_gtin = random.choice(gtins)
            results.append((selected_gtin, name_tag.text.strip()))

    return results
def scrape_all_pages(gtin):
    base_url = "https://salescenter.allegro.com/offer"
    cookies = load_cookies()

    session = requests.Session()
    session.cookies.update(cookies)

    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    results = []
    page = 1

    while True:
        print(f"Tikriname puslapį: {page}")
        url = f"{base_url}?q={gtin}&page={page}"
        response = session.get(url, headers=headers)

        with open(f"response_page_{page}.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        page_results = process_page(session, url)
        if not page_results:
            break
        results.extend(page_results)

        next_page = soup.find("button", {"aria-label": "next page"})
        if not next_page:
            break

        page += 1
        time.sleep(random.uniform(1, 3))  

    return results

def save_results_to_excel(results):
    df = pd.DataFrame(results, columns=["GTIN", "Product Name"])
    df.to_excel("results.xlsx", index=False)
    print(f"Iš viso surasta {len(results)} unikalių rezultatų.")
    print(df)
if __name__ == "__main__":
    gtin = get_gtin()
    results = scrape_all_pages(gtin)
    save_results_to_excel(results)
