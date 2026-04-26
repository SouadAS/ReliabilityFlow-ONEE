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

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a1628; }
::-webkit-scrollbar-thumb { background: #1e6bb8; border-radius: 3px; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a1628 100%) !important;
    border: 1px solid #1a3a6b !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: #f0c040 !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #7fa8d4 !important; }

/* Tabs */
[data-testid="stTabs"] button {
    background: transparent !important;
    color: #7fa8d4 !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #1e6bb8, #1a5a9e) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(30,107,184,0.4) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1f3c !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid #1a3a6b !important;
    gap: 4px !important;
}

/* Selectbox / Multiselect */
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div {
    background: #0d1f3c !important;
    border: 1px solid #1a3a6b !important;
    border-radius: 8px !important;
    color: #e8edf5 !important;
}

/* Slider */
[data-testid="stSlider"] .stSlider > div { color: #f0c040 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1a3a6b !important; border-radius: 10px !important; }

/* Alerts */
.stAlert { border-radius: 10px !important; }

/* Divider */
hr { border-color: #1a3a6b !important; }

/* General button */
.stButton > button {
    background: linear-gradient(135deg, #1e6bb8, #f0c040) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #050d1a !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    local_path = "donnees.xlsx"
    if os.path.exists(local_path):
        # Utilisation de engine='openpyxl' pour éviter les erreurs d'import
        df = pd.read_excel(local_path, engine='openpyxl')
    else:
        st.error(f"❌ Le fichier `{local_path}` est introuvable à la racine du projet.")
        st.stop()
    return df

df = load_data()

# ─── NAV HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(90deg, #050d1a 0%, #0a1628 50%, #050d1a 100%);
    border-bottom: 2px solid #1e6bb8;
    padding: 0.8rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 999;
    backdrop-filter: blur(10px);
">
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="
            background: linear-gradient(135deg, #1e6bb8, #f0c040);
            width: 38px; height: 38px; border-radius: 8px;
            display:flex; align-items:center; justify-content:center;
            font-size:1.2rem; font-weight:900; color:#050d1a;
        ">⚡</div>
        <div>
            <span style="font-size:1.1rem; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">ReliabilityFlow</span>
            <span style="font-size:1.1rem; font-weight:300; color:#f0c040;"> × ONEE</span>
        </div>
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
        <span style="background:#22c55e22; color:#22c55e; border:1px solid #22c55e44;
                     padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:600;">
            ● SYSTÈME ACTIF
        </span>
        <span style="color:#7fa8d4; font-size:0.8rem;">Maintenance Prédictive IA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠  ACCUEIL",
    "📊  DASHBOARD KPI",
    "📋  PARC ÉQUIPEMENTS",
    "🚨  ALERTES IA",
    "📅  PLAN MAINTENANCE",
    "👥  QUI SOMMES-NOUS",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #050d1a 0%, #0a1e3d 40%, #0d2550 70%, #050d1a 100%);
        border: 1px solid #1a3a6b;
        border-radius: 20px;
        padding: 4rem 3rem;
        margin: 1.5rem 1rem;
        position: relative;
        overflow: hidden;
        text-align: center;
    ">
        <div style="position:absolute; inset: 0; background-image: linear-gradient(rgba(30,107,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(30,107,184,0.08) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none;"></div>
        <div style="position:relative; z-index:2;">
            <div style="display:inline-block; background: linear-gradient(135deg, #1e6bb844, #f0c04022); border: 1px solid #1e6bb866; border-radius: 30px; padding: 6px 20px; font-size: 0.8rem; font-weight: 600; color: #f0c040; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1.5rem;">Office National de l'Électricité et de l'Eau Potable</div>
            <h1 style="font-size: 3.5rem; font-weight: 900; color: #ffffff; line-height: 1.1; margin: 0 0 1rem 0; letter-spacing: -2px;">Maintenance Prédictive<br><span style="background: linear-gradient(90deg, #1e6bb8, #f0c040); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Pilotée par l'Intelligence Artificielle</span></h1>
            <p style="font-size: 1.15rem; color: #a0b8d8; max-width: 700px; margin: 0 auto 2.5rem; line-height: 1.7; font-weight: 400;">ReliabilityFlow transforme vos données industrielles brutes en <strong style="color:#f0c040;">décisions stratégiques prescriptives</strong> — anticipez les pannes, optimisez vos ressources et garantissez la continuité de service sur l'ensemble du parc ONEE.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("⚙️ Équipements", len(df))
    with c2: st.metric("🚨 Alertes Critiques", len(df[df["BaselineHealthScore"] < 45]))
    with c3: st.metric("📍 Sites", df["Site"].nunique())
    with c4: st.metric("💚 Santé Moyenne", f"{df['BaselineHealthScore'].mean():.1f}/100")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD KPI
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Tableau de Bord KPI")
    
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("MTTR (h)", f"{df['MTTR_h'].mean():.1f}")
    g2.metric("MTBF (h)", f"{df['MTBF_h'].mean():.0f}")
    g3.metric("Disponibilité", f"{df['Disponibilité_%'].mean():.1f}%")
    g4.metric("Budget (MAD)", f"{df['Coût_MAD'].sum()/1e6:.1f}M")

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PARC ÉQUIPEMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div style='padding:1.5rem 1rem;'>", unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    sites = f1.multiselect("Filtrer par Site", df["Site"].unique(), default=df["Site"].unique())
    df_filt = df[df["Site"].isin(sites)]
    st.dataframe(df_filt, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTES IA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div style='padding:1.5rem 1rem;'>", unsafe_allow_html=True)
    df_alerts = df[df["BaselineHealthScore"] < 45]
    if df_alerts.empty:
        st.success("✅ Aucun équipement critique.")
    else:
        for _, row in df_alerts.iterrows():
            st.warning(f"⚠️ **{row['AssetID']}** ({row['Nom']}) - Score: {row['BaselineHealthScore']}/100")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PLAN MAINTENANCE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.info("Planification en cours basée sur les scores de santé...")
    st.table(df[["AssetID", "ProchaineMaintenance", "Statut"]].head(10))

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — QUI SOMMES-NOUS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1f3c, #0a1628); border: 1px solid #1a3a6b; border-radius: 14px; padding: 2rem; margin: 1rem;">
        <h2 style='color:#ffffff;'>ReliabilityFlow × ONEE</h2>
        <p style='color:#a0b8d8;'>Projet académique de maintenance industrielle pilotée par l'IA.</p>
    </div>
    """, unsafe_allow_html=True)
