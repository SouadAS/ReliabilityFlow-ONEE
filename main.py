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
    # Try local file first; fallback to GitHub if needed
    local_path = "donnees.xlsx"
    github_url = "https://raw.githubusercontent.com/your-username/your-repo/main/donnees.xlsx"
    if os.path.exists(local_path):
        df = pd.read_excel(local_path)
    else:
        try:
            df = pd.read_excel(github_url)
        except Exception:
            st.error("❌ Impossible de charger `donnees.xlsx`. Vérifiez le fichier local ou l'URL GitHub.")
            st.stop()
    return df

df = load_data()

# ─── HELPER: KPI COMPUTATIONS ──────────────────────────────────────────────────
def get_kpi_color(val, thresholds=(45, 70), reverse=False):
    low, high = thresholds
    if reverse:
        return "#ef4444" if val < low else ("#f0c040" if val < high else "#22c55e")
    return "#22c55e" if val > high else ("#f0c040" if val > low else "#ef4444")

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
        <!-- Decorative grid -->
        <div style="
            position: absolute; inset: 0;
            background-image: linear-gradient(rgba(30,107,184,0.08) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(30,107,184,0.08) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
        "></div>
        <!-- Glow orb -->
        <div style="
            position:absolute; top:-60px; right:-60px;
            width:300px; height:300px; border-radius:50%;
            background: radial-gradient(circle, rgba(240,192,64,0.12), transparent 70%);
            pointer-events:none;
        "></div>
        <div style="
            position:absolute; bottom:-60px; left:-60px;
            width:250px; height:250px; border-radius:50%;
            background: radial-gradient(circle, rgba(30,107,184,0.18), transparent 70%);
            pointer-events:none;
        "></div>

        <div style="position:relative; z-index:2;">
            <div style="
                display:inline-block;
                background: linear-gradient(135deg, #1e6bb844, #f0c04022);
                border: 1px solid #1e6bb866;
                border-radius: 30px;
                padding: 6px 20px;
                font-size: 0.8rem;
                font-weight: 600;
                color: #f0c040;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: 1.5rem;
            ">Office National de l'Électricité et de l'Eau Potable</div>

            <h1 style="
                font-size: 3.5rem;
                font-weight: 900;
                color: #ffffff;
                line-height: 1.1;
                margin: 0 0 1rem 0;
                letter-spacing: -2px;
            ">
                Maintenance Prédictive<br>
                <span style="
                    background: linear-gradient(90deg, #1e6bb8, #f0c040);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">Pilotée par l'Intelligence Artificielle</span>
            </h1>

            <p style="
                font-size: 1.15rem;
                color: #a0b8d8;
                max-width: 700px;
                margin: 0 auto 2.5rem;
                line-height: 1.7;
                font-weight: 400;
            ">
                ReliabilityFlow transforme vos données industrielles brutes en
                <strong style="color:#f0c040;">décisions stratégiques prescriptives</strong> —
                anticipez les pannes, optimisez vos ressources et garantissez la continuité
                de service sur l'ensemble du parc ONEE.
            </p>

            <!-- 3 key metrics -->
            <div style="display:flex; gap:1.5rem; justify-content:center; flex-wrap:wrap; margin-top:2rem;">
                <div style="
                    background: linear-gradient(135deg, #0d1f3c, #0a1628);
                    border: 1px solid #1e6bb8;
                    border-radius: 14px; padding: 1.5rem 2rem;
                    min-width: 160px;
                ">
                    <div style="font-size:2.2rem; font-weight:900; color:#f0c040;">-25%</div>
                    <div style="font-size:0.85rem; color:#7fa8d4; margin-top:4px;">Réduction des coûts<br>de maintenance</div>
                </div>
                <div style="
                    background: linear-gradient(135deg, #0d1f3c, #0a1628);
                    border: 1px solid #1e6bb8;
                    border-radius: 14px; padding: 1.5rem 2rem;
                    min-width: 160px;
                ">
                    <div style="font-size:2.2rem; font-weight:900; color:#22c55e;">+40%</div>
                    <div style="font-size:0.85rem; color:#7fa8d4; margin-top:4px;">Amélioration<br>de la disponibilité</div>
                </div>
                <div style="
                    background: linear-gradient(135deg, #0d1f3c, #0a1628);
                    border: 1px solid #1e6bb8;
                    border-radius: 14px; padding: 1.5rem 2rem;
                    min-width: 160px;
                ">
                    <div style="font-size:2.2rem; font-weight:900; color:#1e6bb8;">24/7</div>
                    <div style="font-size:0.85rem; color:#7fa8d4; margin-top:4px;">Surveillance<br>en temps réel</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats from real data
    st.markdown("<div style='margin:0 1rem;'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("⚙️ Équipements surveillés", len(df))
    with c2:
        alerts = len(df[df["BaselineHealthScore"] < 45])
        st.metric("🚨 Alertes critiques IA", alerts)
    with c3:
        st.metric("📍 Sites couverts", df["Site"].nunique())
    with c4:
        avg_health = round(df["BaselineHealthScore"].mean(), 1)
        st.metric("💚 Santé moyenne du parc", f"{avg_health}/100")
    st.markdown("</div>", unsafe_allow_html=True)

    # Health donut chart
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        health_bins = ["Critique (<45)", "Dégradé (45-70)", "Bon (>70)"]
        counts = [
            len(df[df["BaselineHealthScore"] < 45]),
            len(df[(df["BaselineHealthScore"] >= 45) & (df["BaselineHealthScore"] < 70)]),
            len(df[df["BaselineHealthScore"] >= 70]),
        ]
        fig_donut = go.Figure(go.Pie(
            labels=health_bins, values=counts,
            hole=0.6,
            marker_colors=["#ef4444", "#f0c040", "#22c55e"],
            textinfo="label+percent",
            textfont_color="white",
        ))
        fig_donut.update_layout(
            title="État de santé du parc",
            title_font_color="#e8edf5",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5",
            legend=dict(font=dict(color="#a0b8d8")),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        fig_bar = px.bar(
            df.groupby("Site")["BaselineHealthScore"].mean().reset_index().sort_values("BaselineHealthScore"),
            x="BaselineHealthScore", y="Site", orientation="h",
            color="BaselineHealthScore",
            color_continuous_scale=["#ef4444", "#f0c040", "#22c55e"],
            labels={"BaselineHealthScore": "Score Santé Moyen", "Site": ""},
            title="Score de santé moyen par site",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5",
            title_font_color="#e8edf5",
            coloraxis_showscale=False,
            margin=dict(t=50, b=20, l=10, r=10),
            xaxis=dict(gridcolor="#1a3a6b"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD KPI
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Tableau de Bord KPI — Parc Équipements ONEE")

    # Global bilan cards at top
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0d1f3c, #0a1628);
        border: 1px solid #f0c040;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <p style='color:#f0c040; font-weight:700; font-size:0.85rem; margin:0 0 0.8rem; text-transform:uppercase; letter-spacing:1px;'>
            ⭐ BILAN GLOBAL DU PARC
        </p>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3, g4, g5 = st.columns(5)
    with g1:
        st.metric("MTTR Global (h)", f"{df['MTTR_h'].mean():.1f} h", help="Mean Time To Repair moyen")
    with g2:
        st.metric("MTBF Global (h)", f"{df['MTBF_h'].mean():.0f} h", help="Mean Time Between Failures moyen")
    with g3:
        st.metric("Disponibilité Totale", f"{df['Disponibilité_%'].mean():.1f} %")
    with g4:
        st.metric("Budget Total (MAD)", f"{df['Coût_MAD'].sum()/1e6:.2f} M")
    with g5:
        st.metric("Score Santé Global", f"{df['BaselineHealthScore'].mean():.0f}/100")

    st.markdown("---")

    # KPI Table
    display_cols = ["AssetID", "Nom", "Type", "Site", "Criticité", "BaselineHealthScore",
                    "MTTR_h", "MTBF_h", "Disponibilité_%", "Coût_MAD", "Statut"]
    df_display = df[display_cols].copy()
    df_display.columns = ["ID", "Nom", "Type", "Site", "Criticité", "Santé",
                          "MTTR (h)", "MTBF (h)", "Dispo (%)", "Coût (MAD)", "Statut"]

    st.dataframe(
        df_display.sort_values("Santé"),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        fig_scatter = px.scatter(
            df, x="MTBF_h", y="Disponibilité_%",
            color="BaselineHealthScore",
            size="Coût_MAD",
            hover_name="AssetID",
            hover_data=["Type", "Site", "Criticité"],
            color_continuous_scale=["#ef4444", "#f0c040", "#22c55e"],
            labels={"MTBF_h": "MTBF (h)", "Disponibilité_%": "Disponibilité (%)"},
            title="MTBF vs Disponibilité (taille = Coût)",
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5", title_font_color="#e8edf5",
            xaxis=dict(gridcolor="#1a3a6b"), yaxis=dict(gridcolor="#1a3a6b"),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_r:
        fig_tree = px.treemap(
            df, path=["Site", "Type", "AssetID"],
            values="Coût_MAD",
            color="BaselineHealthScore",
            color_continuous_scale=["#ef4444", "#f0c040", "#22c55e"],
            title="Répartition des coûts par site / type",
        )
        fig_tree.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8edf5",
            title_font_color="#e8edf5",
        )
        st.plotly_chart(fig_tree, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PARC ÉQUIPEMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📋 Parc Équipements — Filtres Avancés")

    f1, f2, f3 = st.columns(3)
    with f1:
        sites_sel = st.multiselect("📍 Site géographique", sorted(df["Site"].unique()), default=list(df["Site"].unique()))
    with f2:
        crits_sel = st.multiselect("⚠️ Criticité", sorted(df["Criticité"].unique()), default=list(df["Criticité"].unique()))
    with f3:
        health_range = st.slider("💚 Score de santé", 0, 100, (0, 100))

    df_filt = df[
        df["Site"].isin(sites_sel) &
        df["Criticité"].isin(crits_sel) &
        (df["BaselineHealthScore"] >= health_range[0]) &
        (df["BaselineHealthScore"] <= health_range[1])
    ]

    st.markdown(f"<p style='color:#7fa8d4; font-size:0.9rem;'>🔍 <strong style='color:#f0c040;'>{len(df_filt)}</strong> équipement(s) correspondant aux filtres</p>", unsafe_allow_html=True)

    # Cards view
    cols_per_row = 3
    rows = [df_filt.iloc[i:i+cols_per_row] for i in range(0, len(df_filt), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, eq) in zip(cols, row.iterrows()):
            hs = eq["BaselineHealthScore"]
            color = "#ef4444" if hs < 45 else ("#f0c040" if hs < 70 else "#22c55e")
            with col:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #0d1f3c, #0a1628);
                    border: 1px solid #1a3a6b;
                    border-left: 4px solid {color};
                    border-radius: 12px;
                    padding: 1rem;
                    margin-bottom: 0.8rem;
                ">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-weight:700; color:#ffffff; font-size:0.9rem;">{eq['AssetID']}</span>
                        <span style="background:{color}22; color:{color}; border:1px solid {color}55;
                                     padding:2px 8px; border-radius:20px; font-size:0.7rem; font-weight:600;">
                            {hs}/100
                        </span>
                    </div>
                    <div style="color:#a0b8d8; font-size:0.82rem; margin-bottom:0.3rem;">{eq['Nom']}</div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:0.5rem;">
                        <span style="background:#1e6bb822; color:#7fa8d4; padding:2px 7px; border-radius:10px; font-size:0.72rem;">📍 {eq['Site']}</span>
                        <span style="background:#1e6bb822; color:#7fa8d4; padding:2px 7px; border-radius:10px; font-size:0.72rem;">⚙️ {eq['Type']}</span>
                        <span style="background:#1e6bb822; color:#7fa8d4; padding:2px 7px; border-radius:10px; font-size:0.72rem;">⚠️ {eq['Criticité']}</span>
                    </div>
                    <div style="margin-top:0.6rem; height:4px; background:#1a3a6b; border-radius:2px;">
                        <div style="height:4px; width:{hs}%; background:{color}; border-radius:2px;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:0.5rem; font-size:0.75rem; color:#7fa8d4;">
                        <span>MTBF: {eq['MTBF_h']:.0f}h</span>
                        <span>Dispo: {eq['Disponibilité_%']:.1f}%</span>
                        <span>Coût: {eq['Coût_MAD']/1000:.0f}k MAD</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTES IA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)

    df_alerts = df[df["BaselineHealthScore"] < 45].sort_values("BaselineHealthScore")

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #2d0a0a, #1a0505);
        border: 1px solid #ef444466;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <h3 style='color:#ef4444; margin:0 0 0.5rem;'>🚨 ALERTES IA — {len(df_alerts)} équipement(s) en état critique</h3>
        <p style='color:#f87171; margin:0; font-size:0.9rem;'>
            Ces actifs ont un <strong>BaselineHealthScore inférieur à 45</strong>.
            Une intervention immédiate est recommandée par le système IA pour éviter une panne critique.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if len(df_alerts) == 0:
        st.success("✅ Aucune alerte critique détectée. Tous les équipements sont au-dessus du seuil de 45.")
    else:
        for _, eq in df_alerts.iterrows():
            hs = eq["BaselineHealthScore"]
            urgency = "URGENT" if hs < 30 else "CRITIQUE"
            urg_color = "#ef4444" if hs < 30 else "#f97316"

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1a0a0a, #0d0505);
                border: 1px solid {urg_color}55;
                border-left: 5px solid {urg_color};
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
                margin-bottom: 1rem;
                position: relative;
            ">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
                            <span style="font-weight:800; color:#ffffff; font-size:1rem;">{eq['AssetID']}</span>
                            <span style="background:{urg_color}33; color:{urg_color}; border:1px solid {urg_color};
                                         padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:700;
                                         animation: pulse 2s infinite;">
                                ⚠ {urgency}
                            </span>
                        </div>
                        <div style="color:#f87171; font-size:0.85rem;">{eq['Nom']} — {eq['Type']}</div>
                        <div style="color:#7fa8d4; font-size:0.8rem; margin-top:4px;">📍 {eq['Site']} &nbsp;|&nbsp; Criticité : {eq['Criticité']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:2rem; font-weight:900; color:{urg_color}; line-height:1;">{hs}</div>
                        <div style="font-size:0.72rem; color:#f87171;">Score Santé</div>
                    </div>
                </div>
                <div style="margin-top:0.8rem; height:6px; background:#2d1010; border-radius:3px;">
                    <div style="height:6px; width:{hs}%; background:{urg_color}; border-radius:3px;"></div>
                </div>
                <div style="display:flex; gap:1.5rem; margin-top:0.8rem; font-size:0.8rem; color:#f87171;">
                    <span>⏱ MTTR: <strong style='color:white;'>{eq['MTTR_h']} h</strong></span>
                    <span>📉 MTBF: <strong style='color:white;'>{eq['MTBF_h']:.0f} h</strong></span>
                    <span>📊 Dispo: <strong style='color:white;'>{eq['Disponibilité_%']}%</strong></span>
                    <span>💰 Coût: <strong style='color:white;'>{eq['Coût_MAD']/1000:.0f}k MAD</strong></span>
                </div>
                <div style="margin-top:0.8rem; padding:0.6rem; background:#2d101022; border-radius:8px;
                            border:1px solid #ef444422; font-size:0.82rem; color:#fca5a5;">
                    🤖 <strong>Recommandation IA :</strong>
                    Planifier une inspection immédiate. Score de santé de {hs}/100 indique un risque élevé de défaillance.
                    MTTR estimé : {eq['MTTR_h']}h. Impact coût si panne non prévenue : +{round(eq['Coût_MAD']*0.35/1000,0):.0f}k MAD.
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PLAN DE MAINTENANCE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div style='padding:1.5rem 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### 📅 Plan de Maintenance — Interface Technicien")

    # Init session state for task tracking
    if "task_states" not in st.session_state:
        st.session_state.task_states = {}

    # Build maintenance tasks from data (prioritize low health scores)
    tasks_df = df.sort_values("BaselineHealthScore").head(12).copy()

    for _, eq in tasks_df.iterrows():
        aid = eq["AssetID"]
        if aid not in st.session_state.task_states:
            st.session_state.task_states[aid] = {"statut": "Pas encore", "progression": 0}

        state = st.session_state.task_states[aid]
        hs = eq["BaselineHealthScore"]
        priority_color = "#ef4444" if hs < 45 else ("#f0c040" if hs < 70 else "#22c55e")

        with st.expander(f"⚙️ {aid} — {eq['Nom']} | Santé: {hs}/100 | Site: {eq['Site']}", expanded=(hs < 45)):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                statut = st.selectbox(
                    "📌 Statut de l'intervention",
                    ["Pas encore", "En cours", "Fait"],
                    index=["Pas encore", "En cours", "Fait"].index(state["statut"]),
                    key=f"statut_{aid}",
                )
                st.session_state.task_states[aid]["statut"] = statut

            with c2:
                prog = st.slider(
                    "📊 Progression (%)",
                    0, 100,
                    value=state["progression"],
                    key=f"prog_{aid}",
                )
                st.session_state.task_states[aid]["progression"] = prog

            with c3:
                statut_colors = {"Pas encore": "#7fa8d4", "En cours": "#f0c040", "Fait": "#22c55e"}
                sc = statut_colors.get(statut, "#7fa8d4")
                st.markdown(f"""
                <div style="
                    background:{sc}22; border:2px solid {sc};
                    border-radius:10px; padding:0.8rem;
                    text-align:center; margin-top:1.2rem;
                ">
                    <div style="color:{sc}; font-weight:800; font-size:1.1rem;">{prog}%</div>
                    <div style="color:{sc}; font-size:0.75rem;">{statut}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="
                display:flex; gap:1.5rem; flex-wrap:wrap;
                font-size:0.82rem; color:#7fa8d4; margin-top:0.5rem;
                padding:0.6rem; background:#0d1f3c; border-radius:8px;
            ">
                <span>📅 Prochain: <strong style='color:white;'>{eq['ProchaineMaintenance']}</strong></span>
                <span>🔧 Type: <strong style='color:white;'>{eq['Type']}</strong></span>
                <span>⚠️ Criticité: <strong style='color:{priority_color};'>{eq['Criticité']}</strong></span>
                <span>💰 Budget: <strong style='color:white;'>{eq['Coût_MAD']/1000:.0f}k MAD</strong></span>
            </div>
            """, unsafe_allow_html=True)

    # Global progress summary
    st.markdown("---")
    total = len(tasks_df)
    done = sum(1 for v in st.session_state.task_states.values() if v["statut"] == "Fait")
    in_progress = sum(1 for v in st.session_state.task_states.values() if v["statut"] == "En cours")
    avg_prog = round(sum(v["progression"] for v in st.session_state.task_states.values()) / max(total, 1), 1)

    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("📋 Tâches totales", total)
    with s2: st.metric("✅ Terminées", done)
    with s3: st.metric("🔄 En cours", in_progress)
    with s4: st.metric("📊 Avancement moyen", f"{avg_prog}%")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — QUI SOMMES-NOUS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""
    <div style='padding:1.5rem 1rem 0;'>
    <h3 style='color:#e8edf5;'>👥 Qui Sommes-Nous ?</h3>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0d1f3c, #0a1628);
            border: 1px solid #1a3a6b;
            border-radius: 14px;
            padding: 2rem;
            margin: 0 0.5rem 1.5rem;
        ">
            <div style="
                display:inline-block;
                background: linear-gradient(135deg, #1e6bb822, #f0c04011);
                border: 1px solid #1e6bb855;
                border-radius: 20px;
                padding: 4px 16px;
                font-size: 0.75rem;
                font-weight: 600;
                color: #f0c040;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 1rem;
            ">Projet Académique — Maintenance Industrielle</div>

            <h2 style='color:#ffffff; font-weight:800; margin:0 0 0.5rem; font-size:1.8rem;'>
                ReliabilityFlow × ONEE
            </h2>
            <p style='color:#a0b8d8; line-height:1.7; font-size:0.95rem;'>
                Ce projet s'inscrit dans le cadre de notre formation en
                <strong style='color:#f0c040;'>Maintenance Industrielle</strong>.
                L'objectif est de concevoir et déployer une solution de
                <strong style='color:#1e9bf8;'>Maintenance Prédictive basée sur l'Intelligence Artificielle</strong>
                pour l'Office National de l'Électricité et de l'Eau Potable (ONEE).
            </p>
            <p style='color:#a0b8d8; line-height:1.7; font-size:0.95rem; margin-top:1rem;'>
                Notre application transforme des données industrielles brutes en
                <strong style='color:#22c55e;'>décisions stratégiques prescriptives</strong>,
                permettant une réduction significative des coûts de maintenance et
                une amélioration de la disponibilité du parc équipements.
            </p>

            <div style="margin-top:1.5rem; padding:1rem; background:#0a1220; border-radius:10px; border:1px solid #1a3a6b;">
                <div style="color:#f0c040; font-weight:700; font-size:0.85rem; margin-bottom:0.8rem;">🎯 OBJECTIFS STRATÉGIQUES</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Réduction de 25% des coûts</div>
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Surveillance 24/7 en temps réel</div>
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Anticipation des pannes IA</div>
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Rapports décisionnels auto</div>
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Interface technicien intuitive</div>
                    <div style="color:#a0b8d8; font-size:0.85rem;">✅ Couverture multi-sites ONEE</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        team = [
            {"nom": "Souad Assad", "role": "Chef de Projet & Analyste IA", "icon": "👩‍💻"},
            {"nom": "Équipe Maintenance", "role": "Ingénieurs Terrain", "icon": "⚙️"},
            {"nom": "Direction ONEE", "role": "Sponsor Stratégique", "icon": "🏛️"},
        ]
        for m in team:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0d1f3c, #0a1628);
                border: 1px solid #1a3a6b;
                border-radius: 12px;
                padding: 1.2rem;
                margin: 0 0.5rem 1rem;
                display: flex;
                align-items: center;
                gap: 1rem;
            ">
                <div style="
                    background: linear-gradient(135deg, #1e6bb8, #f0c040);
                    width: 48px; height: 48px;
                    border-radius: 50%;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.5rem; flex-shrink:0;
                ">{m['icon']}</div>
                <div>
                    <div style="font-weight:700; color:#ffffff; font-size:0.95rem;">{m['nom']}</div>
                    <div style="color:#7fa8d4; font-size:0.8rem;">{m['role']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0d2010, #0a1508);
            border: 1px solid #22c55e44;
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0 0.5rem 1rem;
            text-align: center;
        ">
            <div style="color:#22c55e; font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;">
                Stack Technologique
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:6px; justify-content:center;">
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">Python</span>
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">Streamlit</span>
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">Plotly</span>
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">Pandas</span>
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">GitHub</span>
                <span style="background:#1e6bb822; color:#7fa8d4; padding:3px 10px; border-radius:20px; font-size:0.75rem;">Excel / KPIs IA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top: 3rem;
    padding: 1.2rem 2rem;
    background: #050d1a;
    border-top: 1px solid #1a3a6b;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
">
    <span style="color:#3a5a8a; font-size:0.8rem;">
        ⚡ ReliabilityFlow × ONEE — Maintenance Prédictive IA
    </span>
    <span style="color:#3a5a8a; font-size:0.8rem;">
        Filière Maintenance Industrielle | Souad Assad | 2024-2025
    </span>
</div>
""", unsafe_allow_html=True)
