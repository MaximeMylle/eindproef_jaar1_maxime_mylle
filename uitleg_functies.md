# Uitleg Python-functies — Eindwerk Data Science

Overzicht van alle functies voor het **laden, opkuisen en filteren** van de dataset.
Bedoeld als spiekbriefje voor de presentatie.

---

## Overzicht: hoe hangt alles samen?

```
rawdata.csv  ──┐
Nace.csv     ──┤  laad_alle_data()  ──►  df (ruw)
Risk.csv     ──┤
Sex.csv      ──┤                             │
icd10.csv    ──┘                             │
                                             ▼
                                    kuise_data_op()  ──►  df (klaar voor analyse)
                                             │
                          ┌──────────────────┼───────────────────────┐
                          ▼                  ▼                       ▼
               filter_laatste_n_jaar()  filter_op_periode()    (direct gebruiken)
```

---

## Bestand 1 — `Lib/data_laden.py`

> **Doel:** alle CSV-bestanden van schijf lezen en samenvoegen tot één grote tabel.

---

### `laad_ruwe_data(pad)`

**Wat doet het?**
Leest `rawdata.csv` in — dat is de grote dataset met meer dan 1 miljoen rijen.

**Aandachtspunten:**
- Scheidingsteken is `;` (geen komma)
- De tekst `"NULL"` in het bestand wordt automatisch omgezet naar een echte lege waarde (`pd.NA`)
- `low_memory=False` vermijdt waarschuwingen bij grote bestanden

**Resultaat:** een DataFrame met alle rijen en kolommen, nog ongefilterd.

```python
df_ruw = laad_ruwe_data('../Data/rawdata.csv')
# → 1 254 667 rijen, 15 kolommen
```

---

### `laad_nace(pad)`

**Wat doet het?**
Leest `Nace.csv` in — een kleine opzoektabel die NACE-codes omzet naar sectorbeschrijvingen.

**Aandachtspunten:**
- Het bestand heeft **geen kolomnamen** → we geven ze zelf mee: `nace_code` en `nace_omschrijving`
- Encoding `utf-8-sig` zorgt dat het BOM-teken (onzichtbaar teken vooraan het bestand) niet in de data terechtkomt
- Spaties worden weggehaald met `.str.strip()`

**Resultaat:**

| nace_code | nace_omschrijving |
|-----------|-------------------|
| 86.10Z    | Activités hospitalières |
| 85.31Z    | Enseignement secondaire général |
| ...       | ... |

---

### `laad_risicos(pad)`

**Wat doet het?**
Leest `Risk.csv` in — opzoektabel van risico-codes naar omschrijvingen.

**Aandachtspunten:**
- Zelfde structuur als Nace: geen kolomnamen, geeft kolommen `risk_code` en `risk_omschrijving`
- `on_bad_lines="skip"` slaat eventueel kapotte regels over (bv. als er een `;` in de omschrijving zit)

**Resultaat:**

| risk_code | risk_omschrijving |
|-----------|-------------------|
| K.A.01    | écran de visualisation |
| K.B.02    | bruit |
| ...       | ... |

---

### `laad_geslacht(pad)`

**Wat doet het?**
Leest `Sex.csv` in — een mini-tabel met 3 rijen die getallen omzet naar geslachtslabels.

**Aandachtspunten:**
- De originele labels zijn in het Frans: `Indéfini`, `Homme`, `Femme`
- We vertalen ze meteen naar het Nederlands: `Onbepaald`, `Man`, `Vrouw`
- De code-kolom wordt omgezet naar een integer zodat de koppeling later klopt

**Resultaat:**

| geslacht_code | geslacht_label |
|---------------|----------------|
| 0 | Onbepaald |
| 1 | Man |
| 2 | Vrouw |

---

### `laad_icd10(pad)`

**Wat doet het?**
Leest `icd10.csv` in — de internationale ICD-10 thesaurus met 17 833 codes en hun Franstalige omschrijving.

**Aandachtspunten:**
- Het BOM-teken (`\ufeff`) kan in de eerste code terechtgekomen zijn → wordt handmatig weggehaald met `.str.lstrip("\ufeff")`
- Rijen zonder geldige code worden gefilterd

**Resultaat:**

| pathology_icd10code | pathologie_omschrijving |
|---------------------|-------------------------|
| M54.5 | lombalgie basse |
| H52.1 | myopie |
| B97.2 | coronavirus comme cause de maladies... |
| ... | ... |

---

### `laad_alle_data(data_map)` ⭐ hoofdfunctie

**Wat doet het?**
Roept alle bovenstaande functies aan en plakt alles aan elkaar via **merges** (vergelijkbaar met een SQL JOIN).

**Stap voor stap:**
1. Laad `rawdata.csv` als basisDataFrame
2. Laad de 4 opzoektabellen (Nace, Risk, Sex, ICD-10)
3. Koppel geslachtslabel op `employee_sex`
4. Koppel NACE-omschrijving op `nace_code`
5. Koppel risico-omschrijving op `risk_code`
6. Koppel ICD-10 omschrijving op `pathology_icd10code`

Alle koppelingen zijn `how="left"` — dit betekent: **behoud alle rijen uit de hoofdtabel**, ook als er geen overeenkomst is in de opzoektabel (dan krijgt die rij `NaN`).

**Resultaat:** 1 DataFrame met 19 kolommen — de originele data plus de toegevoegde omschrijvingen.

```python
df = laad_alle_data('../Data')
# Toegevoegde kolommen: geslacht_label, nace_omschrijving,
#                       risk_omschrijving, pathologie_omschrijving
```

---

## Bestand 2 — `Lib/data_opkuisen.py`

> **Doel:** de ruwe data schoonmaken, aanvullen met berekende kolommen, en filteren.

---

### Constante: `TE_VERWIJDEREN_RISICOS`

**Wat is het?**
Een vaste lijst van risico-codes die **geen echte blootstellingsrisico's** zijn. Ze zijn door vroegere datamigratiefouten als risico-codes opgeslagen, maar stellen eigenlijk het type medisch toezicht voor (SIG, SIA, SIR).

```python
TE_VERWIJDEREN_RISICOS = {
    "SIG", "SIA", "SI", "SIR1", "SIR2",
    "SIG_DECL", "SIA_DECL", "SIR_DECL",
    "AUTRE", "SIR2_décl"
}
```

---

### `verwijder_ongeldige_risicos(df)`

**Wat doet het?**
Verwijdert alle rijen waarvan de `risk_code` in de bovenstaande lijst staat.

**Hoe werkt het technisch?**
```python
masker = ~df["risk_code"].isin(TE_VERWIJDEREN_RISICOS)
#  ~  betekent "NIET in de lijst"
#  isin() controleert voor elke rij of de waarde in de set zit
```

**Resultaat:** 283 750 rijen worden verwijderd (22,6% van de data).

---

### `verwijder_ongeldige_pathologieen(df)`

**Wat doet het?**
Verwijdert rijen met ICD-10 code `999999` — een ongeldige code die gebruikt werd als plaatshouder.

**Bijzonderheid:**
Omdat datums soms als getal worden ingelezen, kan de waarde `999999.0` (met decimaal) zijn ipv `999999`. Daarom wordt eerst de `.0` weggehaald voor de vergelijking:

```python
genormaliseerd = df["pathology_icd10code"].astype(str).str.replace(r"\.0$", "", regex=True)
#  r"\.0$"  is een reguliere expressie: verwijder ".0" op het einde van de tekst
```

---

### `strip_icd10_spaties(df)`

**Wat doet het?**
Verwijdert onzichtbare spaties voor en achter de ICD-10 code.

**Waarom nodig?**
In de brondata staan soms spaties in de code: `" M54.5"` of `"M54.5 "`. Hierdoor matcht een koppeling met de opzoektabel niet. `.str.strip()` lost dit op.

```python
df["pathology_icd10code"] = df["pathology_icd10code"].str.strip()
```

---

### `parseer_datums(df)`

**Wat doet het?**
Converteert 7 tekstkolommen naar echte datum-objecten (`datetime`).

**Waarom nodig?**
CSV-bestanden kennen geen datumtype — alles is tekst. Pas na de conversie kunnen we rekenen met datums (verschil berekenen, filteren op jaar, maand opvragen...).

De kolommen die worden omgezet:
- `employee_birthdate` — geboortedatum werknemer
- `employment_startdate` / `employment_enddate` — begin/einde tewerkstelling
- `risk_startdate` / `risk_enddate` — begin/einde risicoblootstelling
- `pathology_startdate` / `pathology_enddate` — begin/einde pathologie

```python
df[kolom] = pd.to_datetime(df[kolom], errors="coerce")
#  errors="coerce"  → ongeldige datums worden NaT (Not a Time) ipv een fout
```

---

### `voeg_leeftijdsgroep_toe(df)`

**Wat doet het?**
Berekent op basis van `employee_age_start_pathology` in welke leeftijdsgroep de werknemer valt en slaat dat op in een nieuwe kolom `leeftijdsgroep`.

**Hoe werkt `pd.cut()`?**
`pd.cut()` verdeelt een reeks getallen in vakjes (bins):

```
Leeftijd 27  →  valt in  [20, 30)  →  label "20–29"
Leeftijd 54  →  valt in  [50, 60)  →  label "50–59"
```

De grenzen gaan van 0 tot 100, in stappen van 10, met een extra groep `100+`.

**Resultaat:** nieuwe kolom met categorische waarden: `0–9`, `10–19`, ..., `90–99`, `100+`.

---

### `voeg_seizoen_toe(df)`

**Wat doet het?**
Kijkt naar de **maand** van `pathology_startdate` en voegt een seizoenslabel toe.

**Indeling:**

| Maanden | Seizoen |
|---------|---------|
| maart – mei (3, 4, 5) | Lente |
| juni – augustus (6, 7, 8) | Zomer |
| september – november (9, 10, 11) | Herfst |
| december – februari (12, 1, 2) | Winter |

```python
df["seizoen"] = df["pathology_startdate"].dt.month.map(_maand_naar_seizoen)
#  .dt.month  haalt het maandnummer op uit een datum
#  .map()     past de hulpfunctie toe op elke waarde
```

---

### `filter_laatste_n_jaar(df, n=5)`

**Wat doet het?**
Geeft enkel de rijen terug waarvan de `pathology_startdate` in de **laatste n jaar** valt (standaard 5 jaar).

**Hoe werkt het?**
```python
grens = pd.Timestamp.now() - pd.DateOffset(years=n)
# Vandaag min 5 jaar = de grensdatum
# Behoud alleen rijen met startdatum >= grensdat
```

**Gebruik in de notebook:**
```python
df_5j = filter_laatste_n_jaar(df, n=5)
# → bevat alleen data van de laatste 5 jaar (~200 000 rijen)
```

---

### `filter_op_periode(df, jaar_van, jaar_tot)`

**Wat doet het?**
Filtert op een **specifiek historisch tijdvenster**: van `jaar_van` (inclusief) tot `jaar_tot` (exclusief).

```python
df_1990_2000 = filter_op_periode(df, 1990, 2000)
# → alle rijen waarbij pathologie begon in 1990, 1991, ..., 1999

df_2000_2010 = filter_op_periode(df, 2000, 2010)
# → alle rijen waarbij pathologie begon in 2000, 2001, ..., 2009
```

**Technisch:**
```python
(df["pathology_startdate"].dt.year >= jaar_van)   # 1990 of later
& (df["pathology_startdate"].dt.year <  jaar_tot)  # strikt voor 2000
```

---

### `kuise_data_op(df)` ⭐ hoofdfunctie

**Wat doet het?**
Roept **alle opkuisfuncties** in de juiste volgorde aan. Dit is de enige functie die je in de notebook hoeft aan te roepen.

**Volgorde:**
1. `verwijder_ongeldige_risicos()` — ongeldige risico-codes weg
2. `verwijder_ongeldige_pathologieen()` — code 999999 weg
3. `strip_icd10_spaties()` — spaties uit ICD-10 codes
4. `parseer_datums()` — tekst naar datum-objecten
5. `voeg_leeftijdsgroep_toe()` — nieuwe kolom `leeftijdsgroep`
6. `voeg_seizoen_toe()` — nieuwe kolom `seizoen`

```python
df = kuise_data_op(df_ruw)
# Van 1 254 667 rijen naar 970 917 rijen — klaar voor analyse
```

---

## Samenvatting: de 2 aanroepen in de notebook

```python
# Stap 1: alles inlezen en samenvoegen
df_ruw = laad_alle_data('../Data')

# Stap 2: opkuisen en verrijken
df = kuise_data_op(df_ruw)

# Optioneel: filteren op periode
df_5j          = filter_laatste_n_jaar(df, n=5)
df_1990_2000   = filter_op_periode(df, 1990, 2000)
df_2000_2010   = filter_op_periode(df, 2000, 2010)
```

Alle verdere analyse en visualisaties werken op `df` of een gefilterde versie ervan.
