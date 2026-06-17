import urllib.request
import feedparser
import os
import json
from google import genai
from google.genai import types

# --- CONFIGURATIE: DE BRONNENLIJST ---
BRONNEN = {
    "Public Domain Review": "https://publicdomainreview.org/feed/",
    "British Library Medieval": "https://blogs.bl.uk/manuscripts/atom.xml",
    "Atlas Obscura": "https://www.atlasobscura.com/feeds/latest",
    "DailyArt Magazine": "https://www.dailyartmagazine.com/feed/"
}

def haal_artikelen_multi_bron():
    alle_artikelen = []
    
    for bron_naam, rss_url in BRONNEN.items():
        print(f"🕵️ De Curator inspecteert {bron_naam}...")
        try:
            req = urllib.request.Request(
                rss_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                html_content = response.read()
            feed = feedparser.parse(html_content)
            
            teller = 0
            for entry in feed.entries:
                if teller >= 2:
                    break
                
                artikel = {
                    'titel': f"[{bron_naam}] {entry.get('title', 'Geen titel')}",
                    'link': entry.get('link', 'Geen link'),
                    'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))[:500]
                }
                alle_artikelen.append(artikel)
                teller += 1
                
        except Exception as e:
            print(f"❌ Fout bij ophalen van {bron_naam}: {e}")
            
    print(f"\nTotaal {len(alle_artikelen)} artikelen verzameld uit {len(BRONNEN)} bronnen.\n")
    return alle_artikelen

def beoordeel_met_gemini(artikelen):
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ Geen API sleutel gevonden!")
        return None
    
    client = genai.Client()
    print("🧠 Gemini weegt de obscuriteit van de verzamelde oogst...\n")
    
    artikelen_tekst = json.dumps(artikelen, indent=2)
    
    prompt = f"""
    Je bent De Nieuwsgierige Curator, een expert in obscure kunst en cultuurgeschiedenis.
    Beoordeel de volgende artikelen. Geef elk artikel een 'obscuriteits_score' van 1 tot 10.
    1 = Heel bekend/mainstream geschiedenis.
    10 = Extreem obscuur, bizar, of een totaal vergeten historisch feit/kunstwerk.
    
    Schrijf een korte, prikkelende samenvatting in het Nederlands van maximaal 2 zinnen.
    Behoud de bron-tag in de titel (bijvoorbeeld: [Atlas Obscura] Titel).
    
    Geef antwoord in dit exacte JSON formaat:
    {{
      "artikelen": [
        {{
          "titel": "Titel van het artikel inclusief de brontag",
          "obscuriteits_score": 8,
          "samenvatting": "Nederlandse samenvatting hier."
        }}
      ]
    }}
    
    Hier zijn de artikelen:
    {artikelen_tekst}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        # Vang serverfouten (zoals de 503) netjes op zonder te crashen
        print(f"⚠️ Google Gemini is momenteel overbelast of onbereikbaar. De robot probeert het bij de volgende run opnieuw. Details: {e}\n")
        return None

def sla_parels_op(beoordeling, originele_artikelen):
    if not beoordeling or "artikelen" not in beoordeling:
        print("ℹ️ Geen nieuwe beoordelingen om te verwerken.")
        return
        
    parels = []
    links_dict = {art['titel']: art['link'] for art in originele_artikelen}
    
    for art in beoordeling["artikelen"]:
        if art.get("obscuriteits_score", 0) >= 7:
            art["link"] = links_dict.get(art["titel"], "#")
            parels.append(art)
            
    bestandsnaam = "artikelen_database.json"
    bestaande_data = []
    
    if os.path.exists(bestandsnaam):
        with open(bestandsnaam, 'r', encoding='utf-8') as f:
            try:
                bestaande_data = json.load(f)
            except json.JSONDecodeError:
                bestaande_data = []
                
    bestaande_titels = {b['titel'] for b in bestaande_data}
    nieuwe_toevoegingen = [p for p in parels if p['titel'] not in bestaande_titels]
    
    eind_data = bestaande_data + nieuwe_toevoegingen
    
    with open(bestandsnaam, 'w', encoding='utf-8') as f:
        json.dump(eind_data, f, indent=2, ensure_ascii=False)
        
    print(f"📁 Database bijgewerkt! {len(nieuwe_toevoegingen)} nieuwe parels toegevoegd.")

if __name__ == "__main__":
    gevonden_artikelen = haal_artikelen_multi_bron()
    
    if gevonden_artikelen:
        ai_beoordeling = beoordeel_met_gemini(gevonden_artikelen)
        sla_parels_op(ai_beoordeling, gevonden_artikelen)
