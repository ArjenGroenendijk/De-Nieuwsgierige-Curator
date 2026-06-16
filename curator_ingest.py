import feedparser

def haal_artikelen_op(rss_url):
    print(f"De Curator struint het web af naar: {rss_url}...\n")
    
    # Parse de RSS feed
    feed = feedparser.parse(rss_url)
    
    # Controleer of er wel artikelen in de feed staan
    if not feed.entries:
        print("Oeps, de feed lijkt leeg te zijn of de URL klopt niet.")
        return []
    
    print(f"Succes! {len(feed.entries)} artikelen gevonden. Hier zijn de top 5:\n")
    
    artikelen_lijst = []
    
    # We pakken de eerste 5 artikelen om mee te testen
    for entry in feed.entries[:5]:
        artikel = {
            'titel': entry.get('title', 'Geen titel'),
            'link': entry.get('link', 'Geen link'),
            # Sommige feeds gebruiken 'summary', anderen 'description'
            'ruwe_tekst': entry.get('summary', entry.get('description', 'Geen beschrijving'))
        }
        artikelen_lijst.append(artikel)
        
    return artikelen_lijst

if __name__ == "__main__":
    # De RSS feed van The Public Domain Review (perfect voor obscure kunsthistorie)
    kunst_feed_url = "https://publicdomainreview.org/feed.xml"
    
    gevonden_artikelen = haal_artikelen_op(kunst_feed_url)
    
    # Toon de resultaten netjes in de terminal
    for index, art in enumerate(gevonden_artikelen, 1):
        print(f"--- [{index}] {art['titel']} ---")
        print(f"Link: {art['link']}")
        # We kappen de ruwe tekst af op 150 tekens voor het overzicht
        print(f"Ruwe tekst (fragment): {art['ruwe_tekst'][:150]}...")
        print("-" * 40 + "\n")
