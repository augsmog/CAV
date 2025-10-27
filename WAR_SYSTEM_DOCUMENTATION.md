# College Football WAR (Wins Above Replacement) System

## Overview

The WAR system is the **primary valuation metric** for college football players in this model. It measures the number of wins a player contributes to their team above what a replacement-level player would provide.

## Key Formula

```
WAR = (Performance Above Replacement / 100) × 
      Participation Factor × 
      Position Impact × 
      Leverage Index × 
      Opponent Quality × 
      Conference Multiplier ×
      Team Adjustment
```

##  Components

### 1. Replacement Level Benchmarks (40th percentile)
- **QB**: 45 (highest bar)
- **WR/CB**: 42
- **RB**: 43
- **DL**: 41
- **LB/S**: 40-41

Players below these thresholds have negative WAR (below replacement level).

### 2. Position Win Impact Multipliers
Research-based multipliers reflecting each position's influence on game outcomes:
- **QB**: 4.0x (accounts for ~40% of team wins)
- **OL**: 2.5x (collective line impact)
- **DL**: 2.3x (pass rush critical)
- **CB**: 2.0x (coverage critical)
- **WR**: 1.5x (playmakers)
- **LB**: 1.4x
- **S**: 1.3x
- **TE**: 1.2x
- **RB**: 1.0x (most replaceable)

### 3. Leverage Index (0.3x to 2.0x)
Adjusts performance based on game context:

#### High Leverage (1.5x - 2.0x):
- Close games (score differential ≤ 7)
- 4th quarter with game on the line
- Critical downs (3rd/4th down)
- Red zone situations
- Rivalry games

#### Low Leverage (0.3x - 0.5x):
- Blowouts (score differential ≥ 28)
- Garbage time
- Game already decided

**Impact**: A backup QB with 50 attempts in blowouts gets 0.3x weight, while a starter with 50 attempts in close games gets 2.0x weight. This solves the "backup QB overvaluation" problem.

### 4. Opponent Quality Adjustment (0.7x - 1.3x)
- **Elite opponents** (0.800+ win%): 1.25x
- **Average opponents** (0.500 win%): 1.00x
- **Weak opponents** (0.200 win%): 0.75x
- **Conference strength** adds 0-20% bonus (SEC/Big Ten highest)

### 5. Participation Factor
Combines snap share and starter rate:
```
Participation = Snap Share × (0.7 + 0.3 × Starter Rate)
```

Expected snaps by position (for full-time starter):
- QB/OL: 850 snaps
- CB: 750 snaps
- LB: 650 snaps
- DL: 550 snaps
- RB: 500 snaps

### 6. Team Context Adjustment
Players on better teams have slightly inflated stats due to supporting cast:
```
Team Adjustment = 1.0 - (Team Win % - 0.5) × 0.15
```

## WAR to Dollar Value Conversion

Each position has a different $/WAR value based on market realities:

| Position | $/WAR | Elite Player (2.0 WAR) Value |
|----------|-------|------------------------------|
| QB | $1,500,000 | $3,000,000 |
| OL | $900,000 | $1,800,000 |
| DL | $900,000 | $1,800,000 |
| CB | $800,000 | $1,600,000 |
| WR | $700,000 | $1,400,000 |
| LB | $650,000 | $1,300,000 |
| S | $600,000 | $1,200,000 |
| TE | $600,000 | $1,200,000 |
| RB | $500,000 | $1,000,000 |

**Player Value Formula:**
```
Player Value = WAR × $/WAR × Scheme Fit Multiplier × Risk Adjustment
```

## WAR Tiers

| WAR Range | Tier | Description |
|-----------|------|-------------|
| ≥ 2.0 | Elite/All-American | Heisman contenders, game-changers |
| 1.0 - 2.0 | All-Conference | Elite starters, impact players |
| 0.5 - 1.0 | Above Average Starter | Solid contributors |
| 0.0 - 0.5 | Average Starter | Meets expectations |
| -0.5 - 0.0 | Below Average/Backup | Below replacement level |
| < -0.5 | Replacement Level | Detrimental to team |

## Confidence Intervals

WAR uncertainty based on sample size:
- **Full starter** (≥ expected snaps): ±15%
- **Part-time starter** (≥ 50% snaps): ±30%
- **Backup/limited action** (< 50% snaps): ±50%

## Real-World Examples (2023 Season)

### Elite QB - Bo Nix (Oregon)
- **Performance Score**: 90 (elite)
- **Snaps**: 850 (full season starter)
- **Games Started**: 12/12
- **Opponent Quality**: 0.550 (above average)
- **Conference**: Pac-12 (1.10x)
- **WAR**: 1.609
- **Player Value**: $2.65M
- **Tier**: All-Conference

### Backup QB - Limited Action
- **Performance Score**: 65 (average)
- **Snaps**: 150 (backup role)
- **Games Started**: 1/8
- **Leverage**: 0.80x (likely garbage time)
- **WAR**: 0.083
- **Player Value**: $125K
- **Confidence**: ±50% (limited sample)

## Advantages Over Traditional Metrics

1. **Context-Aware**: Garbage time stats properly discounted
2. **Position-Adjusted**: QB impact vs RB impact properly weighted
3. **Sample Size**: Confidence intervals for limited data
4. **Market-Aligned**: Dollar values reflect actual transfer portal economics
5. **Opponent-Adjusted**: Performance vs weak opponents discounted

## Integration with Valuation Model

The complete player valuation consists of:

1. **Player Value** (WAR-driven)
   - What schools/collectives pay
   - Based on on-field wins contributed
   - Adjusted for scheme fit

2. **NIL Potential** (Brand-driven, separate)
   - What player earns through marketing
   - Social media following
   - Market exposure

3. **Combined Value**
   - Total annual opportunity
   - Player Value + NIL Potential

## Future Enhancements

1. **Play-by-Play Data**: True EPA (Expected Points Added) calculations
2. **Game-by-Game Context**: Actual leverage for each play
3. **Opponent-Specific Adjustments**: Performance vs ranked teams
4. **Position-Specific Metrics**: Expand beyond QB to all positions
5. **Historical Baselines**: Multi-year replacement level calculations

## Technical Implementation

- **Calculator**: `models/cfb_war_calculator.py`
- **Valuation Engine**: `models/valuation_engine_v4_war.py`
- **Test Suite**: `test_war_calculator.py`, `test_model_valuations_v4_war.py`

## Conclusion

The WAR system transforms player valuation from subjective assessments to objective, data-driven analysis. By properly weighting game context, opponent quality, and position impact, it provides a realistic measure of player value that aligns with transfer portal market dynamics.

**Key Insight**: A 2.0 WAR QB (elite) is worth $3M because they literally add 2 wins to a team's season, which translates to better recruiting, bowl revenue, playoff opportunities, and program prestige.

