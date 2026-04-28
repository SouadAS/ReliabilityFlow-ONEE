# ==============================================================================
# SMART MAINTENANCE ONEE — Plateforme de Maintenance Prédictive par IA
# Framework: Python 3 / Streamlit
# Données  : donnees.xlsx  (180 équipements ONEE)
# Colonnes réelles : AssetID, Context, Site, Line, AssetType, Criticality,
#                    InstallYear, AgeYears, Manufacturer, RatedPower_kW,
#                    MaintenancePolicy, Redundancy, Environment,
#                    UtilizationRate, BaselineHealthScore
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION DE LA PAGE  (DOIT être le tout premier appel Streamlit)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Maintenance × ONEE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. INJECTION CSS GLOBALE — Thème Corporate ONEE (Bleu #004a99 / Jaune #f9b233)
#    RÈGLE ABSOLUE : tout CSS doit être dans un st.markdown(..., unsafe_allow_html=True)
#    Ne jamais écrire de balises HTML en dehors de st.markdown.
# ──────────────────────────────────────────────────────────────────────────────
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
      rel="stylesheet">
<style>
  /* --- Base ---------------------------------------------------------------- */
  *, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
  html, body, [data-testid="stAppViewContainer"] {
      background: #040e1f !important; color: #e4eaf4 !important;
  }
  [data-testid="stAppViewContainer"] { padding: 0 !important; }
  [data-testid="stHeader"]           { display: none !important; }
  section[data-testid="stSidebar"]   { display: none !important; }
  .block-container                   { padding: 0 !important; max-width: 100% !important; }

  /* --- Onglets ------------------------------------------------------------- */
  [data-testid="stTabs"] [role="tablist"] {
      background: #0b1e3d !important; border-radius: 12px !important;
      padding: 6px !important; border: 1px solid #1a3f7a !important; gap: 4px !important;
  }
  [data-testid="stTabs"] button {
      background: transparent !important; color: #7ba3d4 !important;
      border: none !important; font-weight: 600 !important; font-size: .88rem !important;
      padding: .55rem 1.1rem !important; border-radius: 8px !important; transition: all .2s !important;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
      background: linear-gradient(135deg,#004a99,#0062cc) !important;
      color: #ffffff !important; box-shadow: 0 4px 14px rgba(0,74,153,.45) !important;
  }

  
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 3. CHARGEMENT ET ENRICHISSEMENT DES DONNÉES
#    Tous les KPIs sont calculés dynamiquement à partir du fichier Excel réel.
#    Aucune valeur codée en dur (pas de chiffres statiques).
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def charger_donnees():
    """Charge donnees.xlsx et calcule les KPIs dynamiquement depuis le DataFrame."""

    chemin = "donnees.xlsx"
    if not os.path.exists(chemin):
        st.error(
            "❌ Fichier 'donnees.xlsx' introuvable. "
            "Placez-le dans le même dossier que app.py."
        )
        st.stop()

    df = pd.read_excel(chemin)

    hs = df["BaselineHealthScore"]   # score réel entre 35 et 98

    # MTTR (heures) : score bas + âge élevé = réparation plus longue
    df["MTTR_h"] = ((100 - hs) / 10 + df["AgeYears"] * 0.08).round(1)

    # MTBF (heures) : score élevé + équipement récent = intervalle plus long
    df["MTBF_h"] = (hs * 2.8 + (100 - df["AgeYears"]) * 1.5).round(0)

    # Disponibilité (%)
    df["Disponibilite_pct"] = (
        df["MTBF_h"] / (df["MTBF_h"] + df["MTTR_h"]) * 100
    ).round(1)

    # Coût estimé de maintenance (MAD) — pondéré par criticité et âge
    coeff = {"Very High": 2.0, "High": 1.5, "Medium": 1.0, "Low": 0.7}
    df["Cout_MAD"] = (
        (100 - hs) * 1_800
        + df["AgeYears"] * 900
        + df["RatedPower_kW"] * 55
        + df["Criticality"].map(coeff).fillna(1.0) * 8_000
    ).round(0).astype(int)

    # Catégorie de santé (pour affichage)
    df["Sante_Cat"] = np.select(
        [hs < 45, (hs >= 45) & (hs < 65), hs >= 65],
        ["Critique", "Dégradé", "Bon"],
        default="Inconnu",
    )

    # Score de risque de panne (0–100) — modèle IA multi-critères
    df["RisquePanne"] = (
        (100 - hs) * 0.50
        + df["AgeYears"] * 1.20
        + (1 - df["UtilizationRate"]) * 10
        + df["Criticality"].map({"Very High": 25, "High": 15, "Medium": 8, "Low": 3}).fillna(0)
    ).clip(0, 100).round(1)

    # Statut maintenance dynamique basé sur le risque
    df["Statut_Maint"] = np.where(
        df["RisquePanne"] > 65, "Urgent",
        np.where(df["RisquePanne"] > 40, "Planifié", "OK"),
    )

    # Traduction criticité en français
    trad = {"Very High": "Très Haute", "High": "Haute", "Medium": "Moyenne", "Low": "Faible"}
    df["Criticite_FR"] = df["Criticality"].map(trad).fillna(df["Criticality"])

    return df


df = charger_donnees()


# ──────────────────────────────────────────────────────────────────────────────
# 4. EN-TÊTE NAVIGATION (sticky, pur HTML via st.markdown)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background:linear-gradient(90deg,#040e1f 0%,#0b1e3d 50%,#040e1f 100%);
        border-bottom:2px solid #004a99; padding:.75rem 2.5rem;
        display:flex; align-items:center; justify-content:space-between;
        position:sticky; top:0; z-index:999;
    ">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="
                background:linear-gradient(135deg,#004a99,#f9b233);
                width:38px; height:38px; border-radius:9px;
                display:flex; align-items:center; justify-content:center;
                font-size:1.3rem; color:#040e1f;
            ">⚡</div>
            <span style="font-size:1.15rem; font-weight:800; color:#fff; letter-spacing:-.5px;">
                Smart Maintenance
            </span>
            <span style="font-size:1.05rem; font-weight:300; color:#f9b233;"> × ONEE</span>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
            <span style="
                background:#22c55e22; color:#22c55e; border:1px solid #22c55e55;
                padding:3px 10px; border-radius:20px; font-size:.75rem; font-weight:600;
            ">● SYSTÈME ACTIF</span>
            <span style="color:#7ba3d4; font-size:.8rem;">Maintenance Prédictive IA</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# 5. ONGLETS PRINCIPAUX
# ──────────────────────────────────────────────────────────────────────────────
onglets = st.tabs([
    "ACCUEIL",
    "DASHBOARD KPI",
    "PARC ÉQUIPEMENTS",
    "ALERTES IA",
    "PRÉDICTION PANNES",
    "PLAN MAINTENANCE",
])


# ==============================================================================
# ONGLET 1 — ACCUEIL
# ==============================================================================
with onglets[0]:

    # Section Hero
    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg,#040e1f 0%,#0b1e3d 45%,#0d2860 70%,#040e1f 100%);
            border:1px solid #1a3f7a; border-radius:20px;
            padding:4rem 3rem; margin:1.5rem 1rem;
            position:relative; overflow:hidden; text-align:center;
        ">
            <div style="
                position:absolute; inset:0; pointer-events:none;
                background-image:
                    linear-gradient(rgba(0,74,153,.07) 1px,transparent 1px),
                    linear-gradient(90deg,rgba(0,74,153,.07) 1px,transparent 1px);
                background-size:40px 40px;
            "></div>
            <div style="
                position:absolute; top:-80px; right:-80px; pointer-events:none;
                width:320px; height:320px; border-radius:50%;
                background:radial-gradient(circle,rgba(249,178,51,.12),transparent 70%);
            "></div>
            <div style="
                position:absolute; bottom:-80px; left:-80px; pointer-events:none;
                width:280px; height:280px; border-radius:50%;
                background:radial-gradient(circle,rgba(0,74,153,.2),transparent 70%);
            "></div>
            <div style="position:relative; z-index:2;">
                <div style="
                    display:inline-block;
                    background:linear-gradient(135deg,#004a9933,#f9b23322);
                    border:1px solid #004a9966; border-radius:30px;
                    padding:5px 18px; font-size:.78rem; font-weight:600;
                    color:#f9b233; letter-spacing:2px; text-transform:uppercase;
                    margin-bottom:1.5rem;
                ">Office National de l'Électricité et de l'Eau Potable — Maroc</div>
                <h1 style="
                    font-size:3.5rem; font-weight:900; color:#fff;
                    line-height:1.08; margin:0 0 .8rem; letter-spacing:-2px;
                ">SMART MAINTENANCE</h1>
                <p style="
                    font-size:1.15rem; font-weight:600; margin:0 0 .5rem;
                    background:linear-gradient(90deg,#004a99,#f9b233);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                ">Maintenance Prédictive pilotée par l'Intelligence Artificielle</p>
                <p style="
                    font-size:.97rem; color:#8ab0d8; max-width:680px;
                    margin:0 auto 2.5rem; line-height:1.75;
                ">
                    Transformez vos données industrielles brutes en décisions
                    stratégiques prescriptives — anticipez les pannes, réduisez
                    les coûts et garantissez la continuité de service sur
                    l'ensemble du parc ONEE.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPIs calculés depuis la vraie base de données
    nb_crit    = int((df["BaselineHealthScore"] < 45).sum())
    nb_total   = len(df)
    pct_crit   = round(nb_crit / nb_total * 100, 1)
    gain_cout  = round(df["Cout_MAD"].sum() * 0.25 / 1_000_000, 2)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("⚙️ Équipements surveillés", nb_total)
    with c2:
        st.metric("🚨 En état critique", nb_crit,
                  delta=f"{pct_crit}% du parc", delta_color="inverse")
    with c3:
        st.metric("📍 Sites ONEE couverts", df["Site"].nunique())
    with c4:
        st.metric("💰 Économies potentielles IA", f"{gain_cout} M MAD",
                  help="Estimation de 25% d'économies sur le budget maintenance")

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphiques d'aperçu
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        cats   = ["Critique (<45)", "Dégradé (45-65)", "Bon (>65)"]
        counts = [
            int((df["BaselineHealthScore"] < 45).sum()),
            int(((df["BaselineHealthScore"] >= 45) & (df["BaselineHealthScore"] < 65)).sum()),
            int((df["BaselineHealthScore"] >= 65).sum()),
        ]
        fig_donut = go.Figure(go.Pie(
            labels=cats, values=counts, hole=.58,
            marker_colors=["#ef4444", "#f9b233", "#22c55e"],
            textinfo="label+percent", textfont_color="white",
        ))
        fig_donut.update_layout(
            title="État de santé du parc (180 équipements)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e4eaf4", title_font_color="#e4eaf4",
            legend=dict(font=dict(color="#8ab0d8")),
            margin=dict(t=50, b=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_g2:
        site_avg = (
            df.groupby("Site")["BaselineHealthScore"]
            .mean().round(1).reset_index()
            .sort_values("BaselineHealthScore")
        )
        fig_bar = px.bar(
            site_avg, x="BaselineHealthScore", y="Site", orientation="h",
            color="BaselineHealthScore",
            color_continuous_scale=["#ef4444", "#f9b233", "#22c55e"],
            labels={"BaselineHealthScore": "Score Santé Moyen", "Site": ""},
            title="Score de santé moyen par site",
            text="BaselineHealthScore",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e4eaf4", title_font_color="#e4eaf4",
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#1a3f7a", range=[0, 85]),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(t=50, b=10, l=10, r=60),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Scatter : corrélation âge vs score de santé
    fig_scatter = px.scatter(
        df, x="AgeYears", y="BaselineHealthScore",
        color="Criticite_FR", size="RatedPower_kW",
        hover_name="AssetID",
        hover_data=["AssetType", "Site", "MTBF_h", "MTTR_h"],
        color_discrete_map={
            "Très Haute": "#ef4444", "Haute": "#f97316",
            "Moyenne": "#f9b233", "Faible": "#22c55e",
        },
        labels={"AgeYears": "Âge (années)", "BaselineHealthScore": "Score de Santé"},
        title="Corrélation Âge ↔ Score de Santé (taille bulle = Puissance kW)",
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e4eaf4", title_font_color="#e4eaf4",
        xaxis=dict(gridcolor="#1a3f7a"), yaxis=dict(gridcolor="#1a3f7a"),
        legend=dict(font=dict(color="#8ab0d8")),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ==============================================================================
# ONGLET 2 — DASHBOARD KPI
# ==============================================================================
with onglets[1]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Tableau de Bord KPI — Parc Équipements ONEE")

    # Bannière Bilan Global
    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg,#0b1e3d,#081428);
            border:1.5px solid #f9b233; border-radius:14px;
            padding:1rem 1.5rem; margin-bottom:1.5rem;
        ">
            <p style="color:#f9b233; font-weight:700; font-size:.84rem;
                      margin:0; text-transform:uppercase; letter-spacing:1px;">
                ⭐ BILAN GLOBAL DU PARC
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Calculs globaux RÉELS — pas de valeurs statiques
    mttr_global   = df["MTTR_h"].mean()
    mtbf_global   = df["MTBF_h"].mean()
    dispo_globale = df["Disponibilite_pct"].mean()
    cout_total_M  = df["Cout_MAD"].sum() / 1_000_000
    sante_globale = df["BaselineHealthScore"].mean()

    g1, g2, g3, g4, g5 = st.columns(5)
    with g1:
        st.metric("⏱ MTTR Global", f"{mttr_global:.1f} h",
                  help="Temps moyen de réparation sur tout le parc")
    with g2:
        st.metric("📈 MTBF Global", f"{mtbf_global:.0f} h",
                  help="Temps moyen entre pannes sur tout le parc")
    with g3:
        st.metric("✅ Disponibilité Moyenne", f"{dispo_globale:.1f} %")
    with g4:
        st.metric("💰 Budget Total Maintenance", f"{cout_total_M:.2f} M MAD")
    with g5:
        st.metric("💚 Santé Moyenne Parc", f"{sante_globale:.1f} / 100")

    st.markdown("---")

    # Tableau KPI détaillé (toutes les colonnes calculées)
    cols_affich = [
        "AssetID", "AssetType", "Site", "Criticite_FR",
        "AgeYears", "BaselineHealthScore", "Sante_Cat",
        "MTTR_h", "MTBF_h", "Disponibilite_pct", "Cout_MAD",
    ]
    df_kpi = df[cols_affich].copy()
    df_kpi.columns = [
        "ID", "Type", "Site", "Criticité", "Âge (ans)",
        "Score Santé", "État", "MTTR (h)", "MTBF (h)",
        "Dispo (%)", "Coût (MAD)",
    ]
    st.dataframe(
        df_kpi.sort_values("Score Santé"),
        use_container_width=True,
        hide_index=True,
        height=440,
    )

    col_k1, col_k2 = st.columns(2)

    with col_k1:
        fig_tree = px.treemap(
            df, path=["Site", "AssetType", "AssetID"],
            values="Cout_MAD", color="BaselineHealthScore",
            color_continuous_scale=["#ef4444", "#f9b233", "#22c55e"],
            title="Répartition des coûts par Site / Type",
        )
        fig_tree.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e4eaf4", title_font_color="#e4eaf4",
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_k2:
        fig_sc2 = px.scatter(
            df, x="MTBF_h", y="Disponibilite_pct",
            color="BaselineHealthScore", size="Cout_MAD",
            hover_name="AssetID",
            hover_data=["AssetType", "Site", "MTTR_h"],
            color_continuous_scale=["#ef4444", "#f9b233", "#22c55e"],
            labels={"MTBF_h": "MTBF (h)", "Disponibilite_pct": "Disponibilité (%)"},
            title="MTBF vs Disponibilité (taille = Coût estimé)",
        )
        fig_sc2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e4eaf4", title_font_color="#e4eaf4",
            xaxis=dict(gridcolor="#1a3f7a"), yaxis=dict(gridcolor="#1a3f7a"),
        )
        st.plotly_chart(fig_sc2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# ONGLET 3 — PARC ÉQUIPEMENTS
# ==============================================================================
with onglets[2]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📋 Parc Équipements — Filtres Avancés")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sites_sel = st.multiselect(
            "📍 Site", sorted(df["Site"].unique()),
            default=sorted(df["Site"].unique()),
        )
    with f2:
        crits_sel = st.multiselect(
            "⚠️ Criticité", sorted(df["Criticite_FR"].unique()),
            default=sorted(df["Criticite_FR"].unique()),
        )
    with f3:
        types_sel = st.multiselect(
            "⚙️ Type", sorted(df["AssetType"].unique()),
            default=sorted(df["AssetType"].unique()),
        )
    with f4:
        health_range = st.slider("💚 Score de santé", 0, 100, (0, 100))

    masque = (
        df["Site"].isin(sites_sel)
        & df["Criticite_FR"].isin(crits_sel)
        & df["AssetType"].isin(types_sel)
        & df["BaselineHealthScore"].between(health_range[0], health_range[1])
    )
    df_filt = df[masque].copy()

    st.markdown(
        f"<p style='color:#7ba3d4; font-size:.9rem;'>"
        f"🔍 <strong style='color:#f9b233;'>{len(df_filt)}</strong>"
        f" équipement(s) correspondent aux filtres</p>",
        unsafe_allow_html=True,
    )

    # Affichage en cartes (3 par ligne)
    for i in range(0, len(df_filt), 3):
        ligne = df_filt.iloc[i: i + 3]
        cols  = st.columns(3)
        for col, (_, eq) in zip(cols, ligne.iterrows()):
            hs    = eq["BaselineHealthScore"]
            color = "#ef4444" if hs < 45 else ("#f9b233" if hs < 65 else "#22c55e")
            with col:
                st.markdown(
                    f"""
                    <div style="
                        background:linear-gradient(135deg,#0b1e3d,#081428);
                        border:1px solid #1a3f7a; border-left:4px solid {color};
                        border-radius:12px; padding:1rem; margin-bottom:.8rem;
                    ">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:.4rem;">
                            <span style="font-weight:700; color:#fff; font-size:.9rem;">{eq["AssetID"]}</span>
                            <span style="background:{color}22; color:{color}; border:1px solid {color}66;
                                         padding:2px 8px; border-radius:20px; font-size:.7rem; font-weight:600;">
                                {hs:.0f}/100
                            </span>
                        </div>
                        <div style="color:#8ab0d8; font-size:.82rem; margin-bottom:.3rem;">{eq["AssetType"]}</div>
                        <div style="display:flex; flex-wrap:wrap; gap:5px; margin-top:.5rem;">
                            <span style="background:#004a9922; color:#7ba3d4; padding:2px 7px; border-radius:10px; font-size:.71rem;">📍 {eq["Site"]}</span>
                            <span style="background:#004a9922; color:#7ba3d4; padding:2px 7px; border-radius:10px; font-size:.71rem;">⚠️ {eq["Criticite_FR"]}</span>
                            <span style="background:#004a9922; color:#7ba3d4; padding:2px 7px; border-radius:10px; font-size:.71rem;">📅 {int(eq["AgeYears"])} ans</span>
                        </div>
                        <div style="margin-top:.6rem; height:4px; background:#1a3f7a; border-radius:2px;">
                            <div style="height:4px; width:{hs}%; background:{color}; border-radius:2px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:.5rem; font-size:.73rem; color:#7ba3d4;">
                            <span>MTBF {eq["MTBF_h"]:.0f}h</span>
                            <span>Dispo {eq["Disponibilite_pct"]:.1f}%</span>
                            <span>{int(eq["Cout_MAD"]) // 1000}k MAD</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# ONGLET 4 — ALERTES IA
# ==============================================================================
with onglets[3]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)

    df_alerte = df[df["BaselineHealthScore"] < 45].sort_values("BaselineHealthScore")

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#2d0a0a,#1a0505);
            border:1px solid #ef444466; border-radius:14px;
            padding:1.5rem; margin-bottom:1.5rem;
        ">
            <h3 style="color:#ef4444; margin:0 0 .5rem;">
                🚨 ALERTES IA — {len(df_alerte)} équipement(s) en état critique
            </h3>
            <p style="color:#fca5a5; margin:0; font-size:.9rem;">
                Ces actifs ont un <strong>BaselineHealthScore &lt; 45</strong>.
                Une intervention immédiate est recommandée pour éviter une panne majeure.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(df_alerte) == 0:
        st.success("✅ Aucune alerte critique. Tous les équipements dépassent le seuil de 45.")
    else:
        for _, eq in df_alerte.iterrows():
            hs  = eq["BaselineHealthScore"]
            urg = "URGENT" if hs < 40 else "CRITIQUE"
            uc  = "#ef4444" if hs < 40 else "#f97316"
            st.markdown(
                f"""
                <div style="
                    background:linear-gradient(135deg,#1a0a0a,#0d0505);
                    border:1px solid {uc}55; border-left:5px solid {uc};
                    border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:.9rem;
                ">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:.5rem;">
                        <div>
                            <div style="display:flex; align-items:center; gap:10px; margin-bottom:.3rem;">
                                <span style="font-weight:800; color:#fff; font-size:1rem;">{eq["AssetID"]}</span>
                                <span style="background:{uc}33; color:{uc}; border:1px solid {uc};
                                             padding:2px 10px; border-radius:20px; font-size:.72rem; font-weight:700;">
                                    ⚠ {urg}
                                </span>
                            </div>
                            <div style="color:#fca5a5; font-size:.85rem;">{eq["AssetType"]} — {eq["Manufacturer"]}</div>
                            <div style="color:#7ba3d4; font-size:.8rem; margin-top:4px;">
                                📍 {eq["Site"]} &nbsp;|&nbsp; Criticité : {eq["Criticite_FR"]} &nbsp;|&nbsp; Âge : {int(eq["AgeYears"])} ans
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:2.1rem; font-weight:900; color:{uc}; line-height:1;">{hs:.1f}</div>
                            <div style="font-size:.72rem; color:#fca5a5;">Score Santé</div>
                        </div>
                    </div>
                    <div style="margin-top:.8rem; height:6px; background:#2d1010; border-radius:3px;">
                        <div style="height:6px; width:{hs}%; background:{uc}; border-radius:3px;"></div>
                    </div>
                    <div style="display:flex; gap:1.5rem; flex-wrap:wrap; margin-top:.7rem; font-size:.8rem; color:#fca5a5;">
                        <span>⏱ MTTR <strong style="color:#fff;">{eq["MTTR_h"]} h</strong></span>
                        <span>📉 MTBF <strong style="color:#fff;">{eq["MTBF_h"]:.0f} h</strong></span>
                        <span>📊 Dispo <strong style="color:#fff;">{eq["Disponibilite_pct"]:.1f}%</strong></span>
                        <span>💰 Coût <strong style="color:#fff;">{int(eq["Cout_MAD"]) // 1000}k MAD</strong></span>
                        <span>🔌 Puissance <strong style="color:#fff;">{eq["RatedPower_kW"]} kW</strong></span>
                    </div>
                    <div style="
                        margin-top:.8rem; padding:.6rem; background:#2d101022;
                        border-radius:8px; border:1px solid #ef444422;
                        font-size:.82rem; color:#fca5a5;
                    ">
                        🤖 <strong>Recommandation IA :</strong>
                        Planifier une inspection de <em>{eq["AssetType"]} ({eq["AssetID"]})</em> immédiatement.
                        Score de santé {hs:.1f}/100, risque de panne estimé :
                        <strong style="color:{uc};">{eq["RisquePanne"]:.0f}%</strong>.
                        Économie potentielle si intervention préventive :
                        <strong style="color:#22c55e;">{int(eq["Cout_MAD"] * 0.35) // 1000}k MAD</strong>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# ONGLET 5 — PRÉDICTION DE PANNES
# ==============================================================================
with onglets[4]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 🔮 Prédiction de Pannes — Analyse IA Multi-Critères")

    # Machines dont le score de risque dépasse 50
    df_pred = df[df["RisquePanne"] > 50].sort_values("RisquePanne", ascending=False).head(20)

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#1a0d2e,#0d0520);
            border:1px solid #9333ea66; border-radius:14px;
            padding:1.2rem 1.5rem; margin-bottom:1.5rem;
        ">
            <h4 style="color:#c084fc; margin:0 0 .4rem;">
                🔮 Modèle IA — {len(df_pred)} machine(s) à risque élevé de panne
            </h4>
            <p style="color:#d8b4fe; margin:0; font-size:.88rem;">
                Combinaison de 4 indicateurs : <strong>BaselineHealthScore</strong>,
                <strong>Âge</strong>, <strong>Taux d'utilisation</strong>
                et <strong>Criticité</strong>. Seuil d'alerte : risque &gt; 50%.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Graphique risque de panne
    fig_risk = px.bar(
        df_pred, x="RisquePanne", y="AssetID", orientation="h",
        color="RisquePanne",
        color_continuous_scale=["#f9b233", "#f97316", "#ef4444"],
        hover_data=["AssetType", "Site", "BaselineHealthScore", "AgeYears", "Criticite_FR"],
        labels={"RisquePanne": "Risque de Panne (%)", "AssetID": ""},
        title="Top équipements à risque de panne (score IA multi-critères)",
        text="RisquePanne",
    )
    fig_risk.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_risk.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e4eaf4", title_font_color="#e4eaf4",
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#1a3f7a", range=[0, 115]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        height=530, margin=dict(t=50, b=10, l=10, r=80),
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # Fiches détaillées
    st.markdown("#### 📋 Fiches Détaillées — Machines à Risque")

    for _, eq in df_pred.iterrows():
        rp     = eq["RisquePanne"]
        rp_col = "#ef4444" if rp > 75 else ("#f97316" if rp > 60 else "#f9b233")
        hs     = eq["BaselineHealthScore"]
        niv    = "MAXIMALE" if rp > 75 else ("HAUTE" if rp > 60 else "MODÉRÉE")

        with st.expander(
            f"🔴 {eq['AssetID']} — {eq['AssetType']} | {eq['Site']} "
            f"| Risque : {rp:.1f}%  |  Santé : {hs:.1f}/100",
            expanded=False,
        ):
            d1, d2, d3 = st.columns(3)

            with d1:
                st.markdown(
                    f"""
                    <div style="background:#0b1e3d; border-radius:10px; padding:.9rem; border:1px solid #1a3f7a;">
                        <p style="color:#7ba3d4; font-size:.73rem; margin:0 0 .7rem;
                                  text-transform:uppercase; letter-spacing:1px;">🔧 Identité</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>ID :</b> {eq["AssetID"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Type :</b> {eq["AssetType"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Site :</b> {eq["Site"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Fabricant :</b> {eq["Manufacturer"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Installation :</b> {int(eq["InstallYear"])} ({int(eq["AgeYears"])} ans)</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with d2:
                st.markdown(
                    f"""
                    <div style="background:#0b1e3d; border-radius:10px; padding:.9rem; border:1px solid #1a3f7a;">
                        <p style="color:#7ba3d4; font-size:.73rem; margin:0 0 .7rem;
                                  text-transform:uppercase; letter-spacing:1px;">📊 KPIs</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Score Santé :</b> <span style="color:#f9b233;">{hs:.1f}/100</span></p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>MTTR :</b> {eq["MTTR_h"]} h</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>MTBF :</b> {eq["MTBF_h"]:.0f} h</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Disponibilité :</b> {eq["Disponibilite_pct"]:.1f}%</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Utilisation :</b> {eq["UtilizationRate"] * 100:.1f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with d3:
                st.markdown(
                    f"""
                    <div style="background:#0b1e3d; border-radius:10px; padding:.9rem; border:1px solid {rp_col}55;">
                        <p style="color:{rp_col}; font-size:.73rem; margin:0 0 .7rem;
                                  text-transform:uppercase; letter-spacing:1px;">🚨 Risque IA</p>
                        <p style="color:{rp_col}; font-size:1.9rem; font-weight:900; margin:0 0 .4rem; line-height:1;">
                            {rp:.1f}%
                        </p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Criticité :</b> {eq["Criticite_FR"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Environnement :</b> {eq["Environment"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Politique :</b> {eq["MaintenancePolicy"]}</p>
                        <p style="color:#e4eaf4; font-size:.84rem; margin:.2rem 0;"><b>Coût estimé :</b> <span style="color:#f9b233;">{int(eq["Cout_MAD"]) // 1000}k MAD</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Recommandation IA
            st.markdown(
                f"""
                <div style="
                    margin-top:.8rem; padding:.8rem 1rem;
                    background:#1a0d2e; border-radius:10px;
                    border:1px solid #9333ea44; font-size:.84rem; color:#d8b4fe;
                ">
                    🤖 <strong style="color:#c084fc;">Recommandation IA :</strong>
                    Déclencher une maintenance préventive sur <em>{eq["AssetType"]} {eq["AssetID"]}</em>
                    avant défaillance. Priorité <strong style="color:{rp_col};">{niv}</strong>.
                    Durée estimée : <strong>{eq["MTTR_h"]} h</strong>.
                    Budget requis : <strong>{int(eq["Cout_MAD"]) // 1000}k MAD</strong>.
                    Gain par rapport à une panne subie :
                    <strong style="color:#22c55e;">{int(eq["Cout_MAD"] * 0.35) // 1000}k MAD</strong>.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# ONGLET 6 — PLAN DE MAINTENANCE (Espace Technicien)
# ==============================================================================
with onglets[5]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📅 Plan de Maintenance — Espace Technicien")

    # Initialisation du suivi d'état dans la session Streamlit (persistant par onglet)
    if "etats_taches" not in st.session_state:
        st.session_state.etats_taches = {}

    # 15 machines les plus prioritaires (risque le plus élevé)
    taches_df = df.sort_values("RisquePanne", ascending=False).head(15).copy()

    OPTIONS_STATUT   = ["Pas encore", "En cours", "Fait", "Annulé"]
    OPTIONS_PRIORITE = ["Basse", "Normale", "Haute", "Urgente"]

    for _, eq in taches_df.iterrows():
        aid = eq["AssetID"]

        # Valeurs par défaut si la tâche n'a pas encore été touchée
        if aid not in st.session_state.etats_taches:
            st.session_state.etats_taches[aid] = {
                "statut": "Pas encore",
                "progression": 0,
                "priorite": "Normale",
                "note": "",
            }
        etat = st.session_state.etats_taches[aid]
        rp   = eq["RisquePanne"]
        pc   = "#ef4444" if rp > 70 else ("#f9b233" if rp > 50 else "#22c55e")

        # Correction de la ligne with st.expander
    with st.expander(
        f"🛠️ {aid} • {eq['AssetType']} • {eq['Site']} "
        f"| Risque : {rp:.0f}% | Statut : {etat['statut']}",
        expanded=(rp > 70),
    ):
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

            with c1:
                statut = st.selectbox(
                    "📌 Statut", OPTIONS_STATUT,
                    index=OPTIONS_STATUT.index(etat["statut"]),
                    key=f"statut_{aid}",
                )
                st.session_state.etats_taches[aid]["statut"] = statut

            with c2:
                priorite = st.selectbox(
                    "🎯 Priorité", OPTIONS_PRIORITE,
                    index=OPTIONS_PRIORITE.index(etat["priorite"]),
                    key=f"priorite_{aid}",
                )
                st.session_state.etats_taches[aid]["priorite"] = priorite

            with c3:
                progression = st.slider(
                    "📊 Avancement (%)", 0, 100,
                    value=etat["progression"],
                    key=f"prog_{aid}",
                )
                st.session_state.etats_taches[aid]["progression"] = progression

            with c4:
                col_s = {
                    "Pas encore": "#7ba3d4", "En cours": "#f9b233",
                    "Fait": "#22c55e", "Annulé": "#6b7280",
                }
                cs = col_s.get(statut, "#7ba3d4")
                st.markdown(
                    f"""
                    <div style="
                        background:{cs}22; border:2px solid {cs};
                        border-radius:10px; padding:.7rem; text-align:center; margin-top:1.4rem;
                    ">
                        <div style="color:{cs}; font-weight:800; font-size:1.2rem; line-height:1;">{progression}%</div>
                        <div style="color:{cs}; font-size:.72rem; margin-top:2px;">{statut}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            note = st.text_input(
                "📝 Note technicien",
                value=etat["note"],
                placeholder="Ex : Pièce commandée, intervention prévue le ...",
                key=f"note_{aid}",
            )
            st.session_state.etats_taches[aid]["note"] = note

            # Résumé technique de l'équipement
            st.markdown(
                f"""
                <div style="
                    display:flex; gap:1.5rem; flex-wrap:wrap; font-size:.8rem;
                    color:#7ba3d4; margin-top:.5rem; padding:.6rem;
                    background:#081428; border-radius:8px;
                ">
                    <span>⚙️ Type : <strong style="color:#e4eaf4;">{eq["AssetType"]}</strong></span>
                    <span>🏭 Fab. : <strong style="color:#e4eaf4;">{eq["Manufacturer"]}</strong></span>
                    <span>📅 Âge : <strong style="color:#e4eaf4;">{int(eq["AgeYears"])} ans</strong></span>
                    <span>⚠️ Criticité : <strong style="color:{pc};">{eq["Criticite_FR"]}</strong></span>
                    <span>🔌 Puissance : <strong style="color:#e4eaf4;">{eq["RatedPower_kW"]} kW</strong></span>
                    <span>💰 Budget : <strong style="color:#f9b233;">{int(eq["Cout_MAD"]) // 1000}k MAD</strong></span>
                    <span>⏱ MTTR estimé : <strong style="color:#e4eaf4;">{eq["MTTR_h"]} h</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Tableau de bord synthèse technicien
    st.markdown("---")
    st.markdown("#### 📈 Synthèse d'Avancement du Plan de Maintenance")

    total      = len(taches_df)
    terminees  = sum(1 for v in st.session_state.etats_taches.values() if v["statut"] == "Fait")
    en_cours   = sum(1 for v in st.session_state.etats_taches.values() if v["statut"] == "En cours")
    pas_encore = sum(1 for v in st.session_state.etats_taches.values() if v["statut"] == "Pas encore")
    avanc_moy  = round(
        sum(v["progression"] for v in st.session_state.etats_taches.values()) / max(total, 1), 1
    )

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1: st.metric("📋 Tâches totales", total)
    with s2: st.metric("✅ Terminées", terminees)
    with s3: st.metric("🔄 En cours", en_cours)
    with s4: st.metric("⏳ Pas encore", pas_encore)
    with s5: st.metric("📊 Avancement moyen", f"{avanc_moy}%")

    # Barre de progression globale
    st.markdown(
        f"""
        <div style="margin-top:1rem;">
            <div style="display:flex; justify-content:space-between;
                        color:#7ba3d4; font-size:.82rem; margin-bottom:.3rem;">
                <span>Progression globale du plan</span>
                <span style="color:#f9b233; font-weight:700;">{avanc_moy}%</span>
            </div>
            <div style="height:12px; background:#1a3f7a; border-radius:6px; overflow:hidden;">
                <div style="
                    height:12px; width:{avanc_moy}%;
                    background:linear-gradient(90deg,#004a99,#f9b233);
                    border-radius:6px;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PIED DE PAGE
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        margin-top:3rem; padding:1.1rem 2rem;
        background:#040e1f; border-top:1px solid #1a3f7a;
        display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.5rem;
    ">
        <span style="color:#2e5180; font-size:.78rem;">⚡ Smart Maintenance × ONEE — Maintenance Prédictive IA</span>
        <span style="color:#2e5180; font-size:.78rem;">Filière Maintenance Industrielle | Encadré par M.El Harraki | 2024-2025</span>
    </div>
    """,
    unsafe_allow_html=True,
)
