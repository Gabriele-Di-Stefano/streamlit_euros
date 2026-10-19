import json

import pandas as pd
import streamlit as st
from mplsoccer import VerticalPitch

# --- Column names in the CSV (adjust here if yours are different) ---
MATCH_COL = "match_id"
MINUTE_COL = "minute"
PERIOD_COL = "period"
SHOOTOUT_PERIOD = 5  # StatsBomb: period 5 = penalty shootout

st.set_page_config(page_title="Euro 2024 Shot Map", page_icon="⚽")

st.title("Euro 2024 Shot Map")
st.subheader("Filter by team, match, player and minute to explore the shots")


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


def filter_data(df, team, match, player, minute_range):
    if team:
        df = df[df["team"] == team]
    if match is not None:
        df = df[df[MATCH_COL] == match]
    if player:
        df = df[df["player"] == player]
    min_minute, max_minute = minute_range
    return df[df[MINUTE_COL].between(min_minute, max_minute)]


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


df = load_data("euros_2024_shot_map.csv")
match_labels = build_match_labels(df)  # built on the full data, before any filtering

# --- Filters ---
include_shootout = st.checkbox(
    "Include penalty shootouts",
    value=False,
    help="Shootout penalties are shots too, but they inflate goals and xG "
    "and aren't part of open play, so they are excluded by default.",
)
if not include_shootout:
    df = df[df[PERIOD_COL] != SHOOTOUT_PERIOD]

team = st.selectbox(
    "Select a team",
    df["team"].sort_values().unique(),
    index=None,
    placeholder="Choose a team...",
)

if team is None:
    st.info("Select a team to start exploring its shots.")
    st.stop()

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

min_minute = int(df[MINUTE_COL].min())
max_minute = int(df[MINUTE_COL].max())
minute_range = st.slider(
    "Minute range",
    min_value=min_minute,
    max_value=max_minute,
    value=(min_minute, max_minute),
)

filtered_df = filter_data(df, team, match, player, minute_range)

# --- Summary metrics for the current selection ---
n_shots = len(filtered_df)
n_goals = int((filtered_df["shot_outcome"] == "Goal").sum())
total_xg = filtered_df["shot_statsbomb_xg"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Shots", n_shots)
col2.metric("Goals", n_goals)
col3.metric("Total xG", f"{total_xg:.2f}")
col4.metric("xG per shot", f"{total_xg / n_shots:.2f}" if n_shots else "–")

if n_shots == 0:
    st.warning("No shots match the current filters.")

# --- Shot map ---
pitch = VerticalPitch(pitch_type="statsbomb", half=True)
fig, ax = pitch.draw(figsize=(10, 10))
plot_shots(filtered_df, ax, pitch)

st.pyplot(fig)
st.caption(
    "Each dot is a shot. Dot size is proportional to its expected goals (xG). "
    "Green = goal, white = other outcomes."
)
