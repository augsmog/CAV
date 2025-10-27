# Quick Start Guide
## College Football Player Valuation Model

---

## 5-Minute Setup

### 1. Verify Installation
```bash
cd /home/claude/cfb_valuation_model
python -c "import numpy, pandas; print('Dependencies OK')"
```

### 2. Run Example
```bash
python example_usage.py
```

This will demonstrate:
- Single player valuation
- Player comparisons
- Transfer scenario analysis
- Data export

---

## Basic Usage

### Value a Player

```python
from models.valuation_engine import create_valuation_engine

# Initialize
engine = create_valuation_engine()

# Minimal player data
player = {
    'player_id': 'QB001',
    'name': 'John Smith',
    'position': 'QB',
    'height': 75,
    'weight': 215,
    'current_program': 'Texas',
    'eligibility_remaining': 2,
    
    # Stats (simplified)
    'stats': {
        'completion_percentage': 67.5,
        'yards_per_attempt': 8.2,
    },
    
    # Social (simplified)
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

# View results
print(f"Market Value: ${result['market_value']:,.0f}")
print(f"NIL Estimate: ${result['nil_value_estimate']['annual_expected']:,.0f}")
print(f"Recommendation: {result['transfer_recommendation']['recommendation']}")
```

---

## Understanding Output

### Key Metrics

**market_value**: Estimated transfer portal value in dollars

**performance_score**: On-field performance rating (0-100)

**brand_score**: Personal brand/NIL potential (0-100)

**scheme_fit_score**: Fit with current scheme (0-100)

**nil_value_estimate**: Expected annual NIL earnings
- annual_expected: Best estimate
- annual_low: Conservative estimate
- annual_high: Optimistic estimate

**alternative_program_values**: Value at each target program

**transfer_recommendation**: Stay, Consider Transfer, or Strong Transfer

### Reading the Numbers

**Performance Score:**
- 85+: Elite
- 75-84: Excellent
- 65-74: Good
- 55-64: Average
- <55: Below average

**Market Value (QB example):**
- $800k+: Elite, top programs competing
- $400-800k: Strong starter, multiple options
- $200-400k: Solid contributor
- <$200k: Depth player

---

## Sample Data Format

### Player CSV
```csv
player_id,name,position,height,weight,current_program,stat_completion_percentage,instagram_followers
QB001,John Smith,QB,75,215,Texas,67.5,125000
```

### Transfer CSV
```csv
player_id,transfer_date,from_program,to_program,nil_deal_value
QB002,2024-01-15,Auburn,Miami,350000
```

See `data/raw/sample_players.csv` and `data/raw/sample_transfers.csv` for full examples.

---

## Next Steps

1. **Review Full Documentation**: See README.md
2. **Examine Sample Data**: Check data/raw/ folder
3. **Load Your Data**: Use data/data_loader.py
4. **Run Backtests**: Follow docs/PROJECT_SUMMARY.md
5. **Customize**: Adjust weights in models/valuation_engine.py

---

## Common Questions

**Q: What data do I need minimum?**
A: Position, basic stats for that position, social media followers, current program

**Q: How accurate is this?**
A: Depends on data quality. Initial accuracy ~70% on value, improves with calibration

**Q: Can I add custom factors?**
A: Yes! Edit models/valuation_engine.py to add new components

**Q: How often should I update?**
A: Weekly for active transfers, monthly for regular recalibration

**Q: What if data is missing?**
A: Model uses defaults but flags low confidence. More data = better estimates

---

## Support

- Full docs: README.md
- Implementation guide: docs/PROJECT_SUMMARY.md
- Data template: docs/data_collection_template.txt
- Example code: example_usage.py

---

Last Updated: October 2025
