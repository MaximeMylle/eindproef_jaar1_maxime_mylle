"""
visualisaties.py
----------------
Alle plotfuncties voor de data-analyse en de Streamlit-applicatie.
Elke functie accepteert een (gefilterde) DataFrame en retourneert een Plotly-figuur.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Kleurpalet voor consistente stijl
KLEUR_PRIMAIR = "#2E86AB"
KLEUR_REEKS = px.colors.qualitative.Set2

# Centrale layoutstijl voor alle plots — zorgt voor leesbare, donkere tekst
LAYOUT_STIJL = dict(
    plot_bgcolor="#F0F2F6",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1a1a1a", size=13),
    title_font=dict(color="#1a1a1a", size=16),
    xaxis=dict(
        tickfont=dict(color="#1a1a1a"),
        title_font=dict(color="#1a1a1a"),
        gridcolor="#D0D3DA",
        linecolor="#888888",
    ),
    yaxis=dict(
        tickfont=dict(color="#1a1a1a"),
        title_font=dict(color="#1a1a1a"),
        gridcolor="#D0D3DA",
        linecolor="#888888",
    ),
    legend=dict(
        font=dict(color="#1a1a1a"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#CCCCCC",
        borderwidth=1,
    ),
    margin=dict(l=20, r=20, t=55, b=20),
)


# ─── Hulpfunctie ICD-10 labels ──────────────────────────────────────────────

def _icd10_label(df: pd.DataFrame) -> pd.Series:
    """
    Geeft een Series terug met 'CODE — omschrijving' als label per rij.
    Valt terug op enkel de code als pathologie_omschrijving niet beschikbaar is.
    """
    if "pathologie_omschrijving" in df.columns:
        return (
            df["pathology_icd10code"].fillna("Onbekend")
            + " — "
            + df["pathologie_omschrijving"].fillna("")
        )
    return df["pathology_icd10code"].fillna("Onbekend")


def _icd10_label_map(df: pd.DataFrame) -> dict:
    """
    Geeft een dict {icd10code: 'CODE — omschrijving'} terug voor gebruik in plots.
    """
    if "pathologie_omschrijving" in df.columns:
        dedup = df[["pathology_icd10code", "pathologie_omschrijving"]].drop_duplicates("pathology_icd10code")
        return {
            row["pathology_icd10code"]: f"{row['pathology_icd10code']} — {row['pathologie_omschrijving'] or ''}"
            for _, row in dedup.iterrows()
        }
    return {}


# ─── Algemene helper ────────────────────────────────────────────────────────

def maak_top_barchart(
    serie: pd.Series,
    titel: str,
    x_label: str,
    y_label: str,
    top_n: int = 10,
    horizontaal: bool = True,
) -> go.Figure:
    """
    Maakt een bar chart van de top-n waarden in een Series.

    Parameters
    ----------
    serie : pd.Series
        Series met waarden en hun aantallen (value_counts-formaat)
    titel : str
    x_label : str
    y_label : str
    top_n : int
    horizontaal : bool
        Indien True worden de balken horizontaal weergegeven

    Returns
    -------
    go.Figure
    """
    top = serie.head(top_n)

    if horizontaal:
        fig = go.Figure(go.Bar(
            x=top.values,
            y=top.index.astype(str),
            orientation="h",
            marker_color=KLEUR_PRIMAIR,
            text=top.values,
            textposition="outside",
            textfont=dict(color="#1a1a1a"),
        ))
        fig.update_layout(
            **LAYOUT_STIJL,
            title=titel,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=max(400, top_n * 45),
        )
        fig.update_yaxes(autorange="reversed")
    else:
        fig = go.Figure(go.Bar(
            x=top.index.astype(str),
            y=top.values,
            marker_color=KLEUR_PRIMAIR,
            text=top.values,
            textposition="outside",
            textfont=dict(color="#1a1a1a"),
        ))
        fig.update_layout(
            **LAYOUT_STIJL,
            title=titel,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=450,
        )

    return fig


# ─── Top 10 actieve risico's en pathologieën ────────────────────────────────

def plot_top10_actieve_risicos(df: pd.DataFrame, titel_suffix: str = "") -> go.Figure:
    """
    Top 10 meest voorkomende **actieve** risico's.
    Actief = geen einddatum (risk_enddate is leeg).

    Parameters
    ----------
    df : pd.DataFrame
    titel_suffix : str

    Returns
    -------
    go.Figure
    """
    df_actief = df[df["risk_enddate"].isna()].copy()

    if "risk_omschrijving" in df_actief.columns:
        label = df_actief["risk_code"].fillna("Onbekend") + " — " + df_actief["risk_omschrijving"].fillna("")
    else:
        label = df_actief["risk_code"].fillna("Onbekend")

    tellingen = label.value_counts()

    titel = "Top 10 actieve risico's (zonder einddatum)"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "Risico", top_n=10)


def plot_top10_actieve_pathologieen(df: pd.DataFrame, titel_suffix: str = "") -> go.Figure:
    """
    Top 10 meest voorkomende **actieve** pathologieën.
    Actief = geen einddatum (pathology_enddate is leeg).

    Parameters
    ----------
    df : pd.DataFrame
    titel_suffix : str

    Returns
    -------
    go.Figure
    """
    df_actief = df[df["pathology_enddate"].isna()].copy()

    if "pathologie_omschrijving" in df_actief.columns:
        label = (
            df_actief["pathology_icd10code"].fillna("Onbekend")
            + " — "
            + df_actief["pathologie_omschrijving"].fillna("")
        )
    else:
        label = df_actief["pathology_icd10code"].fillna("Onbekend")

    tellingen = label[df_actief["pathology_icd10code"].notna()].value_counts()

    titel = "Top 10 actieve pathologieën (zonder einddatum)"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "Pathologie", top_n=10)


# ─── Top 10 risico's ────────────────────────────────────────────────────────

def plot_top10_risicos(df: pd.DataFrame, titel_suffix: str = "") -> go.Figure:
    """
    Top 10 meest voorkomende risico's (op basis van risk_code + omschrijving).

    Parameters
    ----------
    df : pd.DataFrame
    titel_suffix : str
        Bijkomende tekst voor de titel (bv. 'Laatste 5 jaar')

    Returns
    -------
    go.Figure
    """
    # Label samenstellen: code + omschrijving (indien beschikbaar)
    if "risk_omschrijving" in df.columns:
        label = df["risk_code"].fillna("Onbekend") + " — " + df["risk_omschrijving"].fillna("")
    else:
        label = df["risk_code"].fillna("Onbekend")

    tellingen = label.value_counts()

    titel = "Top 10 meest voorkomende risico's"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "Risico", top_n=10)


# ─── Top 10 pathologieën ─────────────────────────────────────────────────────

def plot_top10_pathologieen(df: pd.DataFrame, titel_suffix: str = "") -> go.Figure:
    """
    Top 10 meest voorkomende pathologieën (ICD-10 code).

    Parameters
    ----------
    df : pd.DataFrame
    titel_suffix : str

    Returns
    -------
    go.Figure
    """
    # Label samenstellen: code + omschrijving (indien beschikbaar)
    if "pathologie_omschrijving" in df.columns:
        label = (
            df["pathology_icd10code"].fillna("Onbekend")
            + " — "
            + df["pathologie_omschrijving"].fillna("")
        )
    else:
        label = df["pathology_icd10code"].fillna("Onbekend")

    tellingen = label[df["pathology_icd10code"].notna()].value_counts()

    titel = "Top 10 meest voorkomende pathologieën"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "Pathologie", top_n=10)


# ─── Top 10 risico-pathologie combinaties ────────────────────────────────────

def plot_top10_risico_pathologie_combo(df: pd.DataFrame, titel_suffix: str = "") -> go.Figure:
    """
    Top 10 meest voorkomende combinaties van risico en pathologie.

    Parameters
    ----------
    df : pd.DataFrame
    titel_suffix : str

    Returns
    -------
    go.Figure
    """
    risico_label = (
        df["risk_code"].fillna("Onbekend") + " — " + df["risk_omschrijving"].fillna("")
        if "risk_omschrijving" in df.columns
        else df["risk_code"].fillna("Onbekend")
    )
    pathologie_label = (
        df["pathology_icd10code"].fillna("Onbekend") + " — " + df["pathologie_omschrijving"].fillna("")
        if "pathologie_omschrijving" in df.columns
        else df["pathology_icd10code"].fillna("Onbekend")
    )
    combo = risico_label + "  ×  " + pathologie_label
    tellingen = combo.value_counts()

    titel = "Top 10 meest voorkomende risico–pathologie combinaties"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "Combinatie", top_n=10)


# ─── Pathologieën per geslacht ───────────────────────────────────────────────

def plot_pathologie_per_geslacht(df: pd.DataFrame, top_n: int = 5) -> go.Figure:
    """
    Top-n meest voorkomende pathologieën per geslacht (grouped bar chart).

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    if "geslacht_label" not in df.columns:
        geslacht_kolom = "employee_sex"
    else:
        geslacht_kolom = "geslacht_label"

    # Top-n pathologieën over alle geslachten
    top_pats = df["pathology_icd10code"].dropna().value_counts().head(top_n).index.tolist()
    label_map = _icd10_label_map(df)

    df_gefilterd = df[df["pathology_icd10code"].isin(top_pats)].copy()
    df_gefilterd["pathologie_label"] = df_gefilterd["pathology_icd10code"].map(label_map).fillna(df_gefilterd["pathology_icd10code"])

    tellingen = (
        df_gefilterd.groupby([geslacht_kolom, "pathologie_label"])
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="pathologie_label",
        y="aantal",
        color=geslacht_kolom,
        barmode="group",
        title=f"Top {top_n} pathologieën per geslacht",
        labels={
            "pathologie_label": "Pathologie",
            "aantal": "Aantal",
            geslacht_kolom: "Geslacht",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=450)
    return fig


# ─── Pathologieën per seizoen ────────────────────────────────────────────────

def plot_pathologie_per_seizoen(df: pd.DataFrame, top_n: int = 5) -> go.Figure:
    """
    Top-n meest voorkomende pathologieën per seizoen.

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    if "seizoen" not in df.columns:
        return go.Figure().update_layout(title="Geen seizoensdata beschikbaar")

    top_pats = df["pathology_icd10code"].dropna().value_counts().head(top_n).index.tolist()
    label_map = _icd10_label_map(df)

    df_gefilterd = df[df["pathology_icd10code"].isin(top_pats)].copy()
    df_gefilterd["pathologie_label"] = df_gefilterd["pathology_icd10code"].map(label_map).fillna(df_gefilterd["pathology_icd10code"])

    volgorde = ["Lente", "Zomer", "Herfst", "Winter"]

    tellingen = (
        df_gefilterd.groupby(["seizoen", "pathologie_label"])
        .size()
        .reset_index(name="aantal")
    )
    tellingen["seizoen"] = pd.Categorical(tellingen["seizoen"], categories=volgorde, ordered=True)
    tellingen = tellingen.sort_values("seizoen")

    fig = px.bar(
        tellingen,
        x="seizoen",
        y="aantal",
        color="pathologie_label",
        barmode="group",
        title=f"Top {top_n} pathologieën per seizoen",
        labels={
            "seizoen": "Seizoen",
            "aantal": "Aantal",
            "pathologie_label": "Pathologie",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=450)
    return fig


# ─── Risico's per NACE-sector ────────────────────────────────────────────────

def plot_risico_per_nace(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Meest voorkomende risico per NACE-sector (top-n sectoren).
    Toont een heatmap van de aantallen.

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    # Nace-label bepalen
    nace_kolom = "nace_omschrijving" if "nace_omschrijving" in df.columns else "nace_code"

    # Top-n NACE-sectoren op basis van totaal aantal rijen
    top_nace = df[nace_kolom].dropna().value_counts().head(top_n).index.tolist()
    # Top-5 risico's over alle sectoren
    top_risicos = df["risk_code"].dropna().value_counts().head(5).index.tolist()

    df_gefilterd = df[
        df[nace_kolom].isin(top_nace) & df["risk_code"].isin(top_risicos)
    ].copy()

    tellingen = (
        df_gefilterd.groupby([nace_kolom, "risk_code"])
        .size()
        .reset_index(name="aantal")
    )

    pivot = tellingen.pivot(index=nace_kolom, columns="risk_code", values="aantal").fillna(0)

    # Verkort lange NACE-namen voor leesbaarheid
    pivot.index = [str(n)[:50] + "…" if len(str(n)) > 50 else str(n) for n in pivot.index]

    werkelijke_waarden = pivot.values.astype(int)
    # Log-schaal voor kleur zodat uitschieters de schaal niet domineren
    log_waarden = np.log1p(pivot.values)

    fig = go.Figure(go.Heatmap(
        z=log_waarden,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Blues",
        text=werkelijke_waarden,
        texttemplate="%{text}",
        showscale=True,
        colorbar=dict(
            title="Aantal (log)",
            tickvals=[np.log1p(v) for v in [1, 10, 100, 500, 1000, 5000, 10000]],
            ticktext=["1", "10", "100", "500", "1k", "5k", "10k"],
        ),
        hovertemplate="NACE: %{y}<br>Risico: %{x}<br>Aantal: %{text}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_STIJL,
        title=f"Meest voorkomende risico's per NACE-sector (top {top_n} sectoren)",
        xaxis_title="Risico-code",
        yaxis_title="NACE-sector",
        height=max(400, top_n * 50),
    )
    return fig


# ─── Pathologieën per NACE-sector ────────────────────────────────────────────

def plot_pathologie_per_nace(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Meest voorkomende pathologie per NACE-sector (top-n sectoren).

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    nace_kolom = "nace_omschrijving" if "nace_omschrijving" in df.columns else "nace_code"

    top_nace = df[nace_kolom].dropna().value_counts().head(top_n).index.tolist()
    top_pats = df["pathology_icd10code"].dropna().value_counts().head(5).index.tolist()
    label_map = _icd10_label_map(df)

    df_gefilterd = df[
        df[nace_kolom].isin(top_nace) & df["pathology_icd10code"].isin(top_pats)
    ].copy()
    df_gefilterd["pathologie_label"] = df_gefilterd["pathology_icd10code"].map(label_map).fillna(df_gefilterd["pathology_icd10code"])

    tellingen = (
        df_gefilterd.groupby([nace_kolom, "pathologie_label"])
        .size()
        .reset_index(name="aantal")
    )

    pivot = tellingen.pivot(index=nace_kolom, columns="pathologie_label", values="aantal").fillna(0)
    pivot.index = [str(n)[:50] + "…" if len(str(n)) > 50 else str(n) for n in pivot.index]
    pivot.columns = [str(c)[:40] + "…" if len(str(c)) > 40 else str(c) for c in pivot.columns]

    werkelijke_waarden = pivot.values.astype(int)
    # Log-schaal voor kleur zodat uitschieters de schaal niet domineren
    log_waarden = np.log1p(pivot.values)

    fig = go.Figure(go.Heatmap(
        z=log_waarden,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Greens",
        text=werkelijke_waarden,
        texttemplate="%{text}",
        showscale=True,
        colorbar=dict(
            title="Aantal (log)",
            tickvals=[np.log1p(v) for v in [1, 10, 100, 500, 1000, 5000, 10000]],
            ticktext=["1", "10", "100", "500", "1k", "5k", "10k"],
        ),
        hovertemplate="NACE: %{y}<br>Pathologie: %{x}<br>Aantal: %{text}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_STIJL,
        title=f"Meest voorkomende pathologieën per NACE-sector (top {top_n} sectoren)",
        xaxis_title="Pathologie",
        yaxis_title="NACE-sector",
        height=max(400, top_n * 50),
    )
    return fig


# ─── Risico's per functiecode ────────────────────────────────────────────────

def plot_risico_per_functiecode(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Meest voorkomende risico per functiecode.
    Let op: employment_functioncode bevat veel ontbrekende waarden.

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    df_met_functie = df[df["employment_functioncode"].notna()].copy()

    if df_met_functie.empty:
        return go.Figure().update_layout(
            title="Geen functiecode-data beschikbaar",
            annotations=[dict(text="Alle waarden zijn leeg", showarrow=False, x=0.5, y=0.5)],
        )

    top_functies = df_met_functie["employment_functioncode"].value_counts().head(top_n).index.tolist()
    top_risicos = df_met_functie["risk_code"].dropna().value_counts().head(5).index.tolist()

    df_gefilterd = df_met_functie[
        df_met_functie["employment_functioncode"].isin(top_functies)
        & df_met_functie["risk_code"].isin(top_risicos)
    ]

    tellingen = (
        df_gefilterd.groupby(["employment_functioncode", "risk_code"])
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="employment_functioncode",
        y="aantal",
        color="risk_code",
        barmode="group",
        title=f"Meest voorkomende risico's per functiecode (top {top_n})",
        labels={
            "employment_functioncode": "Functiecode",
            "aantal": "Aantal",
            "risk_code": "Risico-code",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=450)
    return fig


# ─── Pathologieën per functiecode ────────────────────────────────────────────

def plot_pathologie_per_functiecode(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Meest voorkomende pathologie per functiecode.
    Let op: employment_functioncode bevat veel ontbrekende waarden.

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    df_met_functie = df[df["employment_functioncode"].notna()].copy()

    if df_met_functie.empty:
        return go.Figure().update_layout(
            title="Geen functiecode-data beschikbaar",
            annotations=[dict(text="Alle waarden zijn leeg", showarrow=False, x=0.5, y=0.5)],
        )

    top_functies = df_met_functie["employment_functioncode"].value_counts().head(top_n).index.tolist()
    top_pats = df_met_functie["pathology_icd10code"].dropna().value_counts().head(5).index.tolist()
    label_map = _icd10_label_map(df_met_functie)

    df_gefilterd = df_met_functie[
        df_met_functie["employment_functioncode"].isin(top_functies)
        & df_met_functie["pathology_icd10code"].isin(top_pats)
    ].copy()
    df_gefilterd["pathologie_label"] = df_gefilterd["pathology_icd10code"].map(label_map).fillna(df_gefilterd["pathology_icd10code"])

    tellingen = (
        df_gefilterd.groupby(["employment_functioncode", "pathologie_label"])
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="employment_functioncode",
        y="aantal",
        color="pathologie_label",
        barmode="group",
        title=f"Meest voorkomende pathologieën per functiecode (top {top_n})",
        labels={
            "employment_functioncode": "Functiecode",
            "aantal": "Aantal",
            "pathologie_label": "Pathologie",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=450)
    return fig


# ─── Pathologieën per leeftijdsgroep ─────────────────────────────────────────

def plot_pathologie_per_leeftijdsgroep(df: pd.DataFrame, top_n: int = 5) -> go.Figure:
    """
    Top-n meest voorkomende pathologieën per leeftijdsgroep.

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    if "leeftijdsgroep" not in df.columns:
        return go.Figure().update_layout(title="Geen leeftijdsgroep-data beschikbaar")

    # Enkel geldige leeftijden (0-100)
    df_geldig = df[
        df["employee_age_start_pathology"].between(0, 100)
    ].copy()

    top_pats = df_geldig["pathology_icd10code"].dropna().value_counts().head(top_n).index.tolist()
    label_map = _icd10_label_map(df_geldig)

    df_gefilterd = df_geldig[df_geldig["pathology_icd10code"].isin(top_pats)].copy()
    df_gefilterd["pathologie_label"] = df_gefilterd["pathology_icd10code"].map(label_map).fillna(df_gefilterd["pathology_icd10code"])

    tellingen = (
        df_gefilterd.groupby(["leeftijdsgroep", "pathologie_label"], observed=True)
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="leeftijdsgroep",
        y="aantal",
        color="pathologie_label",
        barmode="group",
        title=f"Top {top_n} pathologieën per leeftijdsgroep",
        labels={
            "leeftijdsgroep": "Leeftijdsgroep",
            "aantal": "Aantal",
            "pathologie_label": "Pathologie",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=450)
    fig.update_xaxes(
        categoryorder="array",
        categoryarray=[
            "0–9", "10–19", "20–29", "30–39", "40–49",
            "50–59", "60–69", "70–79", "80–89", "90–99", "100+",
        ],
    )
    return fig


# ─── Pathologieën per leeftijdsgroep, gesplitst per geslacht ─────────────────

def plot_pathologie_per_leeftijdsgroep_per_geslacht(
    df: pd.DataFrame, top_n: int = 5
) -> go.Figure:
    """
    Top-n meest voorkomende pathologieën per leeftijdsgroep, gesplitst per geslacht.
    Toont twee grafieken naast elkaar (Man / Vrouw).

    Parameters
    ----------
    df : pd.DataFrame
    top_n : int

    Returns
    -------
    go.Figure
    """
    from plotly.subplots import make_subplots

    if "leeftijdsgroep" not in df.columns:
        return go.Figure().update_layout(title="Geen leeftijdsgroep-data beschikbaar")

    geslacht_kolom = "geslacht_label" if "geslacht_label" in df.columns else "employee_sex"

    # Enkel geldige leeftijden en bekende geslachten
    df_geldig = df[
        df["employee_age_start_pathology"].between(0, 100)
        & df[geslacht_kolom].isin(["Man", "Vrouw"])
    ].copy()

    if df_geldig.empty:
        return go.Figure().update_layout(title="Geen data beschikbaar voor Man/Vrouw filter")

    top_pats = df_geldig["pathology_icd10code"].dropna().value_counts().head(top_n).index.tolist()
    label_map = _icd10_label_map(df_geldig)

    df_geldig["pathologie_label"] = df_geldig["pathology_icd10code"].map(label_map).fillna(df_geldig["pathology_icd10code"])

    leeftijdsvolgorde = [
        "0–9", "10–19", "20–29", "30–39", "40–49",
        "50–59", "60–69", "70–79", "80–89", "90–99", "100+",
    ]
    kleuren = dict(zip(
        [label_map.get(p, p) for p in top_pats],
        KLEUR_REEKS[:top_n],
    ))

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Man", "Vrouw"],
        shared_yaxes=False,
    )

    for kolom_idx, geslacht in enumerate(["Man", "Vrouw"], start=1):
        df_g = df_geldig[
            (df_geldig[geslacht_kolom] == geslacht)
            & df_geldig["pathology_icd10code"].isin(top_pats)
        ]

        tellingen = (
            df_g.groupby(["leeftijdsgroep", "pathologie_label"], observed=True)
            .size()
            .reset_index(name="aantal")
        )
        tellingen["leeftijdsgroep"] = pd.Categorical(
            tellingen["leeftijdsgroep"], categories=leeftijdsvolgorde, ordered=True
        )
        tellingen = tellingen.sort_values("leeftijdsgroep")

        for pathologie in tellingen["pathologie_label"].unique():
            rijen = tellingen[tellingen["pathologie_label"] == pathologie]
            kleur = kleuren.get(pathologie, KLEUR_PRIMAIR)
            fig.add_trace(
                go.Bar(
                    name=pathologie,
                    x=rijen["leeftijdsgroep"].astype(str),
                    y=rijen["aantal"],
                    marker_color=kleur,
                    legendgroup=pathologie,
                    showlegend=(kolom_idx == 1),  # Legenda enkel links tonen
                    hovertemplate=f"<b>{pathologie}</b><br>Leeftijdsgroep: %{{x}}<br>Aantal: %{{y}}<extra></extra>",
                ),
                row=1, col=kolom_idx,
            )

    fig.update_layout(
        **LAYOUT_STIJL,
        title=f"Top {top_n} pathologieën per leeftijdsgroep — Man vs. Vrouw",
        barmode="group",
        height=500,
    )
    fig.update_xaxes(categoryorder="array", categoryarray=leeftijdsvolgorde)
    return fig


# ─── Seizoensgebonden pathologieën ───────────────────────────────────────────

def plot_seizoensgebonden_pathologieen(
    df: pd.DataFrame,
    drempel: float = 0.70,
    min_gevallen: int = 50,
    top_n: int = 10,
) -> go.Figure:
    """
    Zoekt pathologieën die uitsluitend (of sterk overheersend) in één seizoen voorkomen.

    Een pathologie wordt als seizoensgebonden beschouwd als:
    - Minstens `min_gevallen` totale gevallen
    - Minstens `drempel` (bv. 70%) van de gevallen valt in één seizoen

    Parameters
    ----------
    df : pd.DataFrame
    drempel : float
        Minimale fractie in één seizoen (standaard 0.70 = 70%)
    min_gevallen : int
        Minimaal aantal gevallen om mee te tellen (filtert zeldzame codes)
    top_n : int
        Maximum aantal seizoensgebonden pathologieën om te tonen

    Returns
    -------
    go.Figure
    """
    if "seizoen" not in df.columns:
        return go.Figure().update_layout(title="Geen seizoensdata beschikbaar")

    volgorde = ["Lente", "Zomer", "Herfst", "Winter"]
    label_map = _icd10_label_map(df)

    # Bereken het aantal gevallen per pathologie per seizoen
    tellingen = (
        df[df["pathology_icd10code"].notna() & df["seizoen"].notna()]
        .groupby(["pathology_icd10code", "seizoen"])
        .size()
        .reset_index(name="aantal")
    )

    # Totaal per pathologie
    totaal = tellingen.groupby("pathology_icd10code")["aantal"].sum().rename("totaal")
    tellingen = tellingen.join(totaal, on="pathology_icd10code")

    # Fractie per seizoen
    tellingen["fractie"] = tellingen["aantal"] / tellingen["totaal"]

    # Bepaal het dominante seizoen per pathologie
    idx_max = tellingen.groupby("pathology_icd10code")["fractie"].idxmax()
    dominant = tellingen.loc[idx_max, ["pathology_icd10code", "seizoen", "fractie", "totaal"]].copy()
    dominant.columns = ["pathology_icd10code", "dominant_seizoen", "max_fractie", "totaal"]

    # Filter: drempel en minimum gevallen
    seizoensgebonden = dominant[
        (dominant["max_fractie"] >= drempel) & (dominant["totaal"] >= min_gevallen)
    ].sort_values("max_fractie", ascending=False).head(top_n)

    if seizoensgebonden.empty:
        return go.Figure().update_layout(
            title=f"Geen seizoensgebonden pathologieën gevonden (drempel: {drempel:.0%}, min. {min_gevallen} gevallen)",
            annotations=[dict(text="Verlaag de drempel of het minimum aantal gevallen", showarrow=False, x=0.5, y=0.5)],
        )

    # Haal alle seizoensdata op voor de gevonden pathologieën
    codes = seizoensgebonden["pathology_icd10code"].tolist()
    df_plot = tellingen[tellingen["pathology_icd10code"].isin(codes)].copy()
    df_plot["pathologie_label"] = df_plot["pathology_icd10code"].map(label_map).fillna(df_plot["pathology_icd10code"])
    df_plot["seizoen"] = pd.Categorical(df_plot["seizoen"], categories=volgorde, ordered=True)
    df_plot = df_plot.sort_values(["pathologie_label", "seizoen"])

    fig = px.bar(
        df_plot,
        x="seizoen",
        y="aantal",
        color="pathologie_label",
        barmode="group",
        title=f"Seizoensgebonden pathologieën (≥{drempel:.0%} in één seizoen, min. {min_gevallen} gevallen)",
        labels={
            "seizoen": "Seizoen",
            "aantal": "Aantal",
            "pathologie_label": "Pathologie",
        },
        color_discrete_sequence=KLEUR_REEKS,
    )
    fig.update_layout(**LAYOUT_STIJL, height=500)
    return fig


# ─── Coronavirus (B97.2) over tijd ───────────────────────────────────────────

def plot_coronavirus_over_tijd(df: pd.DataFrame) -> go.Figure:
    """
    Lijngrafiek van het maandelijks aantal gevallen van pathologie B97.2
    (coronavirus als oorzaak van elders geclassificeerde ziekten),
    gefilterd op de periode 2018 tot heden.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    go.Figure
    """
    if "pathology_startdate" not in df.columns or "pathology_icd10code" not in df.columns:
        return go.Figure().update_layout(title="Geen datum- of pathologiedata beschikbaar")

    df_covid = df[
        (df["pathology_icd10code"] == "B97.2")
        & (df["pathology_startdate"].dt.year >= 2018)
    ].copy()

    if df_covid.empty:
        return go.Figure().update_layout(
            title="B97.2 — Coronavirus: geen gevallen gevonden vanaf 2018",
            annotations=[dict(text="Geen data", showarrow=False, x=0.5, y=0.5)],
        )

    # Groepeer per maand
    df_covid["maand"] = df_covid["pathology_startdate"].dt.to_period("M").dt.to_timestamp()
    per_maand = df_covid.groupby("maand").size().reset_index(name="aantal")
    per_maand = per_maand.sort_values("maand")

    fig = go.Figure(go.Scatter(
        x=per_maand["maand"],
        y=per_maand["aantal"],
        mode="lines+markers",
        line=dict(color=KLEUR_PRIMAIR, width=2),
        marker=dict(size=5, color=KLEUR_PRIMAIR),
        hovertemplate="Maand: %{x|%B %Y}<br>Aantal: %{y}<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_STIJL,
        title="B97.2 — Coronavirus: aantal gevallen per maand (2018–heden)",
        xaxis_title="Maand",
        yaxis_title="Aantal gevallen",
        height=450,
    )
    fig.update_xaxes(tickformat="%b %Y", tickangle=-45, dtick="M3")
    return fig
