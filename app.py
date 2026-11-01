"""FIFA 21 Player Explorer. CIS 3400 Deliverable 3."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_FILE = Path(__file__).parent / "dashboard_data.csv"
POS_ORDER = ["GK", "CB", "LB", "RB", "LWB", "RWB", "CDM", "CM", "CAM", "LM", "RM", "LW", "RW", "CF", "ST"]

st.set_page_config(page_title="FIFA 21 Player Explorer", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["is_free_agent"] = df["is_free_agent"].astype(str).str.lower().eq("true")
    df["is_wonderkid"] = df["is_wonderkid"].astype(str).str.lower().eq("true")
    return df


def apply_filters(data, confederations, position_groups, nationality, age_range, overall_range, hide_free_agents, wonderkids_only):
    out = data[data["confederation"].isin(confederations) & data["position_group"].isin(position_groups)]
    out = out[out["age"].between(age_range[0], age_range[1])]
    out = out[out["overall"].between(overall_range[0], overall_range[1])]
    if nationality != "All":
        out = out[out["nationality"] == nationality]
    if hide_free_agents:
        out = out[~out["is_free_agent"]]
    if wonderkids_only:
        out = out[out["is_wonderkid"]]
    return out


df = load_data()

st.title("FIFA 21 Player Explorer")
st.write(
    "This dashboard looks at how FIFA 21 ratings change with age, which countries and clubs "
    "have the strongest players, and which positions still have room to grow."
)
st.caption("Audience: football fans and FIFA Career Mode / Ultimate Team players.")

with st.sidebar:
    st.header("Filters")
    st.caption("These filters update the numbers, charts, and player list.")
    confederations = st.multiselect(
        "Confederation",
        sorted(df["confederation"].unique()),
        default=sorted(df["confederation"].unique()),
    )
    position_groups = st.multiselect(
        "Position group",
        ["Goalkeeper", "Defender", "Midfielder", "Forward"],
        default=["Goalkeeper", "Defender", "Midfielder", "Forward"],
    )
    nationality = st.selectbox("Nationality", ["All"] + sorted(df["nationality"].unique()))
    age_range = st.slider("Age", int(df["age"].min()), int(df["age"].max()), (int(df["age"].min()), int(df["age"].max())))
    overall_range = st.slider(
        "Overall rating",
        int(df["overall"].min()),
        int(df["overall"].max()),
        (int(df["overall"].min()), int(df["overall"].max())),
    )
    hide_free_agents = st.checkbox("Hide free agents", value=True)
    wonderkids_only = st.checkbox("Wonderkids only (age 21 or under, potential 85+)", value=False)

    st.divider()
    st.caption("These two only change the country/club chart.")
    rank_by = st.radio("Rank by", ["Nationality", "Club"])
    min_default = 50 if rank_by == "Nationality" else 20
    min_players = st.slider("Minimum players in the ranking", 5, 200, min_default, key=f"min_{rank_by}")

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

if filtered.empty:
    st.warning("No players match the selected filters.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Players", f"{len(filtered):,}")
c2.metric("Average overall", f"{filtered['overall'].mean():.1f}")
c3.metric("Average potential", f"{filtered['potential'].mean():.1f}")
c4.metric("Average growth", f"{filtered['growth'].mean():.1f}")

st.subheader("Average overall and potential by age")
age_summary = (
    filtered.groupby("age")
    .agg(avg_overall=("overall", "mean"), avg_potential=("potential", "mean"), n=("player_id", "count"))
    .reset_index()
)
age_plot = age_summary[age_summary["n"] >= 15]

if len(age_plot) < 2:
    st.info("Not enough players at each age to draw this chart. Widen the age filter or turn off Wonderkids only.")
else:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(age_plot["age"], age_plot["avg_overall"], marker="o", color="#1b4965", label="Average overall")
    ax.plot(age_plot["age"], age_plot["avg_potential"], marker="o", color="#52796f", label="Average potential")
    ax.fill_between(age_plot["age"], age_plot["avg_overall"], age_plot["avg_potential"], color="#84a98c", alpha=0.25)
    ax.set_xlabel("Age")
    ax.set_ylabel("FIFA rating")
    ax.set_title("Average overall and potential by age")
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    gap = (age_plot["avg_potential"] - age_plot["avg_overall"]).abs()
    close_age = int(age_plot.loc[gap.idxmin(), "age"])
    young = age_plot.iloc[0]
    st.write(
        f"With the current filters, average overall at age {int(young['age'])} is {young['avg_overall']:.1f}. "
        f"Overall and potential are closest at age {close_age}. "
        "The shaded gap is remaining growth. It is wide for younger players and closes once players are near their ceiling. "
        "Ages with fewer than 15 players are left off so a handful of older players do not skew the line."
    )

st.subheader("Highest average overall by country or club")
group_col = "nationality" if rank_by == "Nationality" else "team"
ranked = (
    filtered.groupby(group_col)
    .agg(avg_overall=("overall", "mean"), n=("player_id", "count"))
    .query("n >= @min_players")
    .sort_values("avg_overall")
    .tail(15)
)

if ranked.empty:
    st.info("No group has enough players for this chart. Lower the minimum-players slider.")
else:
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(ranked.index.astype(str), ranked["avg_overall"], color="#2a6f97")
    for bar, (_, row) in zip(bars, ranked.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, f"{row['avg_overall']:.1f}  (n={int(row['n'])})", va="center", fontsize=8)
    noun = "nationalities" if group_col == "nationality" else "clubs"
    ax.set_xlabel("Average overall rating")
    ax.set_ylabel("")
    ax.set_title(f"Top {noun} by average overall (at least {min_players} players)")
    ax.set_xlim(ranked["avg_overall"].min() - 1, ranked["avg_overall"].max() + 3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    best_name = ranked["avg_overall"].idxmax()
    best = ranked.loc[best_name]
    st.write(
        f"{best_name} is first in this view, with an average overall of {best['avg_overall']:.1f} across {int(best['n']):,} players. "
        "The minimum-players slider keeps a very small country or club from looking like the best group just because it has two or three high ratings. "
        "A large country can have the most players without having the highest average."
    )

st.subheader("Rating and growth by position")
counts = filtered["primary_position"].value_counts()
keep = counts[counts >= 30].index
pos_df = filtered[filtered["primary_position"].isin(keep)].copy()
order = [p for p in POS_ORDER if p in set(pos_df["primary_position"])]

if not order:
    st.info("No position has at least 30 players in this filter, so this chart is hidden.")
else:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sns.boxplot(data=pos_df, x="primary_position", y="overall", order=order, color="#89c2d9", ax=axes[0])
    axes[0].set_title("Overall rating by position")
    axes[0].set_xlabel("Primary position")
    axes[0].set_ylabel("Overall rating")

    growth = pos_df.groupby("primary_position")["growth"].mean().reindex(order)
    axes[1].bar(growth.index.astype(str), growth.values, color="#84a98c")
    axes[1].set_title("Average growth by position")
    axes[1].set_xlabel("Primary position")
    axes[1].set_ylabel("Average growth (potential − overall)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    top_growth = growth.idxmax()
    st.write(
        f"In this filter, {top_growth} has the most remaining growth ({growth.max():.1f} points on average). "
        "Overall ratings overlap a lot across positions. Growth does not. "
        "Wide attackers and midfielders usually have more room left than goalkeepers and many defenders, especially under age 24. "
        "Positions with fewer than 30 players are hidden."
    )

st.subheader("Players in this filter")
st.caption("Top 50 by potential, then overall.")
table = (
    filtered.sort_values(["potential", "overall"], ascending=False)
    .head(50)[["name", "age", "overall", "potential", "growth", "primary_position", "team", "nationality", "confederation"]]
    .reset_index(drop=True)
)
st.dataframe(table, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Data: FIFA 2021 Complete Player Dataset on Kaggle (CC0), ratings from fifaindex.com. "
    "These are video game ratings from a FIFA 21 snapshot, not live match statistics. Some club assignments may be out of date."
)
