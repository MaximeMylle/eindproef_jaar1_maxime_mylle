"""
visualisaties.py
----------------
Alle plotfuncties voor de data-analyse en de Streamlit-applicatie.
Elke functie accepteert een (gefilterde) DataFrame en retourneert een Plotly-figuur.
"""

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
    tellingen = df["pathology_icd10code"].dropna().value_counts()

    titel = "Top 10 meest voorkomende pathologieën"
    if titel_suffix:
        titel += f" ({titel_suffix})"

    return maak_top_barchart(tellingen, titel, "Aantal", "ICD-10 code", top_n=10)


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
    combo = (
        df["risk_code"].fillna("Onbekend")
        + " + "
        + df["pathology_icd10code"].fillna("Onbekend")
    )
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

    df_gefilterd = df[df["pathology_icd10code"].isin(top_pats)].copy()

    tellingen = (
        df_gefilterd.groupby([geslacht_kolom, "pathology_icd10code"])
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="pathology_icd10code",
        y="aantal",
        color=geslacht_kolom,
        barmode="group",
        title=f"Top {top_n} pathologieën per geslacht",
        labels={
            "pathology_icd10code": "ICD-10 code",
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
    df_gefilterd = df[df["pathology_icd10code"].isin(top_pats)].copy()

    volgorde = ["Lente", "Zomer", "Herfst", "Winter"]

    tellingen = (
        df_gefilterd.groupby(["seizoen", "pathology_icd10code"])
        .size()
        .reset_index(name="aantal")
    )
    tellingen["seizoen"] = pd.Categorical(tellingen["seizoen"], categories=volgorde, ordered=True)
    tellingen = tellingen.sort_values("seizoen")

    fig = px.bar(
        tellingen,
        x="seizoen",
        y="aantal",
        color="pathology_icd10code",
        barmode="group",
        title=f"Top {top_n} pathologieën per seizoen",
        labels={
            "seizoen": "Seizoen",
            "aantal": "Aantal",
            "pathology_icd10code": "ICD-10 code",
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

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Blues",
        text=pivot.values.astype(int),
        texttemplate="%{text}",
        showscale=True,
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

    df_gefilterd = df[
        df[nace_kolom].isin(top_nace) & df["pathology_icd10code"].isin(top_pats)
    ].copy()

    tellingen = (
        df_gefilterd.groupby([nace_kolom, "pathology_icd10code"])
        .size()
        .reset_index(name="aantal")
    )

    pivot = tellingen.pivot(index=nace_kolom, columns="pathology_icd10code", values="aantal").fillna(0)
    pivot.index = [str(n)[:50] + "…" if len(str(n)) > 50 else str(n) for n in pivot.index]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Greens",
        text=pivot.values.astype(int),
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        **LAYOUT_STIJL,
        title=f"Meest voorkomende pathologieën per NACE-sector (top {top_n} sectoren)",
        xaxis_title="ICD-10 code",
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

    df_gefilterd = df_met_functie[
        df_met_functie["employment_functioncode"].isin(top_functies)
        & df_met_functie["pathology_icd10code"].isin(top_pats)
    ]

    tellingen = (
        df_gefilterd.groupby(["employment_functioncode", "pathology_icd10code"])
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="employment_functioncode",
        y="aantal",
        color="pathology_icd10code",
        barmode="group",
        title=f"Meest voorkomende pathologieën per functiecode (top {top_n})",
        labels={
            "employment_functioncode": "Functiecode",
            "aantal": "Aantal",
            "pathology_icd10code": "ICD-10 code",
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
    df_gefilterd = df_geldig[df_geldig["pathology_icd10code"].isin(top_pats)]

    tellingen = (
        df_gefilterd.groupby(["leeftijdsgroep", "pathology_icd10code"], observed=True)
        .size()
        .reset_index(name="aantal")
    )

    fig = px.bar(
        tellingen,
        x="leeftijdsgroep",
        y="aantal",
        color="pathology_icd10code",
        barmode="group",
        title=f"Top {top_n} pathologieën per leeftijdsgroep",
        labels={
            "leeftijdsgroep": "Leeftijdsgroep",
            "aantal": "Aantal",
            "pathology_icd10code": "ICD-10 code",
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
