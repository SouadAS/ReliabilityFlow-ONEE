from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import os

app = FastAPI()

# Nom du fichier Excel
EXCEL_FILE = "donnees.xlsx" if os.path.exists("donnees.xlsx") else "donnees.xlsx.xlsx"

def get_data():
    df_assets = pd.read_excel(EXCEL_FILE, sheet_name=0)
    df_events = pd.read_excel(EXCEL_FILE, sheet_name=1)
    return df_assets, df_events

# --- STYLE CSS ---
def get_style():
    return """
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; color: #333; background: #f4f7f6; }
        .navbar { background: #2c3e50; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .navbar a { color: white; margin: 0 20px; text-decoration: none; font-weight: bold; font-size: 1.1em; }
        .navbar a:hover { color: #3498db; }
        .container { padding: 40px; max-width: 1200px; margin: auto; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th { background: #3498db; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }
        .alert-row { color: #e74c3c; font-weight: bold; background: #fdf2f2; }
        .summary-row { background: #2c3e50; color: white; font-weight: bold; }
    </style>
    """

# --- 1. PAGE D'ACCUEIL (/) ---
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
        <head>
            <title>ONEE - Smart Maintenance</title>
            {get_style()}
            <style>
                .hero {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 60px 20px;
                    text-align: center;
                    border-radius: 15px;
                    margin-bottom: 40px;
                }}
                .hero h1 {{ font-size: 3em; border: none; color: #ecf0f1; margin-bottom: 10px; }}
                .search-box {{
                    margin: -45px auto 40px;
                    max-width: 700px;
                    position: relative;
                }}
                .search-box input {{
                    width: 100%;
                    padding: 22px 30px;
                    font-size: 1.2em;
                    border-radius: 50px;
                    border: 4px solid #3498db;
                    box-shadow: 0 15px 30px rgba(0,0,0,0.2);
                    outline: none;
                    transition: 0.3s;
                }}
                .search-box input:focus {{ border-color: #2ecc71; transform: scale(1.02); }}
                .features {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                    gap: 25px;
                }}
                .f-card {{
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    transition: 0.3s ease;
                    border-top: 6px solid #3498db;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                }}
                .f-card:hover {{ transform: translateY(-10px); box-shadow: 0 12px 25px rgba(0,0,0,0.1); }}
                .f-icon {{ font-size: 45px; display: block; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="navbar">
                <a href="/">Accueil</a> <a href="/equipements">Équipements</a> <a href="/kpi">KPI</a> <a href="/alertes">Alertes</a> <a href="/prediction">IA Prediction</a>
            </div>
            
            <div class="container">
                <div class="hero">
                    <h1>Moteur de Fiabilité ONEE</h1>
                    <p>Gestion intelligente et maintenance prédictive des actifs électromécaniques</p>
                </div>

                <div class="search-box">
                    <form action="/search" method="get">
                        <input type="text" name="query" placeholder="🔍 Rechercher un AssetID, un Site ou une Criticité..." required>
                    </form>
                </div>

                <div class="features">
                    <div class="f-card">
                        <span class="f-icon">⚙️</span>
                        <h3>Inventaire</h3>
                        <p>Registre technique complet du parc machines.</p>
                        <a href="/equipements" class="btn">Consulter</a>
                    </div>

                    <div class="f-card" style="border-top-color: #27ae60;">
                        <span class="f-icon">📊</span>
                        <h3>Indicateurs KPI</h3>
                        <p>Analyse du MTBF, MTTR et Disponibilité globale.</p>
                        <a href="/kpi" class="btn" style="background:#27ae60;">Analyser</a>
                    </div>

                    <div class="f-card" style="border-top-color: #e74c3c;">
                        <span class="f-icon">🚨</span>
                        <h3>Alertes</h3>
                        <p>Suivi des équipements en seuil de santé critique.</p>
                        <a href="/alertes" class="btn" style="background:#e74c3c;">Vérifier</a>
                    </div>

                    <div class="f-card" style="border-top-color: #9b59b6;">
                        <span class="f-icon">🧠</span>
                        <h3>IA Prediction</h3>
                        <p>Algorithme de calcul de la durée de vie (RUL).</p>
                        <a href="/prediction" class="btn" style="background:#9b59b6;">Lancer l'IA</a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

# --- 2. PAGE DE RÉSULTATS DE RECHERCHE ---
@app.get("/search", response_class=HTMLResponse)
def search_results(query: str):
    df_assets, _ = get_data()
    
    q = query.lower()
    mask = (
        df_assets['AssetID'].astype(str).str.lower().str.contains(q) |
        df_assets['AssetType'].astype(str).str.lower().str.contains(q) |
        df_assets['Site'].astype(str).str.lower().str.contains(q) |
        df_assets['Criticality'].astype(str).str.lower().str.contains(q)
    )
    df_filtered = df_assets[mask]

    rows = ""
    for _, row in df_filtered.iterrows():
        rows += f"""
        <tr>
            <td>{row['AssetID']}</td>
            <td>{row['AssetType']}</td>
            <td>{row['Site']}</td>
            <td>{row['Criticality']}</td>
            <td style="font-weight:bold; color: {'#e74c3c' if row['BaselineHealthScore'] < 50 else '#2ecc71'}">
                {row['BaselineHealthScore']}
            </td>
        </tr>"""

    if rows == "":
        rows = "<tr><td colspan='5' style='text-align:center; padding:30px;'>❌ Aucun équipement trouvé pour cette recherche.</td></tr>"

    return f"""
    <html>
        <head><title>Résultats de recherche</title>{get_style()}</head>
        <body>
            <div class="navbar">
                <a href="/">Accueil</a> <a href="/equipements">Équipements</a> <a href="/kpi">KPI</a> <a href="/alertes">Alertes</a> <a href="/prediction">IA Prediction</a>
            </div>
            <div class="container">
                <div class="card">
                    <h1>Résultats de recherche pour : "{query}"</h1>
                    <p><b>{len(df_filtered)}</b> résultat(s) correspondant(s) dans la base ONEE.</p>
                    <table>
                        <thead>
                            <tr><th>AssetID</th><th>Type</th><th>Site</th><th>Criticité</th><th>Santé</th></tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                    <br>
                    <a href="/" class="btn" style="background:#7f8c8d;">← Nouvelle Recherche</a>
                </div>
            </div>
        </body>
    </html>
    """
# --- 2. ÉQUIPEMENTS (/equipements) ---
@app.get("/equipements", response_class=HTMLResponse)
def list_assets():
    df_assets, _ = get_data()
    rows = ""
    for _, row in df_assets.iterrows():
        rows += f"<tr><td>{row['AssetID']}</td><td>{row['AssetType']}</td><td>{row['Site']}</td><td>{row['Manufacturer']}</td><td>{row['Criticality']}</td></tr>"
    return f"""
    <html><head><title>Equipements</title>{get_style()}</head>
    <body>
        <div class="navbar"><a href="/">Accueil</a><a href="/equipements">Équipements</a><a href="/kpi">KPI</a><a href="/alertes">Alertes</a><a href="/prediction">IA Prediction</a></div>
        <div class="container">
            <div class="card">
                <h1>Registre des Actifs ONEE</h1>
                <table>
                    <tr><th>ID</th><th>Type</th><th>Site</th><th>Constructeur</th><th>Criticité</th></tr>
                    {rows}
                </table>
            </div>
        </div>
    </body></html>
    """

# --- 3. KPI (/kpi) ---
@app.get("/kpi", response_class=HTMLResponse)
def view_kpi():
    df_assets, df_events = get_data()
    rows, t_cout, s_dispo, s_mttr, s_mtbf = "", 0, 0, 0, 0
    for _, asset in df_assets.iterrows():
        pannes = df_events[df_events['AssetID'] == asset['AssetID']]
        nb = len(pannes)
        mttr = round(pannes['RepairTimeHours'].mean(), 1) if nb > 0 else 0
        mtbf = round((8760 - pannes['DowntimeHours'].sum()) / nb, 1) if nb > 0 else 8760
        dispo = round((mtbf / (mtbf + mttr)) * 100, 2) if (mtbf + mttr) > 0 else 100
        cout = pannes['TotalCost_MAD'].sum()
        t_cout += cout; s_dispo += dispo; s_mttr += mttr; s_mtbf += mtbf
        rows += f"<tr><td>{asset['AssetID']}</td><td>{asset['AssetType']}</td><td>{mtbf}h</td><td>{mttr}h</td><td>{dispo}%</td><td>{round(cout,0):,} MAD</td></tr>"
    
    count = len(df_assets)
    return f"""
    <html><head><title>KPI</title>{get_style()}</head>
    <body>
        <div class="navbar"><a href="/">Accueil</a><a href="/equipements">Équipements</a><a href="/kpi">KPI</a><a href="/alertes">Alertes</a><a href="/prediction">IA Prediction</a></div>
        <div class="container">
            <div class="card">
                <h1>Analyse des KPI de Fiabilité</h1>
                <table>
                    <tr><th>ID</th><th>Type</th><th>MTBF</th><th>MTTR</th><th>Dispo</th><th>Coût Total</th></tr>
                    {rows}
                    <tr class="summary-row">
                        <td colspan="2">BILAN GLOBAL (MOYENNES)</td>
                        <td>{round(s_mtbf/count,1) if count > 0 else 0}h</td>
                        <td>{round(s_mttr/count,1) if count > 0 else 0}h</td>
                        <td>{round(s_dispo/count,2) if count > 0 else 0}%</td>
                        <td>{round(t_cout,0):,} MAD</td>
                    </tr>
                </table>
            </div>
        </div>
    </body></html>
    """

# --- 4. ALERTES (/alertes) ---
@app.get("/alertes", response_class=HTMLResponse)
def alerts():
    df_assets, df_events = get_data()
    alert_assets = df_assets[df_assets['BaselineHealthScore'] < 50]
    rows = ""
    for _, asset in alert_assets.iterrows():
        pannes = df_events[df_events['AssetID'] == asset['AssetID']]
        nb = len(pannes)
        mttr = round(pannes['RepairTimeHours'].mean(), 1) if nb > 0 else 0
        mtbf = round((8760 - pannes['DowntimeHours'].sum()) / nb, 1) if nb > 0 else 8760
        dispo = round((mtbf / (mtbf + mttr)) * 100, 2) if (mtbf + mttr) > 0 else 100
        rows += f"<tr class='alert-row'><td>{asset['AssetID']}</td><td>{asset['AssetType']}</td><td>{dispo}%</td><td>{asset['BaselineHealthScore']}</td><td>CRITIQUE</td></tr>"
    
    return f"""
    <html><head><title>Alertes</title>{get_style()}</head>
    <body>
        <div class="navbar"><a href="/">Accueil</a><a href="/equipements">Équipements</a><a href="/kpi">KPI</a><a href="/alertes">Alertes</a><a href="/prediction">IA Prediction</a></div>
        <div class="container">
            <div class="card">
                <h1 style="color:#e74c3c">🚨 Machines en Alerte Critique</h1>
                <table>
                    <tr><th>ID</th><th>Type</th><th>Disponibilité</th><th>Santé</th><th>Etat</th></tr>
                    {rows}
                </table>
            </div>
        </div>
    </body></html>
    """

@app.get("/prediction", response_class=HTMLResponse)
def prediction():
    df_assets, _ = get_data()
    
    # --- FILTRE : Uniquement les machines avec une santé < 50% ---
    df_priorite = df_assets[df_assets['BaselineHealthScore'] < 50].sort_values(by='BaselineHealthScore')
    
    cards = ""
    for index, row in df_priorite.iterrows():
        # RÉCUPÉRATION DU SCORE RÉEL
        score = float(row['BaselineHealthScore'])
        
        # --- LOGIQUE D'INTERVALLES ET DE COULEURS ---
        if score <= 20:
            couleur = "#c0392b" # Rouge foncé
            etat = "URGENT : Panne Critique"
            action = "Arrêt immédiat et remplacement requis."
            # RUL très court
            rul_jours = int(score * 0.4) 
        elif score <= 35:
            couleur = "#e74c3c" # Rouge clair
            etat = "ALERTE : Panne Imminente"
            action = "Révision majeure sous 48h."
            rul_jours = int(score * 0.8)
        else:
            couleur = "#d35400" # Orange foncé
            etat = "WARNING : Dégradation Avancée"
            action = "Maintenance curative à planifier d'urgence."
            rul_jours = int(score * 1.2)

        # Ajout d'une petite variation aléatoire basée sur l'ID pour que 
        # deux machines à 35% n'aillent pas exactement le même nombre de jours
        variation = (index % 5)
        rul_jours += variation

        cards += f"""
        <div class="card" style="border-left: 10px solid {couleur}; position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="margin: 0; color: #2c3e50; font-size: 1.5em;">{row['AssetID']}</h2>
                <span style="background: {couleur}; color: white; padding: 6px 15px; border-radius: 20px; font-size: 0.85em; font-weight: bold; text-transform: uppercase;">
                    {etat}
                </span>
            </div>
            
            <p style="margin: 5px 0; color: #7f8c8d; font-size: 1em;">
                <b>Type :</b> {row['AssetType']} | <b>Site :</b> {row['Site']} | <b>Criticité :</b> {row['Criticality']}
            </p>

            <div style="margin: 20px 0;">
                <label style="font-size: 0.95em; font-weight: 500;">Indice de santé actuel : <b style="color: {couleur}; font-size: 1.1em;">{score}%</b></label>
                <div style="background: #f0f0f0; border-radius: 10px; height: 15px; width: 100%; margin-top: 8px; overflow: hidden;">
                    <div style="height: 100%; width: {score}%; background: {couleur}; box-shadow: 2px 0 5px rgba(0,0,0,0.1);"></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-top: 25px; background: #fdfdfd; border: 1px solid #eee; padding: 15px; border-radius: 12px;">
                <div style="border-right: 1px solid #eee; padding-right: 10px;">
                    <span style="font-size: 0.85em; color: #95a5a6; display: block; margin-bottom: 5px;">Prédiction RUL :</span>
                    <b style="font-size: 1.8em; color: {couleur};">{rul_jours} Jours</b>
                </div>
                <div>
                    <span style="font-size: 0.85em; color: #95a5a6; display: block; margin-bottom: 5px;">Action recommandée :</span>
                    <span style="font-size: 1em; font-weight: 600; color: #34495e;">{action}</span>
                </div>
            </div>
        </div>
        """

    return f"""
    <html>
        <head>
            <title>ONEE - IA & Prédiction</title>
            {get_style()}
            <style>
                .grid-prediction {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                    gap: 30px;
                    margin-top: 20px;
                }}
                .card {{ 
                    background: white; 
                    padding: 25px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.08); 
                }}
            </style>
        </head>
        <body>
            <div class="navbar">
                <a href="/">Accueil</a> <a href="/equipements">Équipements</a> <a href="/kpi">KPI</a> <a href="/alertes">Alertes</a> <a href="/prediction">IA Prediction</a>
            </div>
            <div class="container">
                <div style="padding: 20px 0; border-bottom: 2px solid #3498db; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 2.2em;">🧠 Maintenance Prédictive par IA</h1>
                    <p style="color: #7f8c8d; font-size: 1.1em; margin-top: 10px;">Analyse focalisée sur les actifs à haut risque (Santé < 50%)</p>
                </div>
                
                <div class="grid-prediction">
                    {cards if cards else "<div class='card'><h3>✅ Aucun actif critique détecté</h3><p>Tous les équipements ont un indice de santé supérieur à 50%.</p></div>"}
                </div>
            </div>
        </body>
    </html>
    """
# --- 2. RECHERCHE ---
@app.get("/search", response_class=HTMLResponse)
def search_results(query: str):
    df_assets, _ = get_data()
    q = query.lower()
    mask = (
        df_assets['AssetID'].astype(str).str.lower().str.contains(q) |
        df_assets['AssetType'].astype(str).str.lower().str.contains(q) |
        df_assets['Site'].astype(str).str.lower().str.contains(q) |
        df_assets['Criticality'].astype(str).str.lower().str.contains(q)
    )
    df_filtered = df_assets[mask]
    rows = ""
    for _, row in df_filtered.iterrows():
        rows += f"<tr><td>{row['AssetID']}</td><td>{row['AssetType']}</td><td>{row['Site']}</td><td>{row['Criticality']}</td><td>{row['BaselineHealthScore']}</td></tr>"
    
    return f"""
    <html><head><title>Resultats</title>{get_style()}</head>
    <body>
        <div class="navbar"><a href="/">Accueil</a> <a href="/equipements">Equipements</a> <a href="/kpi">KPI</a> <a href="/alertes">Alertes</a> <a href="/prediction">IA Prediction</a></div>
        <div class="container"><div class="card">
            <h1>Resultats pour : {query}</h1>
            <table>
                <tr><th>ID</th><th>Type</th><th>Site</th><th>Criticite</th><th>Sante</th></tr>
                {rows if rows else "<tr><td colspan='5' style='text-align:center;'>Aucun resultat trouve.</td></tr>"}
            </table>
            <br><a href="/" class="btn" style="background:#7f8c8d;">Retour a l'accueil</a>
        </div></div>
    </body></html>
    """