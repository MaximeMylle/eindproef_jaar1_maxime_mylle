"""
data_laden.py
-------------
Functies voor het inlezen van alle CSV-bestanden en het samenvoegen
van de opzoektabellen (Nace, Risk, Sex) met de ruwe dataset.
"""

from pathlib import Path
import pandas as pd


def laad_ruwe_data(pad: str) -> pd.DataFrame:
    """
    Leest rawdata.csv in als een pandas DataFrame.

    Parameters
    ----------
    pad : str
        Pad naar rawdata.csv

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(
        pad,
        sep=";",
        encoding="utf-8",
        low_memory=False,
        na_values=["NULL", "null", ""],
    )
    return df


def laad_nace(pad: str) -> pd.DataFrame:
    """
    Leest Nace.csv in (geen kolomnamen in bestand, latin-1 encoding).

    Parameters
    ----------
    pad : str
        Pad naar Nace.csv

    Returns
    -------
    pd.DataFrame met kolommen: nace_code, nace_omschrijving
    """
    df = pd.read_csv(
        pad,
        sep=";",
        encoding="utf-8-sig",
        header=None,
        names=["nace_code", "nace_omschrijving"],
    )
    df["nace_code"] = df["nace_code"].str.strip()
    df["nace_omschrijving"] = df["nace_omschrijving"].str.strip()
    return df


def laad_risicos(pad: str) -> pd.DataFrame:
    """
    Leest Risk.csv in (geen kolomnamen in bestand, latin-1 encoding).

    Parameters
    ----------
    pad : str
        Pad naar Risk.csv

    Returns
    -------
    pd.DataFrame met kolommen: risk_code, risk_omschrijving
    """
    df = pd.read_csv(
        pad,
        sep=";",
        encoding="utf-8-sig",
        header=None,
        names=["risk_code", "risk_omschrijving"],
        on_bad_lines="skip",
    )
    df["risk_code"] = df["risk_code"].str.strip()
    df["risk_omschrijving"] = df["risk_omschrijving"].str.strip()
    return df


def laad_geslacht(pad: str) -> pd.DataFrame:
    """
    Leest Sex.csv in (geen kolomnamen, latin-1 encoding).
    Inhoud: 0=Indéfini, 1=Homme, 2=Femme

    Parameters
    ----------
    pad : str
        Pad naar Sex.csv

    Returns
    -------
    pd.DataFrame met kolommen: geslacht_code, geslacht_label
    """
    df = pd.read_csv(
        pad,
        sep=";",
        encoding="utf-8-sig",
        header=None,
        names=["geslacht_code", "geslacht_label"],
    )
    # Vertaal Franse labels naar het Nederlands
    vertaling = {"Indéfini": "Onbepaald", "Homme": "Man", "Femme": "Vrouw"}
    df["geslacht_label"] = df["geslacht_label"].str.strip().map(vertaling).fillna(df["geslacht_label"])
    df["geslacht_code"] = df["geslacht_code"].astype(int)
    return df


def laad_icd10(pad: str) -> pd.DataFrame:
    """
    Leest icd10.csv in (geen kolomnamen, latin-1 + BOM encoding).
    Bevat ICD-10 codes met Franstalige omschrijvingen.

    Parameters
    ----------
    pad : str
        Pad naar icd10.csv

    Returns
    -------
    pd.DataFrame met kolommen: pathology_icd10code, pathologie_omschrijving
    """
    df = pd.read_csv(
        pad,
        sep=";",
        encoding="utf-8-sig",
        header=None,
        names=["pathology_icd10code", "pathologie_omschrijving"],
        on_bad_lines="skip",
    )
    # Strip spaties en BOM-teken uit de code-kolom
    df["pathology_icd10code"] = df["pathology_icd10code"].str.strip().str.lstrip("\ufeff")
    df["pathologie_omschrijving"] = df["pathologie_omschrijving"].str.strip()
    # Verwijder rijen zonder geldige ICD-10 code
    df = df[df["pathology_icd10code"].notna() & (df["pathology_icd10code"] != "")]
    return df


def laad_alle_data(data_map: str) -> pd.DataFrame:
    """
    Laadt alle CSV-bestanden en mergt de opzoektabellen met de ruwe dataset.

    Parameters
    ----------
    data_map : str
        Pad naar de map met de CSV-bestanden (bv. '../Data')

    Returns
    -------
    pd.DataFrame — verrijkt met kolommen:
        geslacht_label, nace_omschrijving, risk_omschrijving, pathologie_omschrijving
    """
    map_pad = Path(data_map)

    # Ruwe data inlezen
    df = laad_ruwe_data(map_pad / "rawdata.csv")

    # Opzoektabellen inlezen
    df_nace = laad_nace(map_pad / "Nace.csv")
    df_risico = laad_risicos(map_pad / "Risk.csv")
    df_geslacht = laad_geslacht(map_pad / "Sex.csv")
    df_icd10 = laad_icd10(map_pad / "icd10.csv")

    # Geslacht samenvoegen
    df = df.merge(
        df_geslacht,
        left_on="employee_sex",
        right_on="geslacht_code",
        how="left",
    ).drop(columns=["geslacht_code"])

    # NACE-omschrijving samenvoegen
    df = df.merge(
        df_nace,
        on="nace_code",
        how="left",
    )

    # Risico-omschrijving samenvoegen
    df["risk_code"] = df["risk_code"].str.strip()
    df = df.merge(
        df_risico,
        on="risk_code",
        how="left",
    )

    # ICD-10 omschrijving samenvoegen
    # Strip eerst de pathology_icd10code zodat de merge correct werkt
    df["pathology_icd10code"] = df["pathology_icd10code"].str.strip()
    df = df.merge(
        df_icd10,
        on="pathology_icd10code",
        how="left",
    )

    return df
