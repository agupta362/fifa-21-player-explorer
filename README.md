# FIFA 21 Player Explorer

Interactive Streamlit dashboard for FIFA 21 player ratings. It looks at how overall rating and potential change with age, which countries and clubs have the highest-rated players, and which positions still have room to grow.

**Live app:** [https://fifa-21-player-explorer.streamlit.app/](https://fifa-21-player-explorer.streamlit.app/)

## Audience

Football fans and FIFA players, especially Career Mode and Ultimate Team players who want to compare ratings, find young high-potential players, and look at countries, clubs, and positions with data instead of guesses.

## Questions

1. How do overall rating and potential change with age, and at what age do players peak or stop growing?
2. Which nationalities and clubs have the highest-rated players, once small groups are excluded?
3. How do ratings and growth potential differ by position, and which positions have the most room to grow?

## Dataset

- **Source:** [FIFA 2021 Complete Player Dataset](https://www.kaggle.com/datasets/aayushmishra1512/fifa-2021-complete-player-data) by Aayush Mishra (CC0). Player ratings originally come from [fifaindex.com](https://www.fifaindex.com/).
- **File used by the app:** `dashboard_data.csv` (17,981 players).
- The raw Kaggle file was cleaned in `Deliverable2_FIFA21_Analysis.ipynb` (team names stripped, primary position, position group, growth, age group, free-agent flag, and a wonderkid flag). A small nationality lookup was merged on so each player has a FIFA confederation and region.
- These are video game ratings, not real match statistics. Club assignments are a snapshot from FIFA 21.
- Only the cleaned dashboard CSV is in this repo for deployment. The original Kaggle file is not included.

## Repository files

- `Deliverable2_FIFA21_Analysis.ipynb` — Deliverable 2 analysis notebook
- `app.py` — Streamlit dashboard
- `dashboard_data.csv` — cleaned data used by the app
- `requirements.txt` — Python packages
- `README.md` — this file

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## AI use

ChatGPT was used for help with some of the Streamlit code and debugging.
