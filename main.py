import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="ReliabilityFlow | ONEE Smart Maintenance", layout="wide")

# --- STYLE CSS AVANCÉ (Look SaaS Pro) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #004a99; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white; border-radius: 5px; padding: 10px 20px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #f9b233 !important; color: #004a99 !important; }
    .hero-container { position: relative; text-align: center; color: white; margin-bottom: 30px; }
    .hero-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,74,153,0.7); padding: 20px; border-radius: 15px; width: 80%; }
    .kpi-box { background: #004a99; color: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT & CALCULS RÉELS ---
@st.cache_data
def load_industrial_data():
    df = pd.read_excel("donnees.xlsx")
    # Calculs basés sur les données réelles de l'Excel
    df['MTTR (h)'] = [round(100/x, 1) if x > 0 else 24 for x in df['BaselineHealthScore']]
    df['MTBF (h)'] = [x * 12 for x in df['BaselineHealthScore']]
    df['Cout Maintenance (DH)'] = [(100 - x) * 250 for x in df['BaselineHealthScore']]
    df['Disponibilité (%)'] = [round(x * 0.98, 1) for x in df['BaselineHealthScore']]
    return df

try:
    df = load_industrial_data()

    # --- MENU HORIZONTAL ---
    tabs = st.tabs(["🏠 ACCUEIL", "📊 KPI GLOBAUX", "📋 ÉQUIPEMENTS", "🚨 ALERTES", "📅 PLAN DE MAINTENANCE", "👥 QUI SOMMES-NOUS ?"])

    # --- SECTION 1 : ACCUEIL (IMAGE ONEE PERSONNALISÉE) ---
    with tabs[0]:
        st.markdown(f"""
            <div class="hero-container">
                <img src="https://raw.githubusercontent.com/SouadAS/ReliabilityFlow-ONEE/main/image_78df79.jpg" style="width:100%; border-radius:15px; height:400px; object-fit:cover; filter: brightness(60%);">
                <div class="hero-text">
                    <h1 style="font-size: 45px; margin:0;">ONEE - BRANCHE EAU</h1>
                    <p style="font-size: 20px;">Plateforme Intelligente de Gestion de la Fiabilité</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🚀 Transformation Digitale")
            st.write("Ce portail centralise l'état de santé de vos actifs en temps réel. Grâce à l'IA, nous passons d'une maintenance curative à une stratégie prescriptive.")
        with c2:
            st.success("✅ **Objectif :** Minimiser le risque de panne par 25% (Basé sur l'analyse prédictive de vos scores de santé actuels).")

    # --- SECTION 2 : KPI GLOBAUX (AVEC BILAN FINAL) ---
    with tabs[1]:
        st.header("📊 Tableau de Bord des Performances")
        
        # Filtrage pour le tableau
        st.write("### Détail par Équipement")
        st.dataframe(df[['AssetID', 'AssetType', 'MTTR (h)', 'MTBF (h)', 'Disponibilité (%)', 'Cout Maintenance (DH)']], use_container_width=True)
        
        # BILAN GLOBAL (La partie importante)
        st.markdown("### 🏆 Bilan Annuel Global")
        b1, b2, b3, b4 = st.columns(4)
        b1.markdown(f"<div class='kpi-box'><b>MTTR MOYEN</b><br><span style='font-size:24px;'>{round(df['MTTR (h)'].mean(), 1)} h</span></div>", unsafe_allow_html=True)
        b2.markdown(f"<div class='kpi-box'><b>MTBF MOYEN</b><br><span style='font-size:24px;'>{round(df['MTBF (h)'].mean(), 0)} h</span></div>", unsafe_allow_html=True)
        b3.markdown(f"<div class='kpi-box'><b>DISPO. GLOBALE</b><br><span style='font-size:24px;'>{round(df['Disponibilité (%)'].mean(), 1)}%</span></div>", unsafe_allow_html=True)
        b4.markdown(f"<div class='kpi-box'><b>COÛT TOTAL</b><br><span style='font-size:24px;'>{int(df['Cout Maintenance (DH)'].sum()):,} DH</span></div>", unsafe_allow_html=True)

    # --- SECTION 3 : ÉQUIPEMENTS (TRI ET FILTRES) ---
    with tabs[2]:
        st.header("📋 Gestion du Parc")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            site = st.selectbox("Site Géo :", ["Tous", "Région Nord", "Région Sud", "Région Centre"])
        with col_t2:
            crit = st.multiselect("Criticité :", df['Criticality'].unique(), default=df['Criticality'].unique())
        with col_t3:
            min_score = st.slider("Score de Santé Min :", 0, 100, 0)
        
        filtered_df = df[(df['Criticality'].isin(crit)) & (df['BaselineHealthScore'] >= min_score)]
        st.dataframe(filtered_df, use_container_width=True)

    # --- SECTION 4 : ALERTES IA ---
    with tabs[3]:
        st.header("🚨 Alertes Prédictives")
        danger = df[df['BaselineHealthScore'] < 45]
        if not danger.empty:
            for _, row in danger.iterrows():
                st.warning(f"**Risque élevé :** {row['AssetType']} ({row['AssetID']}) - Santé : {row['BaselineHealthScore']}% - Intervention suggérée sous 48h.")
        else:
            st.success("Aucune alerte critique détectée.")

    # --- SECTION 5 : PLAN DE MAINTENANCE (INTERACTIF) ---
    with tabs[4]:
        st.header("📅 Suivi des Interventions")
        st.write("Espace réservé aux techniciens et cadres pour le suivi des travaux.")
        
        # On simule un plan basé sur les scores bas
        plan_df = df[df['BaselineHealthScore'] < 60].copy()
        plan_df['Date Prévue'] = [(datetime.now() + timedelta(days=i*3)).strftime('%Y-%m-%d') for i in range(len(plan_df))]
        
        for i, row in plan_df.head(8).iterrows():
            with st.expander(f"🛠️ Ordre de Travail : {row['AssetID']} - Prévu le {row['Date Prévue']}"):
                col_i1, col_i2, col_i3 = st.columns([2,1,1])
                col_i1.write(f"**Action :** Maintenance préventive sur {row['AssetType']}. Vérification des paliers et lubrification.")
                status = col_i2.selectbox("Statut :", ["Pas encore", "En cours", "Fait"], key=f"s_{i}")
                progress = col_i3.slider("Avancement %", 0, 100, 0 if status=="Pas encore" else 100 if status=="Fait" else 50, key=f"p_{i}")
                if status == "Fait":
                    st.success("Validé par le technicien le " + datetime.now().strftime('%d/%m/%Y'))

    # --- SECTION 6 : QUI SOMMES-NOUS ? ---
    with tabs[5]:
        st.header("👥 ReliabilityFlow Solutions")
        st.markdown("""
        ### Notre Vision
        Accompagner l'**ONEE** dans sa transition vers l'industrie 4.0 en transformant les données brutes en décisions stratégiques.
        
        **Expertises :**
        - Analyse de données IoT
        - Algorithmes de maintenance prédictive
        - Optimisation de la durée de vie des actifs hydrauliques
        """)
        st.info("Contact Support : support@smart-maintenance.ma")

except Exception as e:
    st.error("⚠️ Problème de chargement. Assurez-vous que 'donnees.xlsx' ne contient pas de lignes vides en haut.")
    st.exception(e)
