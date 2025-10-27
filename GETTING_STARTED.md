# Getting Started with the College Athlete Valuation (CAV) Model

## ✅ Setup Complete!

Your College Athlete Valuation Model is fully set up and ready to use.

---

## 🎯 What This Model Does

The CAV Model estimates the value of college football players by analyzing:

1. **Performance** - On-field statistics and advanced metrics
2. **Brand/NIL** - Social media presence and marketability  
3. **Scheme Fit** - Compatibility with different coaching systems
4. **Position Value** - Strategic importance and scarcity
5. **Win Impact** - Contribution to team success (WAR)
6. **Risk Factors** - Injury history, consistency, off-field issues

### Output Example
- **Market Value**: Transfer portal dollar value estimate
- **NIL Potential**: Expected annual NIL earnings
- **Component Scores**: Detailed breakdown of strengths
- **Transfer Recommendation**: Stay vs. Transfer analysis
- **Alternative Programs**: Value at other schools with scheme fit

---

## 🚀 Quick Start (3 Commands)

### 1. Verify Setup (Already Done ✓)
```bash
python test_setup.py
```

### 2. Run Examples
```bash
python example_usage.py
```
This demonstrates:
- Single player valuation
- Comparing multiple players
- Transfer scenario analysis
- Exporting data

### 3. View Sample Data
Open these files to see the expected format:
- `data/raw/sample_players.csv`
- `data/raw/sample_transfers.csv`

---

## 💡 Your First Valuation

Create a file called `my_first_valuation.py`:

```python
from models.valuation_engine import create_valuation_engine

# Initialize
engine = create_valuation_engine()

# Define a player
player = {
    'player_id': 'QB001',
    'name': 'John Smith',
    'position': 'QB',
    'height': 75,  # inches
    'weight': 215,  # pounds
    'current_program': 'Texas',
    'eligibility_remaining': 2,
    
    # Performance stats
    'stats': {
        'completion_percentage': 67.5,
        'yards_per_attempt': 8.2,
    },
    
    # Social media
    'instagram_followers': 125000,
    'twitter_followers': 85000,
    
    # Context
    'snaps_played': 750,
    'games_played': 12,
    'team_wins': 9,
    'team_losses': 3,
}

# Calculate valuation
result = engine.calculate_comprehensive_valuation(
    player_data=player,
    current_program='Texas',
    target_programs=['Alabama', 'Georgia', 'USC']
)

# Display results
print(f"\nPlayer: {result['player_name']}")
print(f"Market Value: ${result['market_value']:,.0f}")
print(f"NIL Estimate: ${result['nil_value_estimate']['annual_expected']:,.0f}")
print(f"\nComponent Scores:")
print(f"  Performance: {result['performance_score']:.1f}")
print(f"  Brand:       {result['brand_score']:.1f}")
print(f"  Scheme Fit:  {result['scheme_fit_score']:.1f}")
print(f"\nRecommendation: {result['transfer_recommendation']['recommendation']}")
```

Run it:
```bash
python my_first_valuation.py
```

---

## 📚 Documentation Guide

### Start Here
1. **GETTING_STARTED.md** (this file) - First steps
2. **QUICKSTART.md** - 5-minute tutorial
3. **PROJECT_SETUP.md** - Complete setup overview

### Go Deeper  
4. **README.md** - Full API documentation
5. **PROJECT_OVERVIEW.md** - File-by-file guide
6. **docs/PROJECT_SUMMARY.md** - Implementation roadmap

### Reference
7. **data/schemas.py** - Data structure definitions
8. **example_usage.py** - Code examples
9. **docs/data_collection_template.txt** - Data collection guide

---

## 📊 Understanding the Output

### Component Scores (0-100 scale)
- **90-100**: Elite
- **80-89**: Excellent  
- **70-79**: Good
- **60-69**: Average
- **Below 60**: Below average

### Market Value (QB Example)
- **$800k+**: Elite, top programs competing
- **$400-800k**: Strong starter, multiple options
- **$200-400k**: Solid contributor  
- **<$200k**: Depth player

### Transfer Recommendations
- **Stay**: Current program provides best value
- **Consider Transfer**: Moderate value increase possible
- **Strong Transfer**: Significant value increase likely

---

## 🎯 Common Use Cases

### 1. Value a Single Player
```python
engine = create_valuation_engine()
result = engine.calculate_comprehensive_valuation(
    player_data=player,
    current_program='Texas'
)
```

### 2. Compare Transfer Options
```python
result = engine.calculate_comprehensive_valuation(
    player_data=player,
    current_program='Texas',
    target_programs=['Alabama', 'Georgia', 'Ohio State', 'USC']
)

for program, details in result['alternative_program_values'].items():
    print(f"{program}: ${details['total_value']:,.0f}")
```

### 3. Batch Process Multiple Players
```python
import pandas as pd

players_df = pd.read_csv('data/processed/my_players.csv')

results = []
for _, player in players_df.iterrows():
    val = engine.calculate_comprehensive_valuation(
        player_data=player.to_dict(),
        current_program=player['current_program']
    )
    results.append(val)

# Save results
pd.DataFrame(results).to_csv('outputs/reports/valuations.csv')
```

### 4. Backtest Model Accuracy
```python
from analysis.backtesting import BacktestingFramework

backtest = BacktestingFramework(engine)
results = backtest.backtest_transfers(
    historical_transfers=past_transfers,
    historical_player_data=past_players
)

metrics = backtest.calculate_accuracy_metrics(results)
print(f"Accuracy: {metrics['destination_accuracy']:.1f}%")
```

---

## 📝 Data Requirements

### Minimum Required (Model will run)
- Basic info: `player_id`, `name`, `position`, `height`, `weight`
- Performance: Position-specific stats (e.g., completion % for QB)
- Brand: At least one social media follower count
- Context: `current_program`, `games_played`

### Recommended (Better accuracy)
- Advanced metrics: PFF grade, EPA, success rate
- Multiple social platforms
- Film grades
- Injury history
- Team performance data

### Optional (Best accuracy)  
- Scheme history
- Media mentions
- Skill ratings (arm strength, speed, etc.)
- Community engagement metrics
- Known NIL deal values

---

## 🔧 Customization

### Adjust Model Weights
Edit `models/valuation_engine.py` to change component importance:
```python
# Line ~280
total_value = (
    (base_value + position_value) * fit_multiplier +
    nil_value +    # Change weight
    win_value      # Change weight
)
```

### Add New Schemes  
Edit `models/scheme_fit.py` to add coaching systems:
```python
'My New Scheme': {
    'QB': SchemeRequirements(
        scheme_name='My New Scheme',
        position='QB',
        skill_weights={'arm_strength': 9, ...}
    )
}
```

### Modify Risk Assessment
Edit `models/valuation_engine.py` risk calculation:
```python
# Line ~365
total_risk = (
    injury_risk * 0.4 +
    performance_risk * 0.4 +
    off_field_risk * 0.2
)
```

---

## 🎓 Learning Path

### Beginner (Today)
1. ✅ Run `test_setup.py` 
2. Run `python example_usage.py`
3. Review output format
4. Examine sample data files

### Intermediate (This Week)
1. Read README.md fully
2. Create valuations for real players
3. Experiment with different parameters
4. Load historical transfer data

### Advanced (This Month)
1. Run backtesting on historical data
2. Calibrate model weights
3. Customize components
4. Set up data pipeline

---

## 📈 Next Steps

### Today
- [x] Setup complete
- [x] Tests passing
- [ ] Run example_usage.py
- [ ] Review sample data

### This Week  
- [ ] Collect 10-20 real player profiles
- [ ] Calculate their valuations
- [ ] Compare model output to your intuition
- [ ] Gather historical transfer data (if available)

### This Month
- [ ] Build dataset of 50+ historical transfers
- [ ] Run backtesting
- [ ] Adjust model weights based on results
- [ ] Deploy for current season

---

## 💻 System Information

- **Python Version**: 3.13.7
- **Dependencies**: numpy, pandas (installed ✓)
- **Project Location**: `C:\Users\jones\CAV`
- **Setup Date**: October 26, 2025

---

## ⚠️ Important Reminders

1. **This is Not Financial Advice** - Use for analysis only
2. **Data Privacy** - Handle player data responsibly  
3. **Validation Required** - Always backtest before deployment
4. **Regular Updates** - Recalibrate as market evolves
5. **Complement, Don't Replace** - Use alongside traditional scouting

---

## 🆘 Need Help?

### If Something Doesn't Work
1. Check that numpy and pandas are installed: `python -c "import numpy, pandas"`
2. Verify file structure: `dir models` (should show 4 .py files)
3. Re-run setup test: `python test_setup.py`

### Common Issues

**Import Error**: Make sure you're in the CAV directory when running scripts

**Data Error**: Check that data files match format in `sample_players.csv`

**Value Seems Wrong**: Review input data - missing fields get default values

---

## 🎉 You're Ready!

Everything is set up and tested. The model is working correctly.

**Recommended first action**: Run `python example_usage.py` to see the model in action with comprehensive examples.

Happy analyzing! 🏈

---

*CAV Model v1.0 | Setup: October 26, 2025*

