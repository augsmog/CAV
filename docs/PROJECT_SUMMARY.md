# College Football Player Valuation Model
## Project Summary & Implementation Guide

---

## Executive Summary

This comprehensive framework estimates the value of college football players to their current programs and in the transfer portal market. The model integrates:

- **Performance Analytics**: Position-specific metrics, advanced statistics, and WAR calculations
- **Scheme Fit Analysis**: Compatibility with different coaching systems and schemes
- **Brand/NIL Valuation**: Social media presence, marketability, and NIL earning potential
- **Market Dynamics**: Supply/demand factors, program resources, and competitive landscape
- **Risk Assessment**: Injury history, performance consistency, and off-field factors

---

## Model Architecture

### Core Components

1. **Performance Calculator** (`models/performance.py`)
   - Normalizes statistics to 0-100 scale by position
   - Applies conference and strength-of-schedule adjustments
   - Calculates consistency factors and clutch performance
   - Outputs: Performance score, component breakdowns

2. **Scheme Fit Calculator** (`models/scheme_fit.py`)
   - Matches player skills to scheme requirements
   - Evaluates physical and technical fit
   - Estimates learning curve and adaptation time
   - Outputs: Fit score, strengths, concerns, adaptation timeline

3. **Brand Valuation Calculator** (`models/brand_valuation.py`)
   - Quantifies social media presence
   - Estimates NIL earning potential
   - Accounts for market size and position premiums
   - Outputs: Brand score, NIL estimates with confidence intervals

4. **Win Impact Calculator** (`models/performance.py`)
   - Calculates Wins Above Replacement (WAR)
   - Weights by position importance
   - Adjusts for team context
   - Outputs: WAR, wins added, championship impact

5. **Valuation Engine** (`models/valuation_engine.py`)
   - Integrates all components
   - Calculates program-specific values
   - Estimates transfer market value
   - Outputs: Comprehensive valuation with recommendations

### Data Flow

```
Raw Data (CSV/JSON)
    ↓
Data Loader
    ↓
Player Profile Dictionary
    ↓
Valuation Engine
    ├→ Performance Calculator → Performance Score
    ├→ Scheme Fit Calculator → Fit Score
    ├→ Brand Calculator → NIL Estimate
    └→ Win Impact Calculator → WAR
    ↓
Risk Assessment
    ↓
Final Valuation
    ├→ Current Program Value
    ├→ Market Value
    ├→ Alternative Program Values
    └→ Transfer Recommendation
```

---

## Implementation Steps

### Phase 1: Setup and Data Collection (Week 1-2)

**1. Install and Configure**
```bash
cd /home/claude/cfb_valuation_model
pip install numpy pandas --break-system-packages
python example_usage.py  # Test installation
```

**2. Gather Historical Data**

Collect data for 50-100 past transfers (minimum recommended):
- Player statistics from their last season before transfer
- Social media metrics at time of transfer
- Actual transfer destinations and reported NIL values
- First-season performance at new school

Data sources:
- Sports-Reference.com (statistics)
- On3/247Sports (transfer portal tracking)
- Social media platforms (follower counts)
- School announcements (NIL deals when public)

**3. Format Data**

Use the data loader to create properly formatted datasets:
```python
from data.data_loader import DataLoader

loader = DataLoader()
loader.create_sample_dataset('data/raw')  # Creates templates
```

Edit the generated CSV files with your actual data.

### Phase 2: Initial Validation (Week 3-4)

**1. Run Initial Backtests**

```python
from analysis.backtesting import BacktestingFramework
from models.valuation_engine import create_valuation_engine
from data.data_loader import DataLoader

# Load data
loader = DataLoader()
players = loader.load_player_data('data/raw/players.csv')
transfers = loader.load_transfer_data('data/raw/transfers.csv')

# Run backtest
engine = create_valuation_engine()
backtest = BacktestingFramework(engine)

results = backtest.backtest_transfers(
    historical_transfers=transfers,
    historical_player_data=players,
    test_period=(date(2023, 1, 1), date(2024, 12, 31))
)

# Analyze results
metrics = backtest.calculate_accuracy_metrics(results)
```

**2. Review Accuracy Metrics**

Target benchmarks for initial model:
- **Value Prediction**: Mean Absolute % Error < 30%
- **Destination Prediction**: Accuracy > 40%
- **Performance Prediction**: MAE < 10 points

If metrics are far from targets, proceed to calibration.

### Phase 3: Model Calibration (Week 5-6)

**1. Identify Systematic Biases**

```python
weaknesses = backtest.identify_model_weaknesses(results)
print(weaknesses['systematic_biases'])
```

Common issues and fixes:
- **Over-predicting values**: Reduce NIL multipliers or position premiums
- **Under-predicting values**: Increase brand score weights
- **Poor destination accuracy**: Adjust scheme fit weights

**2. Position-Specific Analysis**

```python
position_analysis = backtest.analyze_by_position(results, players)
```

Different positions may need different weight schemes.

**3. Iterative Refinement**

Adjust weights in `models/valuation_engine.py`:
```python
# Example adjustments
total_value = (
    (base_value + position_value) * fit_multiplier * 1.1 +  # Increase by 10%
    nil_value * 0.9 +  # Decrease by 10%
    win_value +
    familiarity_bonus
)
```

Re-run backtests after each adjustment until metrics improve.

### Phase 4: Production Deployment (Week 7-8)

**1. Create Data Pipeline**

Set up automated data collection:
- Web scraping for statistics (within terms of service)
- API integrations for social media metrics
- Regular updates for current players

**2. Build User Interface** (Optional)

Create simple command-line or web interface:
```python
# Simple CLI
python value_player.py --player-id QB001 --targets "Alabama,Georgia,USC"
```

**3. Establish Update Schedule**

- Daily: Social media metrics for active portal players
- Weekly: Performance statistics during season
- Monthly: Model recalibration based on new transfers
- Annually: Major model updates and validations

---

## Usage Scenarios

### Scenario 1: Portal Entry Decision

**Question**: Should Player X enter the transfer portal?

**Process**:
1. Run comprehensive valuation
2. Compare current program value vs. market value
3. Review alternative program options
4. Consider risk factors
5. Evaluate NIL upside potential

**Output**: Transfer recommendation with confidence level

### Scenario 2: Recruiting a Transfer

**Question**: What should we offer Player Y?

**Process**:
1. Calculate player's market value
2. Assess fit with your scheme
3. Compare against your current roster
4. Evaluate positional need premium
5. Factor in competing programs

**Output**: Suggested NIL offer range and fit assessment

### Scenario 3: Portfolio Analysis

**Question**: How valuable is our roster in the portal market?

**Process**:
1. Batch process all roster players
2. Identify flight risks (high market value vs. current value)
3. Highlight undervalued players
4. Calculate total roster value

**Output**: Roster vulnerability report

---

## Interpreting Results

### Understanding Valuations

**Component Scores (0-100 scale)**

Each component contributes to overall value:

| Score Range | Performance | Brand | Scheme Fit |
|------------|-------------|-------|------------|
| 90-100 | Elite starter | National recognition | Perfect match |
| 80-89 | Strong starter | Regional star | Excellent fit |
| 70-79 | Solid starter | Solid presence | Good fit |
| 60-69 | Rotational | Modest following | Adequate fit |
| <60 | Backup | Minimal brand | Poor fit |

**Market Value Ranges**

Context-dependent, but general guidelines:

| Position | Elite | Strong | Average |
|----------|-------|--------|---------|
| QB | $800k+ | $400-800k | $150-400k |
| WR/RB | $500k+ | $250-500k | $100-250k |
| DL/LB | $400k+ | $200-400k | $80-200k |
| OL/DB | $300k+ | $150-300k | $60-150k |

**Risk Categories**

- **Low Risk** (0.9-1.0): Minimal concerns, safe evaluation
- **Average Risk** (1.0-1.15): Normal considerations
- **Elevated Risk** (1.15-1.3): Notable concerns, adjust value downward
- **High Risk** (>1.3): Significant concerns, major value discount

### Red Flags

**Performance Concerns**:
- Declining trajectory over multiple seasons
- High variance/inconsistency
- Poor performance against quality opponents
- Limited sample size (few snaps)

**Scheme Fit Issues**:
- Fit score < 60 indicates significant adaptation challenges
- Physical limitations for scheme requirements
- Complex scheme with low football IQ rating

**Brand/NIL Risks**:
- Declining social media trends
- Negative media attention
- Off-field controversies
- Limited engagement despite followers

**Market Dynamics**:
- Oversaturated position in portal
- Limited program interest
- Better alternatives available
- Academic or eligibility concerns

---

## Advanced Features

### Cross-Validation

Evaluate model stability:
```python
cv_results = backtest.cross_validate(
    all_transfers=transfers,
    player_data=players,
    n_folds=5
)
```

Consistent performance across folds indicates robust model.

### Sensitivity Analysis

Test how changes in inputs affect valuations:
```python
# Test NIL sensitivity
base_val = valuation['market_value']

# Increase Instagram followers by 50%
player_modified = player.copy()
player_modified['instagram_followers'] *= 1.5

new_val = engine.calculate_comprehensive_valuation(...)
sensitivity = (new_val['market_value'] - base_val) / base_val
```

### Cohort Analysis

Compare similar players:
```python
# Group by position and performance tier
elite_qbs = [p for p in players if p['position'] == 'QB' 
             and p['performance_score'] > 85]

for qb in elite_qbs:
    val = engine.calculate_comprehensive_valuation(qb, ...)
    # Compare valuations
```

---

## Best Practices

### Data Quality

1. **Verify Sources**: Use official statistics when possible
2. **Cross-Reference**: Confirm NIL values from multiple sources
3. **Update Regularly**: Stale data produces poor predictions
4. **Handle Missing Data**: Use reasonable defaults, flag low confidence

### Model Application

1. **Use Ranges**: Don't rely on point estimates alone
2. **Consider Context**: Unique circumstances matter
3. **Combine Methods**: Use alongside traditional scouting
4. **Track Outcomes**: Monitor predictions vs. actuals
5. **Iterate**: Continuously improve based on results

### Communication

1. **Be Transparent**: Explain model limitations
2. **Show Components**: Break down what drives value
3. **Discuss Uncertainty**: Present confidence intervals
4. **Provide Options**: Show alternative scenarios

---

## Troubleshooting

### Common Issues

**Issue**: Very high prediction errors

**Solutions**:
- Check data quality (outliers, missing values)
- Verify position-specific benchmarks are calibrated
- Review scheme fit requirements for your league
- Consider market-specific factors

**Issue**: Poor destination predictions

**Solutions**:
- Add more scheme fit data
- Include coaching relationship factors
- Weight geographic preferences more heavily
- Consider NIL market differences

**Issue**: Model seems biased

**Solutions**:
- Check for systematic over/under-prediction
- Analyze by position group
- Review historical transfer patterns
- Adjust component weights

---

## Maintenance Schedule

### Weekly (During Season)
- Update performance statistics
- Refresh social media metrics
- Monitor transfer portal activity

### Monthly
- Run validation on recent transfers
- Update market factors
- Review model accuracy
- Adjust weights if needed

### Annually
- Major model recalibration
- Add new features
- Comprehensive backtesting
- Update documentation

---

## Success Metrics

### Model Performance
- Value prediction MAE < 25%
- Destination prediction accuracy > 50%
- Performance prediction MAE < 8 points
- Consistent results across positions

### Business Impact
- Better roster retention
- Improved portal recruiting
- More efficient NIL budget allocation
- Competitive advantage in talent evaluation

---

## Next Steps

1. **Collect Initial Data**: Gather 50-100 historical transfers
2. **Run First Backtest**: Establish baseline accuracy
3. **Calibrate Model**: Adjust weights based on results
4. **Validate**: Test on holdout data
5. **Deploy**: Use for current season portal activity
6. **Monitor**: Track real outcomes vs. predictions
7. **Improve**: Iterate based on results

---

## Resources

### Key Files
- `README.md` - Full documentation
- `example_usage.py` - Code examples
- `data/schemas.py` - Data structures
- `models/valuation_engine.py` - Main valuation logic

### External Resources
- On3 NIL Valuations: https://www.on3.com/nil/
- Transfer Portal Tracker: https://247sports.com/
- PFF College: https://www.pff.com/college
- Sports Reference: https://www.sports-reference.com/

---

**Model Version**: 1.0  
**Last Updated**: October 2025  
**Framework**: Python 3.8+  
**Dependencies**: NumPy, Pandas
