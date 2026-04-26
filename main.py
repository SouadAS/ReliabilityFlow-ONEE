# -*- coding: utf-8 -*-

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

# ─── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    local_path = "donnees.xlsx"
    github_url = "https://raw.githubusercontent.com/SouadAS/ReliabilityFlow-ONEE/main/donnees.xlsx"

    try:
        if os.path.exists(local_path):
            df = pd.read_excel(local_path, engine="openpyxl")
        else:
            df = pd.read_excel(github_url, engine="openpyxl")
    except Exception as e:
        st.error(f"❌ Erreur de chargement des données: {e}")
        st.stop()

    return df

df = load_data()

# ─── REQUIRED COLUMNS CHECK ────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "AssetID", "Nom", "Type", "Site", "Criticité",
    "BaselineHealthScore", "MTTR_h", "MTBF_h",
    "Disponibilité_%", "Coût_MAD", "Statut",
    "ProchaineMaintenance"
]

missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
if missing_cols:
    st.error(f"❌ Colonnes manquantes: {missing_cols}")
    st.stop()

# ─── SIMPLE UI (clean + safe for deployment) ───────────────────────────────────
st.title("⚡ ReliabilityFlow × ONEE")
st.markdown("### 📊 Dashboard de Maintenance Prédictive")

# ─── KPI SECTION ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Équipements", len(df))

with c2:
    alerts = len(df[df["BaselineHealthScore"] < 45])
    st.metric("Alertes critiques", alerts)

with c3:
    st.metric("Sites", df["Site"].nunique())

with c4:
    st.metric("Santé moyenne", f"{df['BaselineHealthScore'].mean():.1f}/100")

st.divider()

# ─── TABLE ─────────────────────────────────────────────────────────────────────
st.subheader("📋 Parc Équipements")

display_cols = [
    "AssetID", "Nom", "Type", "Site",
    "BaselineHealthScore", "MTTR_h", "MTBF_h", "Disponibilité_%"
]

st.dataframe(df[display_cols], use_container_width=True)

# ─── CHARTS ────────────────────────────────────────────────────────────────────
st.subheader("📊 Analyse")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        df,
        x="BaselineHealthScore",
        nbins=20,
        title="Distribution des scores de santé"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.scatter(
        df,
        x="MTBF_h",
        y="Disponibilité_%",
        color="BaselineHealthScore",
        size="Coût_MAD",
        title="MTBF vs Disponibilité"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ─── ALERTS ────────────────────────────────────────────────────────────────────
st.subheader("🚨 Alertes IA")

df_alerts = df[df["BaselineHealthScore"] < 45]

if df_alerts.empty:
    st.success("✅ Aucun équipement critique")
else:
    for _, row in df_alerts.iterrows():
        st.warning(
            f"{row['AssetID']} | {row['Nom']} → Score: {row['BaselineHealthScore']}"
        )

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("ReliabilityFlow × ONEE | Souad Assad")
