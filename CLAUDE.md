# CLAUDE.md — Projectconventies Eindwerk Data Science

Dit bestand beschrijft de afspraken en conventies voor dit project.
Het doel is consistentie te bewaren doorheen alle sessies en bijdragen.

---

## Taalvereiste

**Alle code, commentaar, docstrings en Markdown-koppen moeten in het Nederlands zijn.**

Dit geldt voor:
- Variabelenamen en functienamen (bv. `df_gefilterd`, `laad_data`, `kuise_op`)
- Docstrings en inline commentaar
- Markdown-titels in de Jupyter notebook
- Labels, titels en as-beschrijvingen in visualisaties
- Streamlit teksten (titels, labels, knoppen)

---

## Naamgevingsconventies

- **snake_case** voor alle variabelen en functies
- Nederlandstalige namen:
  - DataFrames: `df_ruw`, `df`, `df_gefilterd`, `df_laatste_5_jaar`
  - Functies: `laad_alle_data`, `kuise_data_op`, `verwijder_ongeldige_risicos`
  - Kolommen (toegevoegd): `geslacht_label`, `nace_omschrijving`, `risk_omschrijving`, `leeftijdsgroep`, `seizoen`

---

## Projectstructuur

```
MMYLLE_EINDWERK_JAAR_1_V2/
├── CLAUDE.md                 ← dit bestand
├── requirements.txt          ← pakketdependenties
├── Data/                     ← ruwe CSV-bestanden (niet aanpassen)
│   ├── rawdata.csv
│   ├── Nace.csv
│   ├── Risk.csv
│   └── Sex.csv
├── Lib/                      ← herbruikbare Python-modules
│   ├── __init__.py
│   ├── data_laden.py         ← data inlezen en lookup-merges
│   ├── data_opkuisen.py      ← opkuisen, verrijken, filteren
│   └── visualisaties.py      ← alle plotfuncties (Plotly)
├── Notebooks/
│   └── analyse.ipynb         ← hoofdanalyse
└── App/
    └── app.py                ← Streamlit-applicatie
```

---

## Imports in notebook en app

Bovenaan elke notebook of app de rootmap aan `sys.path` toevoegen:

```python
import sys, os
sys.path.insert(0, os.path.abspath('..'))   # vanuit Notebooks/ of App/
from Lib.data_laden import laad_alle_data
from Lib.data_opkuisen import kuise_data_op, filter_laatste_n_jaar
from Lib import visualisaties as vis
```

---

## Gegevensbestanden

| Bestand       | Encoding  | Scheidingsteken | Opmerking                          |
|---------------|-----------|-----------------|-------------------------------------|
| rawdata.csv   | UTF-8     | `;`             | 1,16M+ rijen, `NULL` als tekst      |
| Nace.csv      | UTF-8-sig | `;`             | Geen kolomnamen in bestand          |
| Risk.csv      | UTF-8-sig | `;`             | Geen kolomnamen in bestand          |
| Sex.csv       | UTF-8-sig | `;`             | Geen kolomnamen, 3 rijen            |
| icd10.csv     | UTF-8-sig | `;`             | Geen kolomnamen, BOM aanwezig, 17 833 rijen |

### NULL-behandeling

`'NULL'`-strings in rawdata.csv worden bij inlezen omgezet naar `pd.NA`.

### Te verwijderen risico-codes

Bij het opkuisen worden rijen met de volgende `risk_code` waarden verwijderd:
`SIG`, `SIA`, `SI`, `SIR1`, `SIR2`, `SIG_DECL`, `SIA_DECL`, `SIR_DECL`

---

## Visualisaties

- **Bibliotheek**: Plotly (`plotly.graph_objects` en `plotly.express`)
- Alle plotfuncties staan in `Lib/visualisaties.py`
- Elke functie accepteert een DataFrame en retourneert een `go.Figure`
- Functies zijn herbruikbaar in zowel de notebook als de Streamlit-app
- As-labels, titels en legenda's: altijd in het Nederlands

### Seizoenen (op basis van `pathology_startdate`)

| Seizoen | Maanden         |
|---------|-----------------|
| Lente   | maart – mei     |
| Zomer   | juni – augustus |
| Herfst  | september – november |
| Winter  | december – februari |

### Leeftijdsgroepen

Aangemaakt via `pd.cut()` in stappen van 10 jaar: `0–9`, `10–19`, ..., `90+`

---

## Aandachtspunten

- `pathology_icd10code` bevat trailing spaties → altijd `.str.strip()` toepassen
- `employment_functioncode` is grotendeels `NULL` → vermeld dit in notebook en app
- Leeftijden < 0 of > 100 zijn outliers → enkel filteren in visualisaties, niet in de ruwe data
- NACE-plots tonen enkel de top 10 meest voorkomende sectoren (742 unieke codes totaal)
- Gebruik `@st.cache_data` in Streamlit voor performantie
- Gebruik categorische dtypes voor kolommen met weinig unieke waarden

---

## Werkwijze

1. Lees bestaande code voor je aanpassingen doet
2. Werk stap voor stap, cel per cel in de notebook
3. Test plotfuncties individueel in de notebook voor gebruik in de app
4. Houd `Lib/` zuiver: enkel herbruikbare logica, geen notebook-specifieke code
