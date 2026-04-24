import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration Pro
st.set_page_config(page_title="ReliabilityFlow Pro | ONEE", layout="wide", initial_sidebar_state="expanded")

# --- STYLE CSS POUR LE LOOK INDUSTRIEL ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.title("🛠️ ReliabilityFlow v2.0")
menu = st.sidebar.radio("Navigation", ["🏠 Accueil & Business Case", "📋 Parc Équipements", "📊 Dashboard KPI", "🧠 Prédictions IA", "📅 Plan de Maintenance"])

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_excel("donnees.xlsx")

df = load_data()

# --- SECTION 1 : ACCUEIL ---
if menu == "🏠 Accueil & Business Case":
    st.title("🌊 Digitalisation de la Maintenance - ONEE")
    st.image("https://images.unsplash.com/photo-1581094794329-c8112a89af12?auto=format&fit=crop&q=80&w=1000", caption="Infrastructure Industrielle Intelligente")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🎯 Notre Vision
        Transformer la maintenance réactive en **maintenance prescriptive**. 
        Grâce à l'IA, nous ne réparons plus les pannes, nous les empêchons d'arriver.
        """)
    with col2:
        st.info("**Business Case :**\n- Réduction des coûts : 25%\n- Augmentation de vie des actifs : +5 ans\n- Client cible : Régies d'eau et d'électricité.")

# --- SECTION 2 : EQUIPEMENTS ---
elif menu == "📋 Parc Équipements":
    st.title("📋 Audit du Parc d'Actifs")
    type_filter = st.multiselect("Filtrer par type :", options=df['AssetType'].unique(), default=df['AssetType'].unique())
    st.dataframe(df[df['AssetType'].isin(type_filter)], use_container_width=True)

# --- SECTION 3 : KPI ---
elif menu == "📊 Dashboard KPI":
    st.title("📊 Indicateurs de Performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Disponibilité Globale", "98.5%", "+0.5%")
    col2.metric("MTBF (Moyenne)", "450h", "-12h")
    col3.metric("Coût Maintenance", "1.2M DH", "-5%")
    
    fig = px.bar(df, x="AssetType", y="BaselineHealthScore", color="Criticality", title="Santé moyenne par type d'équipement")
    st.plotly_chart(fig, use_container_width=True)

# --- SECTION 4 : PREDICTIONS IA ---
elif menu == "🧠 Prédictions IA":
    st.title("🧠 Intelligence Artificielle & Alertes")
    alert_level = st.slider("Seuil de risque (Health Score)", 0, 100, 50)
    df_alert = df[df['BaselineHealthScore'] < alert_level]
    
    if not df_alert.empty:
        st.error(f"⚠️ {len(df_alert)} ÉQUIPEMENTS EN RISQUE CRITIQUE")
        st.table(df_alert[['AssetID', 'AssetType', 'BaselineHealthScore', 'Criticality']])
    
    fig_scatter = px.scatter(df, x="InstallationDate", y="BaselineHealthScore", color="Criticality", size="BaselineHealthScore")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- SECTION 5 : PLAN DE MAINTENANCE ---
elif menu == "📅 Plan de Maintenance":
    st.title("📅 Planning de Maintenance Prescriptive")
    st.write("Basé sur l'IA, voici les interventions prioritaires pour la semaine prochaine :")
    st.success("1. Pompe P-042 : Remplacement des roulements (Probabilité de panne : 88%)")
    st.warning("2. Vanne V-12 : Lubrification préventive")
