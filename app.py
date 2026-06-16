import streamlit as dict_streamlit
import json
import os

# Zet de paginastructuur op
dict_streamlit.set_page_config(page_title="De Nieuwsgierige Curator", page_icon="🎨", layout="centered")

# Strakke titel en intro
dict_streamlit.title("🎨 De Nieuwsgierige Curator")
dict_streamlit.subheader("Jouw gids door de meest obscure uithoeken van de kunstgeschiedenis.")
dict_streamlit.markdown("---")

bestandsnaam = "artikelen_database.json"

# Controleer of we al data hebben
if not os.path.exists(bestandsnaam):
    dict_streamlit.info("De database is nog leeg. Draai eerst `curator_ingest.py` om verhalen te verzamelen!")
else:
    with open(bestandsnaam, 'r', encoding='utf-8') as f:
        artikelen = json.load(f)
        
    if not artikelen:
        dict_streamlit.warning("Er zijn nog geen parels gevonden met een score van 7 of hoger.")
    else:
        # Sorteer de artikelen zodat de allerhoogste scores bovenaan staan
        artikelen_gesorteerd = sorted(artikelen, key=lambda x: x.get('obscuriteits_score', 0), reverse=True)
        
        # Laat de parels zien
        for art in artikelen_gesorteerd:
            score = art.get('obscuriteits_score', 0)
            
            # Een leuke visuele indicator voor de score
            score_badge = "🔥" * (score - 6) if score > 7 else "✨"
            
            # Toon het artikel in een mooi 'kaartje'
            with dict_streamlit.container():
                dict_streamlit.markdown(f"### {art['titel']}")
                dict_streamlit.markdown(f"**Curator Score:** {score}/10 {score_badge}")
                dict_streamlit.write(art['samenvatting'])
                
                # Een strakke link naar het originele artikel
                dict_streamlit.link_button("Lees het hele verhaal", art['link'])
                dict_streamlit.markdown("---")
