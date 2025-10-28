# Six-Pillar Ensemble Valuation System

## Overview

The Ensemble Valuation System is a comprehensive, multi-model approach to college athlete market valuation. It combines six distinct analytical pillars into a unified framework that produces accurate, explainable, and actionable player valuations.

## Architecture

```
Player Market Value = f(
  Production Value,           // 30-35% weight
  Predictive Future Value,    // 25-30% weight
  Positional Scarcity,        // 15% weight
  Market Context,             // 10-15% weight
  Intangible/Brand Value,     // 10% weight
  Risk Adjustments            // Applied as multiplier
)
```

## The Six Pillars

### Pillar 1: Production Value Model
**File:** `models/pillars/pillar_1_production_value.py`

Quantifies on-field contribution using position-specific metrics.

**Football Components:**
- QB: EPA per play, completion %, TD:INT, rushing value, 3rd down, red zone
- RB: Yards after contact, success rate, receiving value, broken tackles
- WR/TE: Yards per route run, catch rate, YAC, contested catches
- OL: Pass protection, run blocking, penalties, versatility
- DL/EDGE: Pass rush efficiency, run stop rate, TFL, sacks
- LB: Tackling efficiency, coverage, run defense, blitz effectiveness
- DB: Coverage metrics, playmaking (INT/PBU), tackling

**Basketball Components:**
- Points per 100 possessions, PER, True Shooting %
- Assist/Turnover ratio, rebounding rate
- Win Shares, Box Plus/Minus
- Position-specific emphasis (PG=playmaking, C=rebounding)

**Key Features:**
- Conference strength adjustments (SEC 1.20x, FCS 0.60x)
- Competition tier weighting (P4 vs G5 vs FCS)
- Snap count / playing time weighting
- 3-year rolling average with recency bias

**Output:**
- Production score (0-100)
- Conference-adjusted weighted score
- Percentile vs position
- Component breakdown

---

### Pillar 2: Predictive Future Performance Model
**File:** `models/pillars/pillar_2_predictive_performance.py`

Forecasts expected value trajectory using age curves, statistical trends, and comparables.

**Key Inputs:**
- Age/experience curves by position and class year
  - QBs peak JR/SR year
  - RBs peak earlier (wear and tear)
  - OL longer development curve
- Year-over-year improvement rates
- Recruiting pedigree (ceiling indicator)
- Injury risk impact
- Coaching/system changes
- Roster context (playing time, supporting cast)

**Methodology:**
- Statistical trajectory analysis (trend detection)
- Age curve projections (position-specific)
- Comparable player analysis (historical matches)
- Confidence intervals (P10, P50, P90)

**Output:**
- Next year expected score
- Two-year projection
- Trajectory classification (improving/peaking/declining/stable)
- Confidence level (0-1)
- Outcome ranges

---

### Pillar 3: Positional Scarcity & Market Demand Model
**File:** `models/pillars/pillar_3_positional_scarcity.py`

Analyzes supply/demand dynamics in the transfer portal.

**Position Scarcity Tiers:**

**Football:**
- **Premium** (2.0x+ multiplier): QB, LT, EDGE, CB
- **High** (1.4-1.8x): WR, OT, DL
- **Medium** (1.1-1.3x): S, RB, TE, LB
- **Low** (0.9x): OG, C
- **Replacement** (0.6x): K, P

**Basketball:**
- **Premium** (1.7-1.8x): Elite PG, skilled C
- **High** (1.5-1.6x): 3-and-D wings, stretch bigs
- **Medium** (1.1-1.2x): SG, SF, PF

**Market Analysis:**
- Transfer portal supply count by position
- P4/high-major quality player count
- Estimated team demand (schools seeking position)
- Supply/demand ratio calculation
- Player ranking within position market

**Scarcity Multiplier Formula:**
```
Scarcity = Base Position Value × (Demand/Supply) × Quality Percentile × Timing
```

**Output:**
- Scarcity multiplier (0.6x - 2.5x)
- Position tier
- Market percentile
- Expected number of high-major offers

---

### Pillar 4: Market Context & School-Specific Adjustments
**File:** `models/pillars/pillar_4_market_context.py`

Value varies by school, conference, and market dynamics.

**Conference Multipliers:**

**Football:**
- SEC: 1.40x
- Big Ten: 1.35x
- Big 12 / ACC: 1.15x
- Pac-12: 1.05x
- G5: 0.65-0.75x
- FCS: 0.45x

**Basketball:**
- Blue bloods (Duke, UNC, Kansas, Kentucky): 1.30-1.40x
- P4 power conferences: 1.15-1.30x
- Mid-majors: 0.90-1.00x
- Low-majors: 0.50-0.65x

**School-Specific Factors:**

1. **Revenue/NIL Budget:**
   - Elite (>$150M revenue): 1.30x
   - High ($100-150M): 1.15x
   - Medium ($70-100M): 1.00x
   - Low: 0.85x or less

2. **Recent Success:**
   - Football: Playoff appearances, NY6 bowls, win %
   - Basketball: Tournament runs, Sweet 16+
   - Elite programs: 1.30x+
   - Rebuilding: 0.85x

3. **Market Size:**
   - Tier 1 (LA, NYC, Dallas): 1.25x (local NIL opportunities)
   - Tier 2 (Phoenix, Seattle): 1.15x
   - Tier 3 (mid-size): 1.05x
   - Tier 5 (rural): 0.85x

4. **Development Track Record:**
   - Known "developer" schools get 1.15x premium
   - Examples: Iowa (OL), Baylor (WR), Duke (PG)

5. **Playing Time Opportunity:**
   - Guaranteed starter: 1.10x
   - Backup/competition: 0.75-0.85x
   - Depth piece: 0.60x

**Output:**
- School-adjusted value
- Total multiplier breakdown
- Playing time probability

---

### Pillar 5: Intangible Factors & Brand Value
**File:** `models/pillars/pillar_5_brand_intangibles.py`

Off-field value drivers for NIL potential.

**Social Media Metrics:**

**Follower Tiers:**
- Mega-influencer (500K+): +40% NIL premium
- Strong brand (100-500K): +25%
- Moderate (25-100K): +10%
- Minimal (<25K): +2%

**Engagement Quality:**
- Excellent (8%+ rate): 1.30x multiplier
- Great (5-8%): 1.20x
- Good (3-5%): 1.10x
- Average: 1.00x

**Growth Rate Bonus:**
- 15%+ monthly growth: 1.20x
- 10-15%: 1.15x
- 5-10%: 1.08x

**Position Visibility Multipliers:**

**Football:**
- QB: 2.5x (highest visibility)
- RB: 1.8x
- WR: 1.7x
- EDGE: 1.4x
- OL: 0.85x (lowest visibility)

**Basketball:**
- More position-neutral (1.1-1.3x range)

**Marketability Factors:**
- Personality/charisma
- Community involvement
- Academic excellence (All-American)
- Controversy (discount)
- Regional/hometown appeal

**Output:**
- Brand score (0-100)
- NIL premium (% boost)
- Total brand value ($)
- Brand tier classification

---

### Pillar 6: Risk Adjustment Model
**File:** `models/pillars/pillar_6_risk_adjustment.py`

Comprehensive risk analysis with discounts.

**Risk Categories:**

1. **Injury Risk:**
   - Position base rates (RB: 35%, QB: 20%)
   - Personal injury history
   - Severity tiers (major: 15% discount, minor: 3%)
   - Re-injury patterns
   - Age/wear-and-tear (RB high carries)

2. **Performance Risk:**
   - Variance/consistency analysis
   - One-year wonder detection
   - Small sample size uncertainty

3. **Character/Behavior Risk:**
   - Clean record: 0% discount
   - Minor concerns: 7%
   - Moderate: 18%
   - Major: 35%
   - Severe: 60% (near Do-Not-Recruit)
   - Suspensions, arrests, locker room issues

4. **Eligibility/Availability Risk:**
   - One year remaining: 10% discount
   - Graduate transfer (1-year rental): +5%
   - Academic probation: 12%
   - NCAA investigation: 20%

5. **Fit Risk:**
   - Poor scheme fit: 12%
   - Culture concerns: 8%
   - Pace adjustment needed: 5%

**Risk Levels:**
- Minimal: <5% total discount
- Low: 5-15%
- Moderate: 15-25%
- High: 25-40%
- Severe: 40%+

**Output:**
- Total risk multiplier (0.50-1.00)
- Risk level classification
- Individual discount components
- List of risk factors

---

## Ensemble Model

**File:** `models/pillars/ensemble_valuation.py`

### Weighting Structure

**Football (Default):**
```python
Production:   35%
Predictive:   25%
Scarcity:     15%
Market:       10%
Brand:        10%
Risk:         5% (applied as multiplier)
```

**Basketball:**
```python
Production:   30%
Predictive:   25%
Scarcity:     15%
Market:       15%
Brand:        10%
Risk:         5%
```

### Player Type Adjustments

**Established Star:**
- Production: 40% (proven track record)
- Predictive: 20%

**Young Prospect:**
- Production: 25%
- Predictive: 35% (ceiling focus)

**Influencer Athlete:**
- Production: 30%
- Brand: 25% (NIL focus)

### Value Calculation Flow

```
1. Calculate Production Value (Pillar 1)
   ↓
2. Generate Predictive Projection (Pillar 2)
   ↓
3. Apply Positional Scarcity Multiplier (Pillar 3)
   ↓
4. Convert to Base Dollar Value
   ↓
5. Apply Market Context Adjustments (Pillar 4)
   ↓
6. Calculate Brand/NIL Value (Pillar 5)
   ↓
7. Apply Risk Discount (Pillar 6)
   ↓
8. Output: Player Value + NIL Potential = Total Market Value
```

### Position-Specific Dollar Conversion

**Football (Score × Multiplier):**
- QB: 15,000
- EDGE: 10,000
- LT/CB: 8,000-9,000
- WR/DL: 7,000
- RB: 5,000
- OG/C: 4,000

**Basketball:**
- PG: 8,000
- C: 7,500
- Wings: 7,000
- PF: 6,500

---

## Output & Explainability

**File:** `models/pillars/output_formatter.py`

### For Schools/Recruiters

```
PLAYER VALUATION REPORT - JOHN SMITH
================================================================================

MARKET VALUE ESTIMATE
----------------------------------------
Total Market Value:     $1,245,000
  Player Value:         $985,000
  NIL Potential:        $260,000

Confidence Range (80%): $1,050,000 - $1,440,000

VALUE DRIVERS
----------------------------------------
  ✓ Elite production (92nd percentile)
  ✓ Improving trajectory (upward trend)
  ✓ High positional scarcity (premium)
  ✓ High demand (est. 18+ offers)
  ✓ Strong brand (strong)

RISK FACTORS
----------------------------------------
  ⚠ One year of eligibility remaining

Risk Level: LOW
Risk Discount: 8.5%

RECRUITING RECOMMENDATIONS
----------------------------------------
Fair Value Range:          $1,058,000 - $1,433,000
Overpay Threshold:         >$1,619,000

Investment Assessment:
  ✓ LOW RISK - Recommended investment
```

### For Players/Agents

```
YOUR MARKET VALUE REPORT - JOHN SMITH
================================================================================

YOUR ESTIMATED MARKET VALUE
----------------------------------------
Total Opportunity Value:   $1,245,000
  NIL Earning Potential:   $260,000/year
  School Investment Value: $985,000

NEGOTIATION GUIDANCE
----------------------------------------
Suggested Opening Ask:     $1,370,000
Fair Deal Range:           $1,058,000 - $1,433,000
Walk-Away Number:          $934,000

Negotiation Tips:
  • You have strong leverage - multiple schools likely competing
  • Don't settle quickly - let market develop
  • Consider holding out for best offer
```

### JSON Export

Complete data structure for integration with dashboards, APIs, etc.

---

## Usage Examples

### Basic Usage

```python
from models.pillars import EnsembleValuationEngine, ValuationOutputFormatter

# Initialize engine
engine = EnsembleValuationEngine(sport='football')

# Prepare data
current_stats = {
    'epa_per_play': 0.35,
    'completion_pct': 68.5,
    'passing_touchdowns': 32,
    # ... more stats
}

# Calculate valuation
result = engine.calculate_valuation(
    player_name="John Smith",
    position='QB',
    class_year='JR',
    current_stats=current_stats,
    historical_stats=historical_stats,
    conference='SEC',
    school_name='Georgia',
    school_data=school_data,
    portal_data=portal_data,
    recruiting_rank=85,
    injury_history=injury_history,
    social_media=social_media
)

# Format output
print(ValuationOutputFormatter.format_for_schools(result, "John Smith"))
```

### Basketball Usage

```python
engine = EnsembleValuationEngine(sport='basketball')

result = engine.calculate_valuation(
    player_name="Mike Johnson",
    position='PG',
    class_year='JR',
    current_stats=basketball_stats,
    historical_stats=history,
    conference='Big Ten',
    school_name='Michigan State'
)
```

---

## Testing

Run the comprehensive test suite:

```bash
python test_ensemble_valuation.py
```

Tests include:
- Individual pillar tests (all 6 pillars)
- Full ensemble integration tests
- Football and basketball scenarios
- Output formatting validation

---

## Integration with Existing System

### Relationship to Current Models

**Current V4 WAR System:**
- Location: `models/valuation_engine_v4_war.py`
- Uses WAR as primary driver with $/WAR conversion

**New Ensemble System:**
- Comprehensive multi-factor approach
- More granular position-specific metrics
- Explicit scarcity, market, and brand modeling
- Full risk analysis framework
- Superior explainability

**Recommendation:**
- Use Ensemble for new valuations (more accurate, comprehensive)
- Maintain V4 for backward compatibility
- Gradually migrate to Ensemble as primary

### Database Integration

The ensemble system integrates with existing database models:
- `database/models.py` (football)
- `database/models_basketball.py` (basketball)

Pull player data, stats, social media, injuries, etc. from existing tables.

---

## Model Calibration & Validation

### Training Data Sources

1. **Known NIL Deals:**
   - On3 NIL valuations
   - Reported media deals
   - Crowdsourced customer data

2. **Transfer Portal Outcomes:**
   - Revealed preference (which players got P4 offers)
   - Bidding war reports

3. **Recruiting Market:**
   - 5-star → expected value
   - Historical correlation

### Validation Methodology

**Backtesting:**
- Hold out 20% of known deals
- Train on 80%
- Measure accuracy: RMSE, MAE, R²

**Target Accuracy:**
- Phase 1 (MVP): Within 20% of known deals
- Phase 2: Within 15%
- Phase 3 (Mature): Within 10%

**Cross-Validation:**
- Test across conferences, positions, years
- Ensure generalization

---

## Advantages Over Prior Models

1. **Explainability:** Clear breakdown of value drivers
2. **Comprehensive:** Captures all value dimensions
3. **Adaptable:** Configurable weights by player type
4. **Market-Aware:** Explicit scarcity and context modeling
5. **Risk-Adjusted:** Proper discounting for uncertainties
6. **Future-Oriented:** Predictive trajectory, not just current performance
7. **Brand Integration:** Explicit NIL potential separate from player value

---

## Future Enhancements

1. **Machine Learning Integration:**
   - XGBoost/Random Forest for trajectory prediction
   - Train on historical player outcomes

2. **Real-Time Market Data:**
   - Live transfer portal tracking
   - Dynamic supply/demand updates

3. **Comparable Player Database:**
   - Historical player trajectories
   - Similarity scoring algorithm

4. **Multi-Year Projections:**
   - 3-5 year value forecasts
   - Career arc modeling

5. **Team Fit Scoring:**
   - Specific scheme fit analysis
   - Roster construction optimization

---

## File Structure

```
models/pillars/
├── __init__.py                         # Package initialization
├── pillar_1_production_value.py        # Historical performance
├── pillar_2_predictive_performance.py  # Future projections
├── pillar_3_positional_scarcity.py     # Market supply/demand
├── pillar_4_market_context.py          # School-specific adjustments
├── pillar_5_brand_intangibles.py       # NIL/brand value
├── pillar_6_risk_adjustment.py         # Risk analysis
├── ensemble_valuation.py               # Master orchestrator
└── output_formatter.py                 # Output formatting

test_ensemble_valuation.py              # Comprehensive test suite
ENSEMBLE_VALUATION_README.md            # This file
```

---

## References

- WAR System Documentation: `WAR_SYSTEM_DOCUMENTATION.md`
- V2 Valuation Summary: `V2_VALUATION_SUMMARY.md`
- Basketball Integration: `BASKETBALL_COMPLETE.md`

---

## Support

For questions, issues, or enhancements, contact the CAV development team.

**Version:** 1.0.0
**Last Updated:** 2025-10-27
