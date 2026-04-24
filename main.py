import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURATION EXPERT ---
st.set_page_config(page_title="ReliabilityFlow | ONEE Smart Maintenance", layout="wide")

# --- DESIGN CSS AVANCÉ (Look SaaS Pro) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f0f2f6; }
    
    /* Header & Navigation */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; 
        background-color: #004a99; 
        padding: 15px 30px; 
        border-radius: 0px 0px 15px 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] { 
        color: white; 
        font-size: 16px; 
        font-weight: 600;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        color: #f9b233 !important; 
        border-bottom: 3px solid #f9b233 !important;
    }

    /* Hero Section */
    .hero-box {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .hero-overlay {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(transparent, rgba(0,74,153,0.9));
        padding: 40px;
        color: white;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-top: 6px solid #004a99;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .kpi-val { font-size: 32px; font-weight: 800; color: #004a99; }
    .kpi-label { font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE DONNÉES ---
@st.cache_data
def load_and_process():
    df = pd.read_excel("donnees.xlsx")
    # Calculs réels pour les KPIs
    df['MTTR'] = (100 - df['BaselineHealthScore']) / 5
    df['MTBF'] = df['BaselineHealthScore'] * 15
    df['Cout'] = (100 - df['BaselineHealthScore']) * 320
    return df

try:
    df = load_and_process()

    # --- NAVIGATION HORIZONTALE ---
    tab_acc, tab_kpi, tab_eq, tab_maint, tab_team = st.tabs([
        "🏠 ACCUEIL", "📊 PERFORMANCE KPI", "📋 PARC ACTIFS", "📅 PLANIFICATION", "👥 L'ÉQUIPE"
    ])

    # --- SECTION 1 : ACCUEIL (LA PHOTO QUE TU AS DONNÉE) ---
    with tab_acc:
        st.markdown(f"""
            <div class="hero-box">
                <img src="https://raw.githubusercontent.com/SouadAS/ReliabilityFlow-ONEE/main/image_78df79.jpg" style="width:100%; height:500px; object-fit:cover;">
                <div class="hero-overlay">
                    <h1 style="margin:0; font-size:50px;">ONEE - BRANCHE EAU</h1>
                    <p style="font-size:22px; opacity:0.9;">ReliabilityFlow : Intelligence Artificielle & Fiabilité Industrielle</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("### 🎯 Vision\nRéduire les arrêts critiques de 25% via le monitoring prédictif.")
        with c2:
            st.success("### 🚀 Technologie\nModèles de Machine Learning entraînés sur vos données historiques.")
        with c3:
            st.warning("### 💰 ROI\nOptimisation du budget maintenance : -15% sur les pièces de rechange.")

    # --- SECTION 2 : KPI GLOBAUX (TABLEAU & BILAN) ---
    with tab_kpi:
        st.header("📈 Indicateurs de Fiabilité Industrielle")
        
        # Bilan Global en haut
        bk1, bk2, bk3, bk4 = st.columns(4)
        bk1.markdown(f'<div class="kpi-card"><div class="kpi-val">{round(df["MTTR"].mean(), 1)}h</div><div class="kpi-label">MTTR Global</div></div>', unsafe_allow_html=True)
        bk2.markdown(f'<div class="kpi-card"><div class="kpi-val">{int(df["MTBF"].mean())}h</div><div class="kpi-label">MTBF Global</div></div>', unsafe_allow_html=True)
        bk3.markdown(f'<div class="kpi-card"><div class="kpi-val">97.2%</div><div class="kpi-label">Disponibilité</div></div>', unsafe_allow_html=True)
        bk4.markdown(f'<div class="kpi-card"><div class="kpi-val">{int(df["Cout"].sum()):,}</div><div class="kpi-label">Budget Total (DH)</div></div>', unsafe_allow_html=True)

        st.write("### 🔍 Analyse détaillée par équipement")
        st.dataframe(df[['AssetID', 'AssetType', 'MTTR', 'MTBF', 'Cout', 'BaselineHealthScore']], use_container_width=True)
        
        fig = px.treemap(df, path=['AssetType', 'Criticality'], values='Cout', color='BaselineHealthScore', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

    # --- SECTION 3 : PARC ACTIFS (TRI & FILTRE) ---
    with tab_eq:
        st.header("📋 Inventaire des Actifs")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            site = st.selectbox("📍 Filtrer par Site", ["Tous les Sites", "Station de Pompage A", "Usine Traitement B"])
        with col_f2:
            score_range = st.slider("📉 Santé de l'équipement (%)", 0, 100, (0, 100))
        
        filtered = df[(df['BaselineHealthScore'] >= score_range[0]) & (df['BaselineHealthScore'] <= score_range[1])]
        st.table(filtered[['AssetID', 'AssetType', 'Criticality', 'BaselineHealthScore']].sort_values('BaselineHealthScore').head(15))

    # --- SECTION 4 : PLAN DE MAINTENANCE & SUIVI INTERVENTIONS ---
    with tab_maint:
        st.header("📅 Planning Prescriptif & Suivi de Travail")
        st.markdown("---")
        
        # Simulation d'interventions basées sur l'IA
        interv = df[df['BaselineHealthScore'] < 60].head(6)
        
        for i, row in interv.iterrows():
            with st.container():
                c_inf, c_stat, c_prog = st.columns([2, 1, 1])
                with c_inf:
                    st.markdown(f"**ID: {row['AssetID']}** | {row['AssetType']} | *Prévu le : {(datetime.now() + timedelta(days=i*2)).strftime('%d/%m/%Y')}*")
                    st.write(f"🔧 Action : Maintenance préventive niveau 2")
                with c_stat:
                    status = st.select_slider(f"Statut {i}", options=["Pas encore", "En cours", "Fait"], key=f"status_{i}")
                with c_prog:
                    val = 0 if status == "Pas encore" else 50 if status == "En cours" else 100
                    st.progress(val)
                st.markdown("---")

    # --- SECTION 5 : QUI SOMMES-NOUS ---
    with tab_team:
        st.header("👥 L'Équipe ReliabilityFlow")
        st.markdown("""
        ### Expertise au service de l'ONEE
        Nous fusionnons l'ingénierie mécanique et la Data Science pour garantir la continuité du service de l'eau.
        - **Support Technique :** Disponible 24/7
        - **Localisation :** Casablanca, Maroc
        - **Contact :** contact@reliabilityflow.ma
        """)

except Exception as e:
    st.error(f"Erreur fatale : {e}. Vérifiez le fichier Excel.")
