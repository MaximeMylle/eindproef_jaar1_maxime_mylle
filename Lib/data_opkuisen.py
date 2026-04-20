"""
data_opkuisen.py
----------------
Functies voor het opkuisen, verrijken en filteren van de dataset.
"""

import pandas as pd
from datetime import date

# Risico-codes die verwijderd moeten worden uit de dataset
TE_VERWIJDEREN_RISICOS = {
    "SIG", "SIA", "SI", "SIR1", "SIR2",
    "SIG_DECL", "SIA_DECL", "SIR_DECL",
    "AUTRE", "SIR2_décl"
}

# Seizoensindeling op basis van maandnummer
def _maand_naar_seizoen(maand: int) -> str:
    """Zet een maandnummer om naar een seizoensnaam."""
    if maand in (3, 4, 5):
        return "Lente"
    elif maand in (6, 7, 8):
        return "Zomer"
    elif maand in (9, 10, 11):
        return "Herfst"
    else:
        return "Winter"


def verwijder_ongeldige_risicos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verwijdert rijen waarvan de risk_code in de lijst van ongeldige codes staat.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    masker = ~df["risk_code"].isin(TE_VERWIJDEREN_RISICOS)
    return df[masker].copy()


def verwijder_ongeldige_pathologieen(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verwijdert rijen met ongeldige pathologie-codes (bv. 999999).

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    # Strip en verwijder zowel "999999" als "999999.0" (bij numerieke inlees)
    genormaliseerd = df["pathology_icd10code"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    masker = genormaliseerd != "999999"
    return df[masker].copy()


def strip_icd10_spaties(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verwijdert leading/trailing spaties uit de pathology_icd10code kolom.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    if "pathology_icd10code" in df.columns:
        df["pathology_icd10code"] = df["pathology_icd10code"].str.strip()
    return df


def parseer_datums(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converteert datumkolommen naar het datetime-formaat.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    datumkolommen = [
        "employee_birthdate",
        "employment_startdate",
        "employment_enddate",
        "risk_startdate",
        "risk_enddate",
        "pathology_startdate",
        "pathology_enddate",
    ]
    for kolom in datumkolommen:
        if kolom in df.columns:
            df[kolom] = pd.to_datetime(df[kolom], errors="coerce")
    return df


def voeg_leeftijdsgroep_toe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Voegt een kolom 'leeftijdsgroep' toe op basis van employee_age_start_pathology.
    Groepen per 10 jaar: 0–9, 10–19, ..., 90+

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    if "employee_age_start_pathology" not in df.columns:
        return df

    grenzen = list(range(0, 101, 10)) + [float("inf")]
    labels = [f"{i}–{i+9}" for i in range(0, 100, 10)] + ["100+"]

    df["leeftijdsgroep"] = pd.cut(
        df["employee_age_start_pathology"],
        bins=grenzen,
        labels=labels,
        right=False,
        include_lowest=True,
    )
    return df


def voeg_seizoen_toe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Voegt een kolom 'seizoen' toe op basis van de maand van pathology_startdate.
    Lente (mrt–mei), Zomer (jun–aug), Herfst (sep–nov), Winter (dec–feb)

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    if "pathology_startdate" not in df.columns:
        return df

    df["seizoen"] = df["pathology_startdate"].dt.month.map(_maand_naar_seizoen)
    return df


def filter_laatste_n_jaar(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Filtert de dataset op de laatste n jaar op basis van pathology_startdate.

    Parameters
    ----------
    df : pd.DataFrame
    n : int
        Aantal jaar (standaard 5)

    Returns
    -------
    pd.DataFrame
    """
    if "pathology_startdate" not in df.columns:
        return df

    grens = pd.Timestamp.now() - pd.DateOffset(years=n)
    return df[df["pathology_startdate"] >= grens].copy()


def filter_op_periode(df: pd.DataFrame, jaar_van: int, jaar_tot: int) -> pd.DataFrame:
    """
    Filtert de dataset op een specifieke periode op basis van pathology_startdate.

    Parameters
    ----------
    df : pd.DataFrame
    jaar_van : int
        Beginjaar (inclusief)
    jaar_tot : int
        Eindjaar (exclusief)

    Returns
    -------
    pd.DataFrame
    """
    if "pathology_startdate" not in df.columns:
        return df

    return df[
        (df["pathology_startdate"].dt.year >= jaar_van)
        & (df["pathology_startdate"].dt.year < jaar_tot)
    ].copy()


def kuise_data_op(df: pd.DataFrame) -> pd.DataFrame:
    """
    Voert alle opkuisstappen uit in de juiste volgorde:
    1. Verwijder ongeldige risico-codes
    2. Strip ICD-10 spaties
    3. Parseer datums
    4. Voeg leeftijdsgroep toe
    5. Voeg seizoen toe

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame — opgekuiste en verrijkte dataset
    """
    df = verwijder_ongeldige_risicos(df)
    df = verwijder_ongeldige_pathologieen(df)
    df = strip_icd10_spaties(df)
    df = parseer_datums(df)
    df = voeg_leeftijdsgroep_toe(df)
    df = voeg_seizoen_toe(df)
    return df
