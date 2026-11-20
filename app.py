
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Indian Food Allergen Database",
    page_icon="🧬",
    layout="wide"
)

# ==========================================
# 2. FOOD INFORMATION
# ==========================================

food_details = {
    "peanut": {
        "display": "Peanut",
        "emoji": "🥜",
        "description": "Peanut allergen protein"
    },
    "chick pea": {
        "display": "Chickpea",
        "emoji": "🫘",
        "description": "Chickpea seed protein"
    },
    "sesame seeds": {
        "display": "Sesame",
        "emoji": "🌱",
        "description": "Sesame seed protein"
    },
    "lentil": {
        "display": "Lentil",
        "emoji": "🫘",
        "description": "Lentil seed protein"
    },
    "cashew": {
        "display": "Cashew",
        "emoji": "🥜",
        "description": "Cashew nut protein"
    },
    "alpha lactalbumin": {
        "display": "Milk",
        "emoji": "🥛",
        "description": "Alpha-lactalbumin-associated record"
    },
    "mustard": {
        "display": "Mustard",
        "emoji": "🌿",
        "description": "Mustard seed allergen protein"
    }
}

# Common names for matching foods
matched_food_names = {
    "pista": "Pistachio",
    "hazelnut": "Hazelnut",
    "hazel nut": "Hazelnut",
    "soya bean": "Soybean",
    "mung bean": "Mung bean",
    "pea": "Pea",
    "rapeseed": "Rapeseed",
    "flaxseed": "Flaxseed",
    "black walnut": "Black walnut",
    "castor bean": "Castor bean",
    "winter squash/gaint pumpkin": "Winter squash / giant pumpkin",
    "lupin(therapuetic application)": "Lupin",
    "chicken": "Chicken",
    "lentil": "Lentil",
    "sesame": "Sesame"
}

# ==========================================
# 3. LOAD EXCEL DATA
# ==========================================

@st.cache_data
def load_data():

   from pathlib import Path

    BASE_DIR = Path(__file__).parent

    protein = pd.read_excel(BASE_DIR / "Protein_information.xlsx")
    similarity = pd.read_excel(BASE_DIR / "Similarity_results.xlsx")
    protein.columns = (
        protein.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    similarity.columns = (
        similarity.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    similarity.rename(
        columns={"alingment_length": "alignment_length"},
        inplace=True
    )

    for col in ["identity", "e_value", "alignment_length"]:
        similarity[col] = pd.to_numeric(
            similarity[col], errors="coerce"
        )

    return protein, similarity


protein_df, similarity_df = load_data()

# ==========================================
# 4. CONNECT FOODS TO SEARCH RESULTS
# ==========================================

food_query_mapping = {
    "peanut": r"ara h 1",
    "chick pea": r"late embryogenesis abundant protein group 4",
    "sesame seeds": r"sesame",
    "lentil": r"lipid transfer protein 2 precursor",
    "cashew": r"vicilin-like protein\s*-\s*cashew",
    "alpha lactalbumin": r"milk",
    "mustard": r"mustard"
}

similarity_df["selected_food"] = None

for food, pattern in food_query_mapping.items():

    mask = similarity_df["query"].astype(str).str.contains(
        pattern,
        case=False,
        regex=True,
        na=False
    )

    similarity_df.loc[mask, "selected_food"] = food

# ==========================================
# 5. SIDEBAR
# ==========================================

st.sidebar.title("🧬 Food Explorer")

st.sidebar.write(
    "Select a food to explore its protein information "
    "and sequence similarity results."
)

food_options = list(food_details.keys())

selected_food = st.sidebar.selectbox(
    "Choose a food item:",
    food_options,
    format_func=lambda x: (
        food_details[x]["emoji"] + " " +
        food_details[x]["display"]
    )
)

st.sidebar.divider()

st.sidebar.markdown("### Database Statistics")
st.sidebar.metric("Food records", len(protein_df))
st.sidebar.metric("Similarity matches", len(similarity_df))

# ==========================================
# 6. MAIN PAGE HEADER
# ==========================================

st.title("🧬 Indian Food Allergen Database")

st.markdown(
    "### Exploring protein sequence similarity among selected foods"
)

st.write(
    "A prototype database presenting selected food-associated "
    "proteins and their sequence similarity matches."
)

st.divider()

# ==========================================
# 7. SELECTED FOOD INTRODUCTION
# ==========================================

food_display = food_details[selected_food]["display"]
food_emoji = food_details[selected_food]["emoji"]

st.header(f"{food_emoji} {food_display}")

st.caption(food_details[selected_food]["description"])

# ==========================================
# 8. PROTEIN INFORMATION
# ==========================================

st.subheader("Protein Information")

protein = protein_df[
    protein_df["food"].astype(str).str.lower().str.strip()
    == selected_food
]

if not protein.empty:

    row = protein.iloc[0]

    family = row["protein_family"]

    if pd.isna(family):
        family = "Not provided"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Protein name**")
        st.write(row["protein_name"])

        st.markdown("**Accession number**")
        st.write(row["accession_number"])

    with col2:
        st.markdown("**Protein family**")
        st.write(family)

        st.markdown("**Sequence source**")
        st.write(row["sequence_source"])

st.divider()

# ==========================================
# 9. SIMILARITY RESULTS
# ==========================================

st.subheader("🔍 Potentially Similar Proteins")

matches = similarity_df[
    similarity_df["selected_food"] == selected_food
].copy()

if not matches.empty:

    st.success(
        f"{len(matches)} sequence matches found for {food_display}."
    )

    matches["common_food"] = (
        matches["matched_food"]
        .astype(str)
        .str.strip()
        .apply(
            lambda x: matched_food_names.get(
                x.lower(), x.title()
            )
        )
    )

    display_df = matches[
        [
            "matched_protein",
            "common_food",
            "identity",
            "e_value",
            "alignment_length"
        ]
    ].copy()

    display_df.columns = [
        "Matched Protein",
        "Common Food Name",
        "Sequence Identity (%)",
        "E-value",
        "Alignment Length"
    ]

    display_df["E-value"] = display_df["E-value"].apply(
        lambda x: f"{x:.2e}" if pd.notna(x)
        else "Not reported"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 10. SEQUENCE IDENTITY GRAPH
    # ======================================

    st.subheader("📊 Sequence Identity Graph")

    plot_df = matches.sort_values(
        by="identity",
        ascending=True
    )

    labels = (
        plot_df["common_food"].astype(str)
        + " — "
        + plot_df["matched_protein"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.barh(
        labels,
        plot_df["identity"]
    )

    ax.set_xlabel("Sequence Identity (%)")
    ax.set_ylabel("Matched Protein and Food")
    ax.set_title(
        f"Sequence Similarity Results for {food_display}"
    )

    ax.set_xlim(0, 100)

    ax.bar_label(
        bars,
        fmt="%.1f%%",
        padding=4
    )

    plt.tight_layout()

    st.pyplot(fig)

    # ======================================
    # 11. SUMMARY
    # ======================================

    st.subheader("Results Summary")

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Matches",
        len(matches)
    )

    col2.metric(
        "Highest Sequence Identity",
        f"{matches['identity'].max():.1f}%"
    )

else:

    st.warning("No similarity results available.")

# ==========================================
# 12. SCIENTIFIC DISCLAIMER
# ==========================================

st.divider()

st.subheader("About This Database")

st.write(
    "The database contains seven selected food-associated "
    "protein records and their sequence similarity results "
    "obtained through individual searches against an "
    "allergen sequence database."
)

st.info(
    "Sequence similarity does not independently confirm "
    "clinical allergic cross-reactivity. Further "
    "immunological and clinical validation is necessary."
)

st.caption(
    "Indian Food Allergen Database | Small-scale prototype"
)
