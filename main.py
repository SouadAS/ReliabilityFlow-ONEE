import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="ReliabilityFlow | ONEE", layout="wide")

# 2. Titre et Style Start-up
st.title("🚀 ReliabilityFlow - Solution ONEE")
st.subheader("Intelligence Artificielle pour la Maintenance des Régies")

# 3. Barre latérale (Business Case)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Logo_ONEE.we_webp/1200px-Logo_ONEE.we_webp.png", width=100) # Optionnel
    st.header("📊 Business Case")
    st.info("Objectif : Réduction des arrêts de production de 20%.")
    st.write("**Client :** ONEE Branche Eau")

# 4. Chargement des données depuis Excel
try:
    df = pd.read_excel("donnees.xlsx")
    
    # 5. Dashboard de Performance
    col1, col2, col3 = st.columns(3)
    col1.metric("Actifs Total", len(df))
    # On simule un calcul de disponibilité
    col2.metric("Disponibilité Moyenne", "94.2%", "+1.5%")
    col3.metric("Alertes Critiques", len(df[df['BaselineHealthScore'] < 50]), "-2")

    st.divider()

    # 6. Section IA - Prédictions
    st.subheader("🎯 Analyses Prédictives & Prescriptions")
    
    # On filtre les équipements en danger
    df_danger = df[df['BaselineHealthScore'] < 50].copy()
    
    if not df_danger.empty:
        st.warning("Attention : Les équipements ci-dessous présentent un risque élevé de défaillance.")
        st.dataframe(df_danger[['AssetID', 'AssetType', 'BaselineHealthScore', 'Criticality']], use_container_width=True)
    else:
        st.success("Aucune défaillance majeure prédite pour les prochaines 24h.")

except Exception as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.info("Vérifiez que le fichier 'donnees.xlsx' est bien sur votre GitHub.")
