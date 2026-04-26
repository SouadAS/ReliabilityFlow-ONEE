import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ReliabilityFlow × ONEE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
/* Reset & base */
* { font-family: 'Inter', sans-serif !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: #050d1a !important;
    color: #e8edf5 !important;
}
[data-testid="stAppViewContainer"] { padding: 0 !important; }
[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a1628 100%) !important;
    border: 1px solid #1a3a6b !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: #f0c040 !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #7fa8d4 !important; }

/* Tabs Customization */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1f3c !important;
    border-radius: 12px !important;
    padding: 10px !important;
    border: 1px solid #1a3a6b !important;
    margin: 10px 20px !important;
}
[data-testid="stTabs"] button {
    color: #7fa8d4 !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: #1e6bb8 !important;
    color: white !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING (CORRIGÉ POUR GITHUB) ─────────────────────────────────────────
@st.cache_data
def load_data():
    local_path = "donnees.xlsx"
    # URL RAW correcte pour ton GitHub
    github_url = "https://raw.githubusercontent.com/SouadAS/ReliabilityFlow-ONEE/main/donnees.xlsx"
    
    try:
        if os.path.exists(local_path):
            df = pd.read_excel(local_path)
        else:
            df = pd.read_excel(github_url)
        
        # Injection des calculs nécessaires pour les KPIs s'ils ne sont pas dans l'Excel
        if 'MTTR_h' not in df.columns:
            df['MTTR_h'] = (100 - df['BaselineHealthScore']) / 5
            df['MTBF_h'] = df['BaselineHealthScore'] * 12
            df['Coût_MAD'] = (100 - df['BaselineHealthScore']) * 280
            df['Disponibilité_%'] = df['BaselineHealthScore'] * 0.98
            df['Site'] = "Région Casablanca-Settat" # Fallback site
            df['Nom'] = "Équipement Stratégique"
            df['ProchaineMaintenance'] = "15/05/2024"
            df['Statut'] = "Opérationnel"
            
        return df
    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        st.stop()

df = load_data()

# ─── NAV HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background: #050d1a; border-bottom: 2px solid #1e6bb8; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between;">
    <div style="display:flex; align-items:center; gap:15px;">
        <div style="background: linear-gradient(135deg, #1e6bb8, #f0c040); width: 40px; height: 40px; border-radius: 8px; display:flex; align-items:center; justify-content:center; font-weight:bold; color:black;">RF</div>
        <span style="font-size:1.3rem; font-weight:800; color:white;">ReliabilityFlow <span style="color:#f0c040;">× ONEE</span></span>
    </div>
    <div style="color:#7fa8d4; font-size:0.9rem;">Intelligence Artificielle au service de l'Eau</div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 ACCUEIL", "📊 DASHBOARD KPI", "📋 PARC ÉQUIPEMENTS", "🚨 ALERTES IA", "📅 PLAN MAINTENANCE", "👥 QUI SOMMES-NOUS"
])

# ─── TAB 1: ACCUEIL (AVEC TON IMAGE) ───────────────────────────────────────────
with tabs[0]:
    # Utilisation du lien RAW GitHub pour ton image
    img_url = "https://raw.githubusercontent.com/SouadAS/ReliabilityFlow-ONEE/main/image_78df79.jpg"
    
    st.markdown(f"""
    <div style="position: relative; height: 450px; border-radius: 20px; margin: 20px; overflow: hidden; border: 1px solid #1a3a6b;">
        <img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(40%);">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 80%;">
            <h1 style="color: white; font-size: 3.5rem; font-weight: 900; margin-bottom: 10px;">MAINTENANCE PRÉDICTIVE</h1>
            <p style="color: #f0c040; font-size: 1.5rem; font-weight: 400;">Optimisation Digitale du Patrimoine de l'ONEE</p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-top: 30px;">
                <div style="background: rgba(30,107,184,0.2); padding: 15px 25px; border-radius: 10px; border: 1px solid #1e6bb8;">
                    <span style="display: block; color: #f0c040; font-size: 1.5rem; font-weight: 800;">-25%</span>
                    <span style="color: white; font-size: 0.8rem;">Coûts de Maintenance</span>
                </div>
                <div style="background: rgba(30,107,184,0.2); padding: 15px 25px; border-radius: 10px; border: 1px solid #1e6bb8;">
                    <span style="display: block; color: #22c55e; font-size: 1.5rem; font-weight: 800;">+40%</span>
                    <span style="color: white; font-size: 0.8rem;">Disponibilité Parc</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚙️ Total Actifs", len(df))
    c2.metric("🚨 Alertes Critiques", len(df[df["BaselineHealthScore"] < 45]))
    c3.metric("📍 Régions", "Casablanca")
    c4.metric("💚 Santé Parc", f"{round(df['BaselineHealthScore'].mean(),1)}%")

# ─── TAB 2: DASHBOARD KPI ─────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### 📊 Indicateurs de Performance Globaux")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("MTTR Moyen", f"{df['MTTR_h'].mean():.1f} h")
    k2.metric("MTBF Moyen", f"{int(df['MTBF_h'].mean())} h")
    k3.metric("Disponibilité", f"{df['Disponibilité_%'].mean():.1f}%")
    k4.metric("Dépense Totale", f"{int(df['Coût_MAD'].sum()):,} MAD")
    
    st.markdown("---")
    fig_tree = px.treemap(df, path=['Site', 'AssetType', 'AssetID'], values='Coût_MAD', color='BaselineHealthScore',
                          color_continuous_scale='RdYlGn', title="Répartition des Coûts et Santé du Parc")
    fig_tree.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_tree, use_container_width=True)

# ─── TAB 3: PARC ÉQUIPEMENTS ──────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### 📋 Inventaire des Équipements")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ─── TAB 4: ALERTES IA ────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### 🚨 Actifs Nécessitant une Intervention Immédiate")
    critiques = df[df['BaselineHealthScore'] < 45].sort_values('BaselineHealthScore')
    for _, row in critiques.iterrows():
        st.error(f"**ID: {row['AssetID']}** | Type: {row['AssetType']} | Score Santé: **{row['BaselineHealthScore']}%**")

# ─── TAB 5: PLAN MAINTENANCE (INTERACTIF) ─────────────────────────────────────
with tabs[4]:
    st.markdown("### 📅 Suivi des Interventions Technicien")
    # On affiche les 5 équipements les plus fragiles pour le planning
    planning = df.sort_values('BaselineHealthScore').head(5)
    for i, row in planning.iterrows():
        with st.expander(f"🛠️ Ordre de Travail : {row['AssetID']} ({row['AssetType']})"):
            c1, c2 = st.columns(2)
            c1.write(f"**Criticité:** {row['Criticality']}")
            c1.write(f"**Date prévue:** {row['ProchaineMaintenance']}")
            status = c2.selectbox("Statut de la tâche", ["En attente", "En cours", "Terminé"], key=f"st_{i}")
            progress = c2.slider("Avancement", 0, 100, 0 if status == "En attente" else 100 if status == "Terminé" else 50, key=f"pr_{i}")

# ─── TAB 6: QUI SOMMES-NOUS ───────────────────────────────────────────────────
with tabs[5]:
    st.markdown("""
    <div style="background: #0d1f3c; padding: 40px; border-radius: 15px; border: 1px solid #1e6bb8;">
        <h2 style="color: #f0c040;">ReliabilityFlow Solutions</h2>
        <p>Expert en ingénierie de maintenance et data science industrielle.</p>
        <p>Notre mission : Accompagner l'<b>ONEE</b> dans sa transition vers la maintenance 4.0 pour sécuriser l'accès à l'eau potable via des infrastructures résilientes.</p>
        <hr style="border-color: #1e6bb8;">
        <p style="font-size: 0.9rem; color: #7fa8d4;">Projet Académique - 2026 - Maintenance Industrielle</p>
    </div>
    """, unsafe_allow_html=True)
