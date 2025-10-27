# College Athlete Valuation (CAV) Model

A comprehensive, data-driven framework for valuing college football players using **Wins Above Replacement (WAR)** methodology. This system provides objective, context-aware valuations that align with transfer portal market dynamics.

## 🎯 What This Does

Calculates player value based on:
- **WAR (Wins Above Replacement)** - Primary metric measuring wins contributed
- **Game Context** - High-leverage situations weighted 6.7x more than garbage time
- **Opponent Quality** - Performance vs Top 10 teams weighted higher than vs FCS
- **Position Impact** - QB impact 4x more valuable than RB
- **Sample Size Confidence** - Error bars for limited playing time

## 🏆 Key Features

### V4 WAR-Driven Valuation System
- **Elite QB (1.6 WAR)** → $2.65M player value
- **Backup QB (0.08 WAR)** → $125K (garbage time properly discounted)
- **Clear interpretation**: "This player adds X wins to your team"

### Comprehensive Data Collection
- 2,656+ players valued (2023 season)
- 2,925+ players (2022 season)
- API integration with collegefootballdata.com
- Transfer portal tracking
- Team rosters and statistics

### Interactive Dashboard
- Transfermarkt-style market intelligence platform
- Player database with season segmentation
- Team rankings and roster valuations
- Transfer portal analysis
- Detailed player profiles with WAR metrics

## 📊 Results - 2023 Season

| Player | Team | WAR | Player Value | Wins Added |
|--------|------|-----|--------------|------------|
| Bo Nix | Oregon | 1.609 | $2.65M | +1.6 wins |
| Carson Beck | Georgia | 1.609 | $2.65M | +1.6 wins |
| Dillon Gabriel | Oklahoma | 1.574 | $2.60M | +1.6 wins |
| Caleb Williams | USC | 1.539 | $2.54M | +1.5 wins |

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/augsmog/CAV.git
cd CAV
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API key:
```bash
# Copy template
copy config\config.template.yaml config\config.yaml

# Edit config\config.yaml and add your API key from collegefootballdata.com
```

4. Initialize database:
```bash
python collect_data.py --init-db
```

5. Collect data:
```bash
# Collect 2023 season data
python collect_data.py --year 2023

# Run valuations
python test_model_valuations_v4_war.py
```

6. Launch dashboard:
```bash
python -m streamlit run dashboard.py
```

Navigate to `http://localhost:8501`

## 📁 Project Structure

```
CAV/
├── models/                          # Valuation engines
│   ├── cfb_war_calculator.py       # WAR calculation engine (V4)
│   ├── valuation_engine_v4_war.py  # Dollar value conversion
│   ├── performance.py              # Performance scoring
│   ├── scheme_fit.py               # Scheme fit analysis
│   └── brand_valuation.py          # NIL potential
│
├── database/                        # Data storage
│   └── models.py                   # SQLAlchemy ORM models
│
├── scrapers/                        # Data collection
│   ├── cfb_api_client.py          # CollegeFootballData API
│   └── enhanced_social_scraper.py # Social media data
│
├── etl/                            # Data pipeline
│   ├── data_pipeline.py           # Main orchestrator
│   ├── transformers.py            # Data transformation
│   └── stats_aggregator.py        # Stat aggregation
│
├── outputs/                        # Generated files
│   └── valuations/
│       ├── all_valuations_2023.json
│       └── all_valuations_2022.json
│
├── dashboard.py                    # Streamlit dashboard
├── data_adapter.py                 # Database to model adapter
├── collect_data.py                 # Data collection CLI
└── test_model_valuations_v4_war.py # Full season valuation
```

## 🧮 How WAR Works

### Core Formula
```
WAR = (Performance Above Replacement / 100) × 
      Participation Factor × 
      Position Impact (4.0 for QB, 1.0 for RB) ×
      Leverage Index (0.3x garbage time, 2.0x clutch) ×
      Opponent Quality (0.7x - 1.3x) ×
      Conference Multiplier (SEC 1.20x, Big Ten 1.15x) ×
      Team Adjustment
```

### Dollar Value Conversion
```
Player Value = WAR × $/WAR (position-specific) × Scheme Fit × Risk Adjustment
```

**QB**: $1.5M per WAR → Elite QB (2.0 WAR) = $3M  
**DL**: $900K per WAR → Elite DL (1.5 WAR) = $1.35M  
**RB**: $500K per WAR → Elite RB (0.8 WAR) = $400K

### WAR Tiers
- **≥2.0**: Elite/All-American
- **1.0-2.0**: All-Conference
- **0.5-1.0**: Above Average Starter
- **0.0-0.5**: Average Starter
- **<0.0**: Below Replacement

## 📈 Key Innovations

### 1. Leverage Index - Solves Garbage Time Problem
```python
Close game, 4th quarter, 3rd down, rivalry: 2.0x
Blowout (35-0), mid-3rd quarter: 0.3x
```
**Impact**: Backup QB's 100 yards in blowout → 30 yards equivalent

### 2. Opponent Quality Adjustment
```python
vs Top 10 team: 1.25x
vs Average (0.500 win%): 1.00x
vs FCS team: 0.75x
```

### 3. Sample Size Confidence
```python
Full starter (850+ snaps): ±15% confidence
Part-time (425+ snaps): ±30%
Backup (<425 snaps): ±50%
```

## 🎮 Dashboard Features

### Market Overview
- Total market value across all teams
- Top valued players by position
- Transfer portal activity
- Market trends

### Player Database
- Searchable/filterable player list
- Season-by-season segmentation
- WAR rankings
- Detailed player profiles with:
  - WAR breakdown
  - Leverage index
  - Opponent quality
  - Confidence intervals
  - Value components

### Team Rankings
- Roster valuations
- Average player WAR
- Depth analysis
- Competitive positioning

### Transfer Portal
- Players in portal
- Destination analysis
- Value opportunities
- Fit recommendations

## 📚 Documentation

- **[WAR System Documentation](WAR_SYSTEM_DOCUMENTATION.md)** - Complete technical reference
- **[V4 Improvements Summary](V4_WAR_IMPROVEMENTS_SUMMARY.md)** - What changed in V4
- **[Project Setup](PROJECT_SETUP.md)** - Detailed setup guide
- **[Data Ingestion Guide](DATA_INGESTION_GUIDE.md)** - Data collection documentation

## 🔑 API Key Setup

1. Get free API key from [collegefootballdata.com](https://collegefootballdata.com)
2. Add to `config/config.yaml`:
```yaml
collegefootballdata:
  api_key: "YOUR_API_KEY_HERE"
```

## 🧪 Testing

```bash
# Run V4 WAR valuations on all players
python test_model_valuations_v4_war.py

# Results saved to:
# - outputs/valuations/all_valuations_2023.json
# - outputs/valuations/all_valuations_2022.json
```

## 🎯 Use Cases

### 1. Transfer Portal Strategy
"This QB is worth 1.5 WAR. Your current QB is 0.5 WAR. Upgrading adds 1.0 win = $1.5M value"

### 2. Recruiting ROI
"5-star QB recruit projected 1.8 WAR as freshman = $2.7M value vs scholarship cost"

### 3. Roster Construction
"We have $10M in booster funds. Elite QB (1.5 WAR = $2.25M) + good OL (0.8 WAR × 5 = $3.6M) or spread thin?"

### 4. Contract Negotiations
"Market rate for 1.5 WAR QB is $2.4M. We're offering $2.0M = below market but scheme fit adds value"

## 🔮 Future Enhancements

### Immediate (Ready to Build)
- [x] WAR calculation system
- [x] Leverage index for game context
- [x] Opponent quality adjustments
- [ ] Expand performance calculator to all positions (currently QB-optimized)
- [ ] Historical WAR tracking year-over-year
- [ ] Transfer portal WAR projections

### Medium Term
- [ ] Play-by-play data integration for true EPA calculations
- [ ] Game-by-game context tracking
- [ ] Position-specific advanced metrics (pass rush win rate, separation, etc.)
- [ ] Multi-year player development trajectories

### Long Term
- [ ] Machine learning models for WAR prediction
- [ ] Real-time market valuations during transfer windows
- [ ] Comparative analysis with professional scouting reports
- [ ] Integration with recruiting rankings

## 🤝 Contributing

This is a research project demonstrating advanced sports analytics. For questions or collaboration:

1. Fork the repository
2. Create a feature branch
3. Submit pull request with clear description

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **collegefootballdata.com** - Comprehensive CFB data API
- **Transfermarkt** - Inspiration for market-based valuation approach
- **Baseball's WAR** - Conceptual framework adapted for football

## 📞 Contact

Created by [@augsmog](https://github.com/augsmog)

---

**Key Insight**: Bo Nix (1.609 WAR) literally means "Oregon wins 1.6 more games with Bo Nix than with a replacement-level QB." That's worth $2.65M.
