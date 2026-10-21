# ⚽ Euro 2024 Shot Map & xG Explorer

An interactive Streamlit app to explore every shot taken at UEFA Euro 2024 and to check which teams and players scored **more or fewer goals than their expected goals (xG)** suggested.

**👉 [Open the live app](https://appeuros-kocttckiznjsswfm63uead.streamlit.app)**

## Features

### Shot map
- Filter by **team → match → player**
- Each shot is drawn at its exact location on the pitch (attacking half)
- **Dot size** is proportional to the shot's xG; **green** dots are goals, **white** dots are all other outcomes
- Summary metrics for the current selection: shots, goals, total xG, xG per shot, and **goals vs xG** (green delta = more goals than expected, red = fewer)

### xG vs Goals
- Compare **teams** or **players**, with a minimum-shots threshold to avoid tiny samples
- Bar chart of *goals − xG*: 🟢 overperforming, 🔴 underperforming, ⚪ roughly in line (within ±0.25)
- Sortable table with shots, goals, xG, difference and verdict

### Global filters (sidebar)
- **Minute range** (including extra time)
- **Penalty shootouts** can be included or excluded. They are excluded by default, because shootout penalties are not open play and would inflate both goals and xG

## A note on interpreting the results

Over a single tournament each team plays 4–7 matches, so the sample is small. A team or player scoring above xG is *not* necessarily a better finisher: variance, penalties and a handful of long-range goals can drive large gaps. The comparison is meant to be descriptive and to start questions, not to rank finishing skill.

## Data

Event data in StatsBomb format for Euro 2024, provided with the tutorial repository linked below (`euros_2024_shot_map.csv`). The app keeps only shot events and uses StatsBomb's xG model (`shot_statsbomb_xg`).

## Credits and what I changed

This project started from the tutorial **[Build a Soccer Analytics Web App with Streamlit](https://www.youtube.com/watch?v=M_VknDjN-wo)** by McKay Johns, whose code and data are available in [his GitHub repository](https://github.com/mckayjohns/youtube-videos/tree/main/streamlit). The tutorial builds the basic team/player shot map.

My additions:
- Fixed the goal highlighting (goals are now drawn on top at full opacity)
- Added a **match filter** and a **minute-range filter**
- Handled **penalty shootouts** explicitly (excluded by default, optional)
- Added summary metrics and the **xG vs Goals** comparison with over/underperformance colouring
- Added data caching (`st.cache_data`), a legend and a more structured layout (tabs + sidebar)

## Tech stack

Python · Streamlit · pandas · mplsoccer · matplotlib

## Run it locally

```bash
git clone https://github.com/Gabriele-Di-Stefano/streamlit_euros.git
cd streamlit_euros
pip install -r requirements.txt
streamlit run streamlit_project.py
```

Run the command from the project folder: the app reads `euros_2024_shot_map.csv` from the current directory.

## Possible next steps

- Cumulative xG timeline per match
- Shot quality by body part and play pattern
- Compare xG against opponents' defensive record
- Confidence intervals on the goals − xG difference

## Author

Gabriele Di Stefano, statistics graduate interested in football analytics.
