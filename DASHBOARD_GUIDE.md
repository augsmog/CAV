# Dashboard Guide

## College Athlete Valuation Dashboard

Interactive web dashboard for exploring player valuations, statistics, and transfer portal data.

## Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Features

### 📊 Overview Page
- Key metrics summary
- Player counts by position
- Transfer portal activity
- Top 10 player valuations preview

### 💰 Player Valuations
- Filter by position, team, minimum value
- Interactive valuation distribution chart
- Top N players table
- Component score breakdowns
- CSV download

### 🏫 Team Analysis
- Team-specific player breakdown
- Position distribution
- Total team value
- Top performers by position
- Value by position visualization

### 🔄 Transfer Portal
- Transfer timing analysis
- Top destination schools
- Top source schools (most departures)
- Net transfer balance
- Monthly transfer trends

### 🔍 Player Search
- Search by player name
- Detailed player cards
- Stats and valuations
- Biographical information

## Keyboard Shortcuts

- `R` - Rerun the app
- `C` - Clear cache
- `?` - Show keyboard shortcuts

## Configuration

### Cache Settings
Data is cached for 5 minutes by default. Modify `ttl` parameter in `@st.cache_data` decorators to change.

### Page Layout
Change `layout="wide"` to `layout="centered"` in `st.set_page_config()` for a narrower view.

### Custom Styling
Edit the CSS in the `st.markdown()` section at the top of `dashboard.py`.

## Data Sources

The dashboard pulls data from:
- `cav_data.db` - SQLite database (players, stats, transfers)
- `outputs/valuations/all_valuations_2023.json` - Player valuations

## Refresh Data

To update dashboard data:

```bash
# Collect new season data
python collect_data.py --year 2024

# Run new valuations
python test_model_valuations.py

# Dashboard will auto-reload on refresh
```

## Troubleshooting

### "No valuation data found"
Run: `python test_model_valuations.py`

### "No transfer data available"
Run: `python collect_data.py --year 2023 --transfers-only`

### Dashboard won't start
Check dependencies: `pip install streamlit plotly altair`

### Port already in use
```bash
streamlit run dashboard.py --server.port 8502
```

## Export Options

### Download Data
Use the "Download as CSV" button on the Player Valuations page.

### Share Dashboard
```bash
# Share on local network
streamlit run dashboard.py --server.address 0.0.0.0
```

### Deploy to Cloud
See: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app

## Tips

1. **Use filters** - Narrow down data by position, team, or value range
2. **Compare teams** - Switch between teams in Team Analysis
3. **Track transfers** - Monitor portal activity by month
4. **Search players** - Find specific player valuations quickly
5. **Download data** - Export filtered results for further analysis

## Advanced: Multi-Page Apps

Add new pages by creating files in `pages/` directory:

```
dashboard.py
pages/
    1_📊_Advanced_Analytics.py
    2_🎯_Predictions.py
    3_📈_Trends.py
```

## Performance

For large datasets (>10,000 players):
- Increase cache TTL
- Use database indexes
- Filter data before loading
- Enable query optimization

## Updates

The dashboard auto-refreshes when:
- You click "Rerun" (R key)
- Source files change (with auto-reload)
- Cache expires (5 minutes default)

---

**Quick Start**: `streamlit run dashboard.py`

