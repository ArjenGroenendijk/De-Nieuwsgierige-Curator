import urllib.request
import feedparser

def haal_artikelen_op(rss_url):
    print(f"De Curator struint het web af naar: {rss_url}...\n")
    
    try:
        # We vermommen ons script als een normale internetbrowser (Chrome)
        # Zo voorkom de 'bot-blocker' van websites
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        # Open de URL en lees de data
        with urllib.request.urlopen(req) as response:
            html_content = response.read()
            
        # Geef de data aan feedparser
        feed = feedparser.parse(html_content)
        
    except Exception as e:
        print(f"Er ging iets mis bij het ophalen: {e}")
        return []
    
    if not feed.entries:
        print("De feed is succesvol opgehaald, maar bevat momenteel geen artikelen.")
        return []
        
    print(f"Succes! {len(feed.entries)} artikelen gevonden. Hier zijn de top 5:\n")
    
    artikelen_lijst = []
    for entry in feed.entries[:5]:
        artikel = {
            'titel': entry.get('title', 'Geen titel'),
            'link': entry.get('link', 'Geen link'),
            'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))
        }
        artikelen_lijst.append(artikel)
        
    return artikelen_lijst

if __name__ == "__main__":
    # We proberen de hoofdfreed van de site (zonder .xml aan het einde)
    kunst_feed_url = "https://publicdomainreview.org/feed/"
    
    gevonden_artikelen = haal_artikelen_op(kunst_feed_url)
    
    for index, art in enumerate(gevonden_artikelen, 1):
        print(f"--- [{index}] {art['titel']} ---")
        print(f"Link: {art['link']}")
        print(f"Ruwe tekst (fragment): {art['ruwe_tekst'][:150]}...")
        print("-" * 40 + "\n")
