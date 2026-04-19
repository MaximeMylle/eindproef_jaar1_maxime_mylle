# Eindwerk Data Science — Medische Risicoanalyse

Analyse van een medische dataset met risico's en pathologieën van werknemers.  
Het project bestaat uit een Jupyter notebook voor de data-analyse en een interactieve Streamlit-applicatie.

---

## Dataset

De dataset bevat **970.917 rijen** na opkuisen (origineel 1.254.667).  
Elke rij koppelt een werknemer aan een risico en een pathologie.

| Gegeven | Waarde |
|---|---|
| Meest voorkomende pathologie | M54.5 — lombalgie basse (41.344×) |
| Meest voorkomend risico | K.A.01 — écran de visualisation (94.380×) |
| Meest voorkomende sector | Activités hospitalières |
| Gemiddelde leeftijd | 40,9 jaar (meest voorkomende groep: 40–49) |
| Meest actief seizoen | Winter |
| Actieve risico's (geen einddatum) | 45,3% |
| Actieve pathologieën (geen einddatum) | 69,2% |

> De `employment_functioncode` ontbreekt bij **99,3%** van de rijen en is daardoor beperkt bruikbaar.

---

## Projectstructuur

```
├── Data/               ← Ruwe CSV-bestanden (niet in git)
├── Lib/
│   ├── data_laden.py   ← Inlezen en samenvoegen van alle CSV-bestanden
│   ├── data_opkuisen.py← Opkuisen, verrijken en filteren
│   └── visualisaties.py← Alle Plotly-plotfuncties
├── Notebooks/
│   └── analyse.ipynb   ← Volledige data-analyse
├── App/
│   └── app.py          ← Interactieve Streamlit-applicatie
├── CLAUDE.md           ← Projectconventies
└── requirements.txt
```

---

## Starten

```bash
pip install -r requirements.txt
```

**Notebook:**
```bash
jupyter notebook Notebooks/analyse.ipynb
```

**Streamlit-app:**
```bash
cd App
streamlit run app.py
```

---

## Deel 1 — Notebook (`Notebooks/analyse.ipynb`)

### 1. Data inlezen
Laadt `rawdata.csv` en voegt de opzoektabellen samen (NACE-sectoren, risico-omschrijvingen, ICD-10 labels, geslacht). Na het laden bevat het DataFrame 19 kolommen.

### 2. Data opkuisen
Verwijdert ongeldige risico-codes (`SIG`, `SIA`, `SI`, `SIR1`, `SIR2`, `SIG_DECL`, `SIA_DECL`, `SIR_DECL`, `AUTRE`, `SIR2_décl`) en pathologie-code `999999`. Voegt de kolommen `leeftijdsgroep` en `seizoen` toe.

### 3. Algemene informatie
Overzicht van de datastructuur: datatypes, ontbrekende waarden per kolom, unieke waarden en leeftijdsstatistieken.

### 4. Visualisaties

| Sectie | Inhoud |
|---|---|
| **4.1** Alle jaren | Top 10 risico's, pathologieën en risico–pathologie combinaties |
| **4.2** Laatste 5 jaar | Dezelfde top 10's gefilterd op recente data |
| **4.3** Actief | Top 10 risico's en pathologieën zonder einddatum (45% / 69%) |
| **4.4** Demografie | Per geslacht en per leeftijdsgroep; 4.4.1: Man vs. Vrouw naast elkaar |
| **4.5** Seizoenen | Per seizoen; 4.5.1: 76 seizoensgebonden pathologieën (≥70% in één seizoen) |
| **4.6** NACE-sector | Heatmap risico's en pathologieën voor de top 10 sectoren |
| **4.7** Functiecode | Risico's en pathologieën per functiecode (beperkte data) |

---

## Deel 2 — Streamlit-app (`App/app.py`)

Interactief dashboard op basis van dezelfde plotfuncties als de notebook.

**Filters (zijbalk):**
- Geslacht
- Jaarbereik (op basis van pathologie-startdatum)
- NACE-sector (max. 10)
- Leeftijdsgroep

**Tabs:**

| Tab | Inhoud |
|---|---|
| Risico's | Top 10, per NACE-sector, per functiecode |
| Pathologieën | Top 10, per NACE-sector, per functiecode |
| Combinaties & Seizoenen | Top 10 combinaties, per seizoen (selecteerbaar: top 5/10/20), seizoensgebonden pathologieën |
| Demografie | Per geslacht, per leeftijdsgroep en Man vs. Vrouw (selecteerbaar: top 5/10/20) |

---

## Technische keuzes

- **Pandas** voor data-verwerking (1M+ rijen)
- **Plotly** voor alle visualisaties (interactief in notebook én app)
- **Streamlit** met `@st.cache_data` voor performantie
- Logaritmische kleurschaal in heatmaps om uitschieters op te vangen
- Alle code, commentaar en labels in het **Nederlands**
