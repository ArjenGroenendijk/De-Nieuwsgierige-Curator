import urllib.request
import feedparser
import os
import json
from openai import OpenAI

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
    # We pakken er 3 om API-tegoed te besparen tijdens het testen
    for entry in feed.entries[:3]:
        artikel = {
            'titel': entry.get('title', 'Geen titel'),
            'link': entry.get('link', 'Geen link'),
            'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))[:500] # Eerste 500 tekens is genoeg
        }
        artikelen_lijst.append(artikel)
    return artikelen_lijst

def beoordeel_met_ai(artikelen):
    # De client zoekt automatisch naar de omgevingsvariabele 'OPENAI_API_KEY'
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️ Geen API sleutel gevonden! Vul de OPENAI_API_KEY in je terminal in.")
        return
    
    client = OpenAI()
    print("De Curator leest de verhalen en velt een oordeel...\n")
    
    # We bereiden de tekst voor die we naar de AI sturen
    artikelen_tekst = json.dumps(artikelen, indent=2)
    
    prompt = f"""
    Je bent De Nieuwsgierige Curator, een expert in obscure kunstgeschiedenis.
    Beoordeel de volgende artikelen. Geef elk artikel een 'obscuriteits_score' van 1 tot 10.
    1 = Mainstream (bijv. Vincent van Gogh, Leonardo da Vinci, Rembrandt).
    10 = Extreem obscuur, bizar of een vergeten historisch feit.
    
    Schrijf ook een korte, prikkelende samenvatting in het Nederlands van max 2 zinnen.
    
    Geef ALTIJD antwoord in dit exacte JSON formaat:
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
    
    # We vragen de AI om een gestructureerd JSON antwoord
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Lekker goedkoop en snel voor een MVP
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Print het eindoordeel
    beoordeling = json.loads(response.choices[0].message.content)
    print(json.dumps(beoordeling, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    kunst_feed_url = "https://publicdomainreview.org/feed/"
    gevonden_artikelen = haal_artikelen_op(kunst_feed_url)
    
    if gevonden_artikelen:
        beoordeel_met_ai(gevonden_artikelen)
