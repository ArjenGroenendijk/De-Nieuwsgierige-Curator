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
    # We pakken er 5 om te testen
    for entry in feed.entries[:5]:
        artikel = {
            'titel': entry.get('title', 'Geen titel'),
            'link': entry.get('link', 'Geen link'),
            'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))[:500]
        }
        artikelen_lijst.append(artikel)
    return artikelen_lijst

def beoordeel_met_gemini(artikelen):
    # Controleer of de API-key aanwezig is
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ Geen API sleutel gevonden! Vul de GEMINI_API_KEY in je terminal in.")
        return
    
    # Initialiseer de Gemini Client (pakt automatisch de GEMINI_API_KEY uit de omgeving)
    client = genai.Client()
    print("De Curator leest de verhalen en velt een oordeel via Google Gemini...\n")
    
    artikelen_tekst = json.dumps(artikelen, indent=2)
    
    prompt = f"""
    Je bent De Nieuwsgierige Curator, een expert in obscure kunstgeschiedenis.
    Beoordeel de volgende artikelen. Geef elk artikel een 'obscuriteits_score' van 1 tot 10.
    1 = Mainstream (bijv. Vincent van Gogh, Leonardo da Vinci, Rembrandt).
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
    
    # We roepen Gemini aan en dwingen een JSON-output af
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    # Print het resultaat netjes uit
    beoordeling = json.loads(response.text)
    print(json.dumps(beoordeling, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    kunst_feed_url = "https://publicdomainreview.org/feed/"
    gevonden_artikelen = haal_artikelen_op(kunst_feed_url)
    
    if gevonden_artikelen:
        beoordeel_met_gemini(gevonden_artikelen)
