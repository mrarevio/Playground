import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
 
# --- Konfiguration ---
USER_AGENT = UserAgent()
REQUEST_DELAY = (10, 25)  # Deutlich längere Wartezeiten (10-25 Sekunden)
MAX_RETRIES = 2           # Weniger Wiederholungsversuche
TIMEOUT = 30              # Längere Timeouts
 
# --- Produktliste ---
PRODUCTS = {
    "RTX 5070 Ti": {
        "Gainward RTX 5070 Ti": "https://geizhals.at/gainward-geforce-rtx-5070-ti-v186843.html",
        "MSI RTX 5070 Ti": "https://geizhals.at/msi-geforce-rtx-5070-ti-v186766.html",
        # Weitere Produkte
    },
    "RTX 5080": {
        "Palit GeForce RTX 5080 GamingPro V1": "https://geizhals.at/palit-geforce-rtx-5080-gamingpro-v1-ne75080019t2-gb2031y-a3487808.html",
        "Zotac GeForce RTX 5080": "https://geizhals.at/zotac-geforce-rtx-5080-v186817.html",
        # Weitere Produkte
    }
}
 
# --- Verbesserte Scraping-Funktion mit Selenium ---
def scrape_price(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Hintergrunderstellung (ohne UI)
    options.add_argument(f'user-agent={USER_AGENT.random}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    for attempt in range(MAX_RETRIES):
        try:
            # Zufällige Wartezeit
            delay = random.uniform(*REQUEST_DELAY) * (attempt + 1)
            time.sleep(delay)
 
            driver.get(url)
            time.sleep(5)  # Warten, um sicherzustellen, dass die Seite geladen ist
 
            # Preis extrahieren mit robustem Parsing
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price_element = (
                soup.find('span', class_='gh_price') or 
                soup.find('span', class_='price__value') or
                soup.find('strong', id='pricerange-min')
            )
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = float(price_text
                    .replace('€', '')
                    .replace('.', '')
                    .replace(',', '.'))
                return price
        except Exception as e:
            st.error(f"Versuch {attempt + 1} fehlgeschlagen: {str(e)}")
            continue
        finally:
            driver.quit()  # Schließe den Browser am Ende
 
    return None
 
# --- Hauptfunktion mit optimierter Logik ---
def main():
    st.title("🛒 GPU-Preis Tracker (Geizhals)")    
    # Nur 1 Produkt pro Durchlauf prüfen
    selected_product = st.selectbox(
        "Modell auswählen",
        list(PRODUCTS["RTX 5080"].items()),
        format_func=lambda x: x[0]
    )
    if st.button("Preis prüfen", type="primary"):
        with st.spinner("Scrape läuft (bitte warten...)"):
            name, url = selected_product
            price = scrape_price(url)
            if price:
                st.success(f"✅ {name}: {price:.2f}€")
                # Daten speichern (für Streamlit Cloud angepasst)
                try:
                    data = {"product": name, "price": price, "date": datetime.now().isoformat()}
                    st.session_state.last_price = data
                    st.json(data)  # Debug-Ausgabe
                except Exception as e:
                    st.error(f"Speicherfehler: {str(e)}")
            else:
                st.warning(f"❌ {name}: Preis nicht verfügbar")
 
if __name__ == "__main__":
    main()
 
