import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from mplsoccer import VerticalPitch

# --- Column names in the CSV (adjust here if yours are different) ---
MATCH_COL = "match_id"
MINUTE_COL = "minute"
PERIOD_COL = "period"
SHOOTOUT_PERIOD = 5  # StatsBomb: period 5 = penalty shootout

# --- Over/underperformance settings ---
OVER_COLOR = "#2e7d32"     # green: goals > xG
UNDER_COLOR = "#c62828"    # red:   goals < xG
NEUTRAL_COLOR = "#9e9e9e"  # grey:  roughly in line with xG
NEUTRAL_BAND = 0.25        # |goals - xG| below this is considered "in line"

st.set_page_config(page_title="Euro 2024 Shot Map", page_icon="⚽", layout="wide")

st.title("Euro 2024 Shot Map")
st.caption("Explore every shot of UEFA Euro 2024 and compare goals with expected goals (xG).")


# ----------------------------------------------------------------------------
# Data helpers
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load the CSV once and keep only shots. Cached across interactions."""
    df = pd.read_csv(path)
    df = df[df["type"] == "Shot"].reset_index(drop=True)
    df["location"] = df["location"].apply(json.loads)
    df["shot_statsbomb_xg"] = df["shot_statsbomb_xg"].fillna(0)
    return df


@st.cache_data
def build_match_labels(df: pd.DataFrame) -> dict:
    """Map each match id to a readable label like 'Italy vs Spain'."""
    teams_per_match = df.groupby(MATCH_COL)["team"].unique()
    return {
        match_id: " vs ".join(sorted(teams))
        for match_id, teams in teams_per_match.items()
    }


def filter_data(df, team, match, player):
    if team:
        df = df[df["team"] == team]
    if match is not None:
        df = df[df[MATCH_COL] == match]
    if player:
        df = df[df["player"] == player]
    return df


def summarize_xg(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Shots, goals, xG and goals - xG for each team or player."""
    keys = ["team"] if by == "Team" else ["player", "team"]
    out = (
        df.groupby(keys)
        .agg(
            shots=("shot_statsbomb_xg", "size"),
            goals=("shot_outcome", lambda s: int((s == "Goal").sum())),
            xg=("shot_statsbomb_xg", "sum"),
        )
        .reset_index()
    )
    out["diff"] = out["goals"] - out["xg"]
    out["label"] = out["team"] if by == "Team" else out["player"] + " (" + out["team"] + ")"
    return out


def diff_color(diff: float) -> str:
    if diff > NEUTRAL_BAND:
        return OVER_COLOR
    if diff < -NEUTRAL_BAND:
        return UNDER_COLOR
    return NEUTRAL_COLOR


def verdict(diff: float) -> str:
    if diff > NEUTRAL_BAND:
        return "Overperforming 🟢"
    if diff < -NEUTRAL_BAND:
        return "Underperforming 🔴"
    return "In line ⚪"


def plot_shots(df: pd.DataFrame, ax, pitch: VerticalPitch) -> None:
    """Draw non-goals first, then goals on top (higher zorder, full opacity)."""
    is_goal = df["shot_outcome"] == "Goal"
    layers = [
        (df[~is_goal], "white", 0.5, 1),
        (df[is_goal], "green", 1.0, 2),
    ]
    for data, color, alpha, zorder in layers:
        if data.empty:
            continue
        pitch.scatter(
            data["location"].str[0].astype(float),
            data["location"].str[1].astype(float),
            ax=ax,
            s=1000 * data["shot_statsbomb_xg"],
            color=color,
            edgecolors="black",
            alpha=alpha,
            zorder=zorder,
        )


# ----------------------------------------------------------------------------
# Global filters (sidebar): apply to both tabs
# ----------------------------------------------------------------------------
df = load_data("euros_2024_shot_map.csv")
match_labels = build_match_labels(df)  # built on the full data, before any filtering

with st.sidebar:
    st.header("Filters")
    include_shootout = st.checkbox(
        "Include penalty shootouts",
        value=False,
        help="Shootout penalties are shots too, but they inflate goals and xG "
        "and aren't part of open play, so they are excluded by default.",
    )
    if not include_shootout:
        df = df[df[PERIOD_COL] != SHOOTOUT_PERIOD]

    min_minute = int(df[MINUTE_COL].min())
    max_minute = int(df[MINUTE_COL].max())
    minute_range = st.slider(
        "Minute range",
        min_value=min_minute,
        max_value=max_minute,
        value=(min_minute, max_minute),
    )

df = df[df[MINUTE_COL].between(minute_range[0], minute_range[1])]

tab_map, tab_xg = st.tabs(["Shot map", "xG vs Goals"])

# ----------------------------------------------------------------------------
# Tab 1: shot map
# ----------------------------------------------------------------------------
with tab_map:
    team = st.selectbox(
        "Select a team",
        df["team"].sort_values().unique(),
        index=None,
        placeholder="Choose a team...",
    )

    if team is None:
        st.info("Select a team to start exploring its shots.")
    else:
        team_df = df[df["team"] == team]

        match = st.selectbox(
            "Select a match (optional)",
            sorted(team_df[MATCH_COL].unique()),
            index=None,
            format_func=lambda m: match_labels[m],
            placeholder="All matches",
        )

        player_pool = team_df if match is None else team_df[team_df[MATCH_COL] == match]
        player = st.selectbox(
            "Select a player (optional)",
            player_pool["player"].sort_values().unique(),
            index=None,
            placeholder="All players",
        )

        filtered_df = filter_data(df, team, match, player)

        n_shots = len(filtered_df)
        n_goals = int((filtered_df["shot_outcome"] == "Goal").sum())
        total_xg = filtered_df["shot_statsbomb_xg"].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Shots", n_shots)
        # The delta is green when goals > xG and red when goals < xG
        col2.metric("Goals", n_goals, delta=f"{n_goals - total_xg:+.2f} vs xG")
        col3.metric("Total xG", f"{total_xg:.2f}")
        col4.metric("xG per shot", f"{total_xg / n_shots:.2f}" if n_shots else "–")

        if n_shots == 0:
            st.warning("No shots match the current filters.")

        pitch = VerticalPitch(pitch_type="statsbomb", half=True)
        fig, ax = pitch.draw(figsize=(10, 10))
        plot_shots(filtered_df, ax, pitch)

        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            "Each dot is a shot. Dot size is proportional to its expected goals (xG). "
            "Green = goal, white = other outcomes."
        )

# ----------------------------------------------------------------------------
# Tab 2: xG vs goals
# ----------------------------------------------------------------------------
with tab_xg:
    st.subheader("Who is finishing above or below expectations?")

    c1, c2, c3 = st.columns(3)
    by = c1.radio("Compare by", ["Team", "Player"], horizontal=True)
    min_shots = c2.slider("Minimum shots", 1, 30, 5 if by == "Player" else 1)
    n_show = c3.slider("Number of bars", 5, 30, 15)

    summary = summarize_xg(df, by)
    summary = summary[summary["shots"] >= min_shots]

    if summary.empty:
        st.warning("No data for the current filters. Try lowering the minimum number of shots.")
    else:
        # Keep the entries furthest from their xG (both over and under), then sort for display
        extremes = summary.loc[summary["diff"].abs().nlargest(n_show).index]
        chart_df = extremes.sort_values("diff")

        fig2, ax2 = plt.subplots(figsize=(9, max(3.0, 0.38 * len(chart_df))))
        ax2.barh(
            chart_df["label"],
            chart_df["diff"],
            color=[diff_color(d) for d in chart_df["diff"]],
        )
        ax2.axvline(0, color="black", linewidth=0.8)
        ax2.set_xlabel("Goals − xG   (positive = overperforming, negative = underperforming)")
        ax2.spines[["top", "right"]].set_visible(False)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        table = (
            summary.sort_values("diff", ascending=False)
            .assign(verdict=lambda d: d["diff"].map(verdict))
            .rename(
                columns={
                    "label": "Name",
                    "shots": "Shots",
                    "goals": "Goals",
                    "xg": "xG",
                    "diff": "Goals − xG",
                    "verdict": "Verdict",
                }
            )[["Name", "Shots", "Goals", "xG", "Goals − xG", "Verdict"]]
            .round({"xG": 2, "Goals − xG": 2})
        )
        st.dataframe(table, hide_index=True, use_container_width=True)

        st.caption(
            f"🟢 goals exceed xG by more than {NEUTRAL_BAND}, 🔴 goals fall short by more "
            f"than {NEUTRAL_BAND}, ⚪ roughly in line. Over a single tournament the sample is "
            "small, so over/underperformance is often just luck: treat it as descriptive, "
            "not as a measure of finishing skill."
        )
