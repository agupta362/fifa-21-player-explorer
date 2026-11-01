"""FIFA 21 Player Explorer. CIS 3400 Deliverable 3."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_FILE = Path(__file__).parent / "dashboard_data.csv"
POS_ORDER = ["GK", "CB", "LB", "RB", "LWB", "RWB", "CDM", "CM", "CAM", "LM", "RM", "LW", "RW", "CF", "ST"]
POSITION_GROUPS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
LINE_OVERALL = "#1b4965"
LINE_POTENTIAL = "#2a9d8f"
BAR_COLOR = "#2a6f97"
BOX_COLOR = "#89c2d9"
GROWTH_COLOR = "#52b788"

st.set_page_config(page_title="FIFA 21 Player Explorer", page_icon="⚽", layout="wide")
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["is_free_agent"] = df["is_free_agent"].astype(str).str.lower().eq("true")
    df["is_wonderkid"] = df["is_wonderkid"].astype(str).str.lower().eq("true")
    return df


def apply_filters(
    data,
    confederations,
    position_groups,
    nationality,
    age_range,
    overall_range,
    hide_free_agents,
    wonderkids_only,
):
    out = data
    if confederations:
        out = out[out["confederation"].isin(confederations)]
    if position_groups:
        out = out[out["position_group"].isin(position_groups)]
    if nationality != "All":
        out = out[out["nationality"] == nationality]
    out = out[out["age"].between(age_range[0], age_range[1])]
    out = out[out["overall"].between(overall_range[0], overall_range[1])]
    if hide_free_agents:
        out = out[~out["is_free_agent"]]
    if wonderkids_only:
        out = out[out["is_wonderkid"]]
    return out


def show_fig(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data file {DATA_FILE.name}: {e}")
    st.stop()

st.title("⚽ FIFA 21 Player Explorer")
st.markdown(
    """
This dashboard is for **football fans** and **FIFA Career Mode / Ultimate Team** players.
Use the sidebar filters to compare ratings, find young high-potential players, and look at countries, clubs, and positions.

**Questions this app answers**
1. How do overall rating and potential change with age?
2. Which countries and clubs have the highest-rated players?
3. How do ratings and remaining growth differ by position?
"""
)

st.sidebar.header("Dashboard Filters")
st.sidebar.caption("Leave a list empty to include all values.")

confed_options = sorted(df["confederation"].unique())
confederations = st.sidebar.multiselect(
    "Confederation (leave empty to show all)",
    options=confed_options,
    default=[],
)
position_groups = st.sidebar.multiselect(
    "Position group (leave empty to show all)",
    options=POSITION_GROUPS,
    default=[],
)
nationality = st.sidebar.selectbox("Nationality", ["All"] + sorted(df["nationality"].unique()))
age_range = st.sidebar.slider(
    "Age",
    int(df["age"].min()),
    int(df["age"].max()),
    (int(df["age"].min()), int(df["age"].max())),
)
overall_range = st.sidebar.slider(
    "Overall rating",
    int(df["overall"].min()),
    int(df["overall"].max()),
    (int(df["overall"].min()), int(df["overall"].max())),
)
hide_free_agents = st.sidebar.checkbox("Hide free agents", value=True)
wonderkids_only = st.sidebar.checkbox("Wonderkids only (age ≤ 21 and potential ≥ 85)", value=False)

st.sidebar.divider()
st.sidebar.caption("These two only change the country / club chart.")
rank_by = st.sidebar.radio("Rank by", ["Nationality", "Club"], horizontal=True)
min_default = 50 if rank_by == "Nationality" else 20
min_players = st.sidebar.slider("Minimum players in the ranking", 5, 200, min_default, key=f"min_{rank_by}")

filtered = apply_filters(
    df,
    confederations,
    position_groups,
    nationality,
    age_range,
    overall_range,
    hide_free_agents,
    wonderkids_only,
)

confed_label = ", ".join(confederations) if confederations else "all confederations"
pos_label = ", ".join(position_groups) if position_groups else "all positions"
nat_label = nationality if nationality != "All" else "all nationalities"
st.caption(
    f"Showing **{len(filtered):,}** players · {nat_label} · {confed_label} · {pos_label} · "
    f"ages {age_range[0]}–{age_range[1]} · overall {overall_range[0]}–{overall_range[1]}."
)

st.subheader("📊 Summary Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Players", f"{len(filtered):,}")
if filtered.empty:
    m2.metric("Average overall", "N/A")
    m3.metric("Average potential", "N/A")
    m4.metric("Average growth", "N/A")
    st.warning("No players match the selected filters. Clear a filter or leave Confederation / Position empty to show all.")
    st.stop()

m2.metric("Average overall", f"{filtered['overall'].mean():.1f}")
m3.metric("Average potential", f"{filtered['potential'].mean():.1f}")
m4.metric("Average growth", f"{filtered['growth'].mean():.1f}")

st.subheader("📈 Visualizations")

st.markdown("#### Q1 · Average overall and potential by age")
age_summary = (
    filtered.groupby("age")
    .agg(avg_overall=("overall", "mean"), avg_potential=("potential", "mean"), n=("player_id", "count"))
    .reset_index()
)
age_plot = age_summary[age_summary["n"] >= 15]

if len(age_plot) < 2:
    st.info("Not enough players at each age to draw this chart. Widen the age range or turn off Wonderkids only.")
else:
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(age_plot["age"], age_plot["avg_overall"], marker="o", color=LINE_OVERALL, linewidth=2.2, label="Average overall")
    ax.plot(age_plot["age"], age_plot["avg_potential"], marker="o", color=LINE_POTENTIAL, linewidth=2.2, label="Average potential")
    ax.fill_between(age_plot["age"], age_plot["avg_overall"], age_plot["avg_potential"], color=LINE_POTENTIAL, alpha=0.18)
    ax.set_title("How ratings change as players get older")
    ax.set_xlabel("Age")
    ax.set_ylabel("FIFA rating")
    ax.legend(frameon=False)
    fig.tight_layout()
    show_fig(fig)

    gap = (age_plot["avg_potential"] - age_plot["avg_overall"]).abs()
    close_age = int(age_plot.loc[gap.idxmin(), "age"])
    young = age_plot.iloc[0]
    st.caption(
        f"At age {int(young['age'])}, average overall is {young['avg_overall']:.1f}. "
        f"Overall and potential are closest at age {close_age}. "
        "The shaded gap is remaining growth. Ages with fewer than 15 players are left off."
    )

left, right = st.columns(2)

with left:
    st.markdown("#### Q2 · Highest average overall")
    group_col = "nationality" if rank_by == "Nationality" else "team"
    ranked = (
        filtered.groupby(group_col)
        .agg(avg_overall=("overall", "mean"), n=("player_id", "count"))
        .query("n >= @min_players")
        .sort_values("avg_overall")
        .tail(12)
    )
    if ranked.empty:
        st.info("No group has enough players for this chart. Lower the minimum-players slider.")
    else:
        fig, ax = plt.subplots(figsize=(6.5, 5.6))
        ax.barh(ranked.index.astype(str), ranked["avg_overall"], color=BAR_COLOR, edgecolor="black", linewidth=0.4)
        for y, (_, row) in enumerate(ranked.iterrows()):
            ax.text(row["avg_overall"] + 0.08, y, f"{row['avg_overall']:.1f} (n={int(row['n'])})", va="center", fontsize=8)
        noun = "nationalities" if group_col == "nationality" else "clubs"
        ax.set_title(f"Top {noun} (min {min_players} players)")
        ax.set_xlabel("Average overall rating")
        ax.set_xlim(ranked["avg_overall"].min() - 1.2, ranked["avg_overall"].max() + 3.4)
        fig.tight_layout()
        show_fig(fig)

        best_name = ranked["avg_overall"].idxmax()
        best = ranked.loc[best_name]
        st.caption(
            f"{best_name} leads this view at {best['avg_overall']:.1f} overall "
            f"({int(best['n']):,} players). The minimum-player cutoff stops tiny groups from looking strongest."
        )

with right:
    st.markdown("#### Q3 · Rating and growth by position")
    counts = filtered["primary_position"].value_counts()
    keep = counts[counts >= 30].index
    pos_df = filtered[filtered["primary_position"].isin(keep)].copy()
    order = [p for p in POS_ORDER if p in set(pos_df["primary_position"])]
    if not order:
        st.info("No position has at least 30 players in this filter.")
    else:
        fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.6), gridspec_kw={"height_ratios": [1.15, 1]})
        sns.boxplot(data=pos_df, x="primary_position", y="overall", order=order, color=BOX_COLOR, ax=axes[0])
        axes[0].set_title("Overall rating by position")
        axes[0].set_xlabel("")
        axes[0].set_ylabel("Overall")

        growth = pos_df.groupby("primary_position")["growth"].mean().reindex(order)
        axes[1].bar(growth.index.astype(str), growth.values, color=GROWTH_COLOR, edgecolor="black", linewidth=0.4)
        axes[1].set_title("Average remaining growth")
        axes[1].set_xlabel("Primary position")
        axes[1].set_ylabel("Growth")
        fig.tight_layout()
        show_fig(fig)

        st.caption(
            f"{growth.idxmax()} has the most remaining growth ({growth.max():.1f} points). "
            "Overall is similar across positions; unused potential is not. Positions with fewer than 30 players are hidden."
        )

st.subheader("📋 Players in this filter")
st.caption("Top 50 by potential, then overall.")
table = (
    filtered.sort_values(["potential", "overall"], ascending=False)
    .head(50)[
        ["name", "age", "overall", "potential", "growth", "primary_position", "team", "nationality", "confederation"]
    ]
    .reset_index(drop=True)
)
st.dataframe(table, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Data: FIFA 2021 Complete Player Dataset on Kaggle (CC0), ratings from fifaindex.com. "
    "These are video game ratings from a FIFA 21 snapshot, not live match statistics."
)
