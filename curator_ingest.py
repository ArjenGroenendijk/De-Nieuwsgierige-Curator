import urllib.request
import feedparser
import os
import json
from google import genai
from google.genai import types

def haal_artikelen_op(rss_url):
    print(f"De Curator struint het web af naar: {rss_url}...\n")
    try:
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            html_content = response.read()
        feed = feedparser.parse(html_content)
    except Exception as e:
        print(f"Er ging iets mis bij het ophalen: {e}")
        return []
    
    artikelen_lijst = []
    # We pakken er nu netjes 5
    for entry in feed.entries[:5]:
        artikel = {
            'titel': entry.get('title', 'Geen titel'),
            'link': entry.get('link', 'Geen link'),
            'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))[:500]
        }
        artikelen_lijst.append(artikel)
    return artikelen_lijst

def beoordeel_met_gemini(artikelen):
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ Geen API sleutel gevonden!")
        return None
    
    client = genai.Client()
    print("De Curator leest de verhalen en velt een oordeel via Google Gemini...\n")
    
    artikelen_tekst = json.dumps(artikelen, indent=2)
    
    prompt = f"""
    Je bent De Nieuwsgierige Curator, een expert in obscure kunstgeschiedenis.
    Beoordeel de volgende artikelen. Geef elk artikel een 'obscuriteits_score' van 1 tot 10.
    1 = Mainstream (bijv. Vincent van Gogh, Leonardo da Vinci).
    10 = Extreem obscuur, bizar of een vergeten historisch feit.
    
    Schrijf ook een korte, prikkelende samenvatting in het Nederlands van maximaal 2 zinnen.
    
    Geef antwoord in dit exacte JSON formaat:
    {{
      "artikelen": [
        {{
          "titel": "Titel van het artikel",
          "obscuriteits_score": 8,
          "samenvatting": "Nederlandse samenvatting hier."
        }}
      ]
    }}
    
    Hier zijn de artikelen:
    {artikelen_tekst}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    return json.loads(response.text)

def sla_parels_op(beoordeling, originele_artikelen):
    if not beoordeling or "artikelen" not in beoordeling:
        return
        
    parels = []
    
    # Maak een handige lookup om de originele link terug te vinden op basis van de titel
    links_dict = {art['titel']: art['link'] for art in originele_artikelen}
    
    # Filter de artikelen: we willen alleen de échte parels (score >= 7)
    for art in beoordeling["artikelen"]:
        if art.get("obscuriteits_score", 0) >= 7:
            # Voeg de originele link toe aan de AI-beoordeling
            art["link"] = links_dict.get(art["titel"], "#")
            parels.append(art)
            
    # Sla de parels op in een JSON bestand
    bestandsnaam = "artikelen_database.json"
    
    # Als het bestand al bestaat, laden we de oude data in zodat we niks overschrijven
    bestaande_data = []
    if os.path.exists(bestandsnaam):
        with open(bestandsnaam, 'r', encoding='utf-8') as f:
            try:
                bestaande_data = json.load(f)
            except json.JSONDecodeError:
                bestaande_data = []
                
    # Voeg alleen unieke nieuwe parels toe (check op basis van titel)
    bestaande_titels = {b['titel'] for b in bestaande_data}
    nieuwe_toevoegingen = [p for p in parels if p['titel'] not in bestaande_titels]
    
    eind_data = bestaande_data + nieuwe_toevoegingen
    
    with open(bestandsnaam, 'w', encoding='utf-8') as f:
        json.dump(eind_data, f, indent=2, ensure_ascii=False)
        
    print(f"📁 Database bijgewerkt! Er zijn {len(nieuwe_toevoegingen)} nieuwe parels opgeslagen in '{bestandsnaam}'.")

if __name__ == "__main__":
    kunst_feed_url = "https://publicdomainreview.org/feed/"
    gevonden_artikelen = haal_artikelen_op(kunst_feed_url)
    
    if gevonden_artikelen:
        ai_beoordeling = beoordeel_met_gemini(gevonden_artikelen)
        sla_parels_op(ai_beoordeling, gevonden_artikelen)
