import streamlit as st
import json
import os

st.set_page_config(page_title="De Nieuwsgierige Curator", page_icon="🎨", layout="centered")

st.title("🏛️ De Nieuwsgierige Curator")
st.subheader("Jouw wekelijkse dosis obscure kunst & cultuurgeschiedenis")

bestandsnaam = "artikelen_database.json"

if os.path.exists(bestandsnaam):
    with open(bestandsnaam, "r", encoding="utf-8") as f:
        artikelen = json.load(f)
    
    # Sorteer op de hoogste score
    artikelen = sorted(artikelen, key=lambda x: x.get('obscuriteits_score', 0), reverse=True)
    
    if not artikelen:
        st.info("De database is nog leeg. De robot is onderweg!")
    
    for art in artikelen:
        # Toon de schone titel
        st.markdown(f"### [{art.get('obscuriteits_score', 0)}/10] {art['titel']}")
        
        # Toon de bron als een elegant grijs sub-tekstje
        st.caption(f"🔍 Bron: {art.get('bron', 'Onbekende bron')} — [Lees het originele artikel]({art['link']})")
        
        # Toon de AI samenvatting
        st.write(art['samenvatting'])
        st.write("---")
else:
    st.info("Er is nog geen database gevonden. Start de robot een keer op via GitHub Actions!")
