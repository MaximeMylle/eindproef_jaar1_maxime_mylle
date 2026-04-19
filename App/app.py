"""
app.py
------
Streamlit-applicatie voor de interactieve visualisatie van de medische risicoanalyse.
Start met: streamlit run app.py (vanuit de App/ map)
"""

import sys
import os

# Voeg de rootmap toe zodat Lib geïmporteerd kan worden
sys.path.insert(0, os.path.abspath('..'))

import streamlit as st
import pandas as pd

from Lib.data_laden import laad_alle_data
from Lib.data_opkuisen import kuise_data_op, filter_laatste_n_jaar
from Lib import visualisaties as vis

# ─── Paginaconfiguratie ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Medische Risicoanalyse",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Data laden (eenmalig gecached) ─────────────────────────────────────────

@st.cache_data(show_spinner="Data inlezen en opkuisen...")
def laad_data():
    """Laadt en kuist de data op. Resultaat wordt gecached."""
    data_map = os.path.join(os.path.dirname(__file__), '..', 'Data')
    df_ruw = laad_alle_data(data_map)
    df = kuise_data_op(df_ruw)
    return df


df_volledig = laad_data()

# ─── Zijbalk — filters ───────────────────────────────────────────────────────

st.sidebar.title("Filters")
st.sidebar.markdown("---")

# --- Geslacht ---
geslacht_opties = sorted(df_volledig["geslacht_label"].dropna().unique().tolist())
geslacht_keuze = st.sidebar.multiselect(
    "Geslacht",
    options=geslacht_opties,
    default=geslacht_opties,
    help="Selecteer één of meerdere geslachten",
)

# --- Jaarbereik ---
min_jaar = int(df_volledig["pathology_startdate"].dt.year.min())
max_jaar = int(df_volledig["pathology_startdate"].dt.year.max())

jaar_bereik = st.sidebar.slider(
    "Jaarbereik (pathologie-startdatum)",
    min_value=min_jaar,
    max_value=max_jaar,
    value=(max(min_jaar, max_jaar - 10), max_jaar),
    help="Filter op het jaar van de pathologie-startdatum",
)

# --- NACE-sector ---
nace_kolom = "nace_omschrijving" if "nace_omschrijving" in df_volledig.columns else "nace_code"
top_nace_opties = (
    df_volledig[nace_kolom]
    .dropna()
    .value_counts()
    .head(30)
    .index.tolist()
)
nace_keuze = st.sidebar.multiselect(
    "NACE-sector (max. 10)",
    options=top_nace_opties,
    default=[],
    max_selections=10,
    help="Laat leeg om alle sectoren te tonen",
)

# --- Leeftijdsgroep ---
leeftijdsgroep_opties = [
    "0–9", "10–19", "20–29", "30–39", "40–49",
    "50–59", "60–69", "70–79", "80–89", "90–99", "100+",
]
leeftijdsgroep_keuze = st.sidebar.multiselect(
    "Leeftijdsgroep",
    options=leeftijdsgroep_opties,
    default=[],
    help="Laat leeg om alle leeftijdsgroepen te tonen",
)

# --- Filters wissen ---
if st.sidebar.button("Filters wissen"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Eindwerk Data Science — Medische Risicoanalyse")


# ─── Filters toepassen ───────────────────────────────────────────────────────

def pas_filters_toe(df: pd.DataFrame) -> pd.DataFrame:
    """Past alle zijbalk-filters toe op de dataframe."""
    # Geslacht
    if geslacht_keuze:
        df = df[df["geslacht_label"].isin(geslacht_keuze)]

    # Jaarbereik
    df = df[
        (df["pathology_startdate"].dt.year >= jaar_bereik[0])
        & (df["pathology_startdate"].dt.year <= jaar_bereik[1])
    ]

    # NACE-sector
    if nace_keuze:
        df = df[df[nace_kolom].isin(nace_keuze)]

    # Leeftijdsgroep
    if leeftijdsgroep_keuze and "leeftijdsgroep" in df.columns:
        df = df[df["leeftijdsgroep"].astype(str).isin(leeftijdsgroep_keuze)]

    return df


df_gefilterd = pas_filters_toe(df_volledig)


# ─── Hoofdpaneel ─────────────────────────────────────────────────────────────

st.title("🏥 Medische Risicoanalyse")
st.markdown(
    "Interactief dashboard voor de analyse van risico's en pathologieën van werknemers. "
    "Gebruik de filters in de zijbalk om de selectie te verfijnen."
)

# Statistieken bovenaan
col1, col2, col3, col4 = st.columns(4)
col1.metric("Aantal records", f"{len(df_gefilterd):,}")
col2.metric("Unieke risico's", f"{df_gefilterd['risk_code'].nunique():,}")
col3.metric("Unieke pathologieën", f"{df_gefilterd['pathology_icd10code'].nunique():,}")
col4.metric("Unieke NACE-sectoren", f"{df_gefilterd['nace_code'].nunique():,}")

if len(df_gefilterd) == 0:
    st.warning("Geen data beschikbaar voor de huidige filtercombinatie. Pas de filters aan.")
    st.stop()

st.markdown("---")

# ─── Tabs ────────────────────────────────────────────────────────────────────

tab_risicos, tab_pathologieen, tab_combinaties, tab_demografie = st.tabs([
    "Risico's",
    "Pathologieën",
    "Combinaties & Seizoenen",
    "Demografie",
])


# --- Tab: Risico's ---
with tab_risicos:
    st.header("Risico's")

    st.subheader("Top 10 meest voorkomende risico's")
    st.plotly_chart(
        vis.plot_top10_risicos(df_gefilterd),
        use_container_width=True,
    )

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Risico's per NACE-sector")
        st.plotly_chart(
            vis.plot_risico_per_nace(df_gefilterd),
            use_container_width=True,
        )
    with col_r:
        st.subheader("Risico's per functiecode")
        pct_null = df_gefilterd["employment_functioncode"].isnull().mean() * 100
        if pct_null > 50:
            st.caption(f"⚠️ {pct_null:.0f}% van de rijen heeft geen functiecode. Plot is gebaseerd op beperkte data.")
        st.plotly_chart(
            vis.plot_risico_per_functiecode(df_gefilterd),
            use_container_width=True,
        )


# --- Tab: Pathologieën ---
with tab_pathologieen:
    st.header("Pathologieën")

    st.subheader("Top 10 meest voorkomende pathologieën")
    st.plotly_chart(
        vis.plot_top10_pathologieen(df_gefilterd),
        use_container_width=True,
    )

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Pathologieën per NACE-sector")
        st.plotly_chart(
            vis.plot_pathologie_per_nace(df_gefilterd),
            use_container_width=True,
        )
    with col_r:
        st.subheader("Pathologieën per functiecode")
        pct_null = df_gefilterd["employment_functioncode"].isnull().mean() * 100
        if pct_null > 50:
            st.caption(f"⚠️ {pct_null:.0f}% van de rijen heeft geen functiecode. Plot is gebaseerd op beperkte data.")
        st.plotly_chart(
            vis.plot_pathologie_per_functiecode(df_gefilterd),
            use_container_width=True,
        )


# --- Tab: Combinaties & Seizoenen ---
with tab_combinaties:
    st.header("Combinaties & Seizoenen")

    st.subheader("Top 10 meest voorkomende risico–pathologie combinaties")
    st.plotly_chart(
        vis.plot_top10_risico_pathologie_combo(df_gefilterd),
        use_container_width=True,
    )

    st.divider()

    col_seizoen_l, col_seizoen_r = st.columns([3, 1])
    with col_seizoen_l:
        st.subheader("Pathologieën per seizoen")
    with col_seizoen_r:
        top_n_seizoen = st.selectbox(
            "Aantal pathologieën",
            options=[5, 10, 20],
            index=0,
            key="top_n_seizoen",
        )
    st.plotly_chart(
        vis.plot_pathologie_per_seizoen(df_gefilterd, top_n=top_n_seizoen),
        use_container_width=True,
    )

    st.divider()

    st.subheader("Seizoensgebonden pathologieën")
    st.caption("Pathologieën waarbij ≥ 70% van de gevallen in één seizoen valt en minstens 50 gevallen.")
    st.plotly_chart(
        vis.plot_seizoensgebonden_pathologieen(df_gefilterd, drempel=0.70, min_gevallen=50, top_n=10),
        use_container_width=True,
    )


# --- Tab: Demografie ---
with tab_demografie:
    st.header("Demografie")

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Pathologieën per geslacht")
        st.plotly_chart(
            vis.plot_pathologie_per_geslacht(df_gefilterd),
            use_container_width=True,
        )
    with col_r:
        st.subheader(" ")  # Uitlijning met linker kolom

    st.divider()

    col_leeftijd_l, col_leeftijd_r = st.columns([3, 1])
    with col_leeftijd_l:
        st.subheader("Pathologieën per leeftijdsgroep")
    with col_leeftijd_r:
        top_n_leeftijd = st.selectbox(
            "Aantal pathologieën",
            options=[5, 10, 20],
            index=0,
            key="top_n_leeftijd",
        )

    st.plotly_chart(
        vis.plot_pathologie_per_leeftijdsgroep(df_gefilterd, top_n=top_n_leeftijd),
        use_container_width=True,
    )

    st.subheader("Pathologieën per leeftijdsgroep — Man vs. Vrouw")
    st.plotly_chart(
        vis.plot_pathologie_per_leeftijdsgroep_per_geslacht(df_gefilterd, top_n=top_n_leeftijd),
        use_container_width=True,
    )
