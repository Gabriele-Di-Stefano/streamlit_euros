# ⚽ Euro 2024 Shot Map

An interactive Streamlit app to explore every shot taken at UEFA Euro 2024, by team and by player.

**👉 [Open the live app](https://appeuros-kocttckiznjsswfm63uead.streamlit.app)**

![App screenshot](screenshot.png)

## What it does

- Filter shots by **team** and then by **player**
- Visualise each shot on a pitch (attacking half) at its exact location
- **Marker size** is proportional to the shot's expected goals (xG)
- **Green** markers are goals, **white** markers are all other shots

## Data

Event data from [StatsBomb Open Data] for Euro 2024 [verify source and add the
attribution required by their terms]. The file `euros_2024_shot_map.csv` contains
one row per event, including location, player, team, outcome and StatsBomb xG.

## Tech stack

Python · Streamlit · pandas · mplsoccer · matplotlib

## Run it locally

```bash
git clone https://github.com/Gabriele-Di-Stefano/streamlit_euros.git
cd streamlit_euros
pip install -r requirements.txt
streamlit run streamlit_project.py
```

## Possible next steps

- Add match and minute filters
- Compare xG vs. actual goals per team and per player
- Add a summary table (shots, goals, total xG, xG per shot)

## Author

Gabriele Di Stefano – Statistics graduate interested in football analytics.
[LinkedIn link]
