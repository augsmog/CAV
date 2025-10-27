# College Football Transfer Market Dashboard

## 🎯 Mission: Transfermarkt for College Sports

This dashboard provides **market intelligence** for college football programs, helping athletic directors and coaches make data-driven transfer portal decisions.

---

## 🚀 Quick Start

### Method 1: Batch File (Easiest)
Double-click **`start_dashboard.bat`**

### Method 2: Command Line
```bash
python -m streamlit run dashboard.py
```

### Access
Open browser to: **http://localhost:8501**

---

## 📊 Dashboard Pages

### 1. **Market Overview** 💰
*Real-time market intelligence*

**Features:**
- Total FBS market value ($B)
- Top 10 most valuable teams
- Top 10 most valuable players
- Transfer portal activity heatmap
- Position availability analysis

**Use Case:** Get a pulse on the entire transfer market at a glance

---

### 2. **Team Valuations** 🏫
*Complete roster value analysis*

**Features:**
- Ranked list of all FBS teams by total roster value
- Search and filter teams
- Detailed team breakdowns:
  - Total roster value
  - Average player value
  - Value by position
  - Most valuable players on roster

**Use Case:** 
- Benchmark your program against competitors
- Identify which positions hold most value
- Understand roster composition

**Example Insights:**
- "Georgia has $45M in roster value, we have $28M"
- "Our QB room is worth $8M, theirs is $12M"
- "We need to upgrade at WR - only $2M invested there"

---

### 3. **Transfer Portal** 🔄
*Live marketplace of available players*

**Features:**
- All uncommitted transfer portal players
- Filter by position
- Sort by market value
- See where players are transferring FROM
- Market value of available talent

**Use Case:**
- See who's available RIGHT NOW
- Find players at positions of need
- Identify high-value targets
- Track which programs are losing talent

**Example:**
- "5-star QB worth $3.2M just entered portal from Alabama"
- "15 DBs available under $500K each"
- "Top RB from Georgia entered portal - valued at $1.8M"

---

### 4. **Target Players** 🎯
*AI-powered transfer recommendations*

**Features:**
- Position needs analysis for YOUR team
- Recommended transfer targets based on:
  - Your team's roster gaps
  - Scheme fit scores
  - Market value
  - Performance metrics
- Prioritized target list

**Use Case:**
- Get smart recommendations for your roster
- Find players who fit your scheme
- Fill position depth chart gaps
- Make data-driven recruiting decisions

**How It Works:**
1. Select your team
2. System analyzes your roster depth at each position
3. Identifies gaps (e.g., "Need 2 more WRs, 1 QB")
4. Searches portal for best fits
5. Ranks by scheme fit + value

**Example Output:**
```
YOUR TEAM: Michigan
Position Needs:
- WR: Need 2 (have 4, ideal 6)
- QB: Need 1 (have 2, ideal 3)

Top Targets:
1. John Smith - WR - From Ohio State
   💰 $1.2M | Scheme Fit: 92/100
   
2. Mike Johnson - QB - From USC  
   💰 $2.8M | Scheme Fit: 88/100
```

---

### 5. **Undervalued Gems** 💎
*Find the market inefficiencies*

**Features:**
- High performance, low value players
- Value efficiency scoring
- Filter by position and max value
- Identify "portal" availability
- Bargain hunting

**Use Case:**
- Find diamonds in the rough
- Maximize recruiting budget ROI
- Identify players from smaller programs
- Smart G5 → P5 transfer targets

**Value Efficiency Formula:**
```
Efficiency = Performance Score / Market Value
```

**Example:**
- Player A: 85 performance, $500K value = 170 efficiency ⭐⭐⭐
- Player B: 90 performance, $3M value = 30 efficiency

**Target Profile:**
- Performance > 60 (solid contributor)
- Market Value < $1M (affordable)
- High efficiency score (best bang for buck)

---

## 💡 Key Metrics Explained

### Market Value
Total estimated value of a player based on:
- 40% Performance (statistics)
- 20% Scheme Fit (system compatibility)
- 15% Brand/NIL (marketability)
- 15% Positional Value (supply/demand)
- 10% Win Impact (WAR)

### Team Roster Value
Sum of all valued players on team's roster

### Scheme Fit Score (0-100)
How well a player fits your offensive/defensive system
- 90-100: Perfect fit
- 75-89: Good fit
- 60-74: Adequate fit
- <60: Poor fit

### Value Efficiency
Performance-to-cost ratio - higher is better value

---

## 🎯 Use Cases by Role

### For Athletic Directors
- **Budget Planning**: "We have $35M in roster value, what's realistic?"
- **Competitive Analysis**: "How do we stack up against SEC?"
- **Transfer Strategy**: "Should we go after expensive stars or multiple solid players?"
- **ROI Tracking**: "Are we getting value from our NIL investments?"

### For Head Coaches
- **Roster Planning**: "Where are our depth chart weaknesses?"
- **Transfer Targeting**: "Who should we pursue in the portal?"
- **Scheme Fit**: "Which QBs fit our offense?"
- **Recruiting Priorities**: "Focus on high-value positions"

### For Position Coaches
- **Position Analysis**: "How does our WR room compare?"
- **Player Development**: "Which players increased value year-over-year?"
- **Portal Scouting**: "Find me 3 DB targets under $800K"
- **Scheme Matching**: "Players who fit our 3-4 defense"

### For Recruiting Coordinators
- **Market Intelligence**: "Who's entering the portal?"
- **Value Opportunities**: "Undervalued players we should target"
- **Competition**: "Who else is recruiting these players?"
- **Timing**: "When do most transfers happen?"

---

## 📈 Workflow Examples

### Example 1: Filling a Position Need

**Scenario**: Need to replace starting WR who declared for draft

**Workflow:**
1. Go to **Team Valuations** → Find your team
   - See you lost $2.1M in WR value
   
2. Go to **Transfer Portal** → Filter: WR
   - Find 47 WRs available
   - Sort by value (high to low)
   
3. Go to **Target Players** → Select your team
   - System recommends 5 WRs that fit your scheme
   - Top target: 85 scheme fit, $1.4M value
   
4. Go to **Undervalued Gems** → Position: WR, Max: $1M
   - Find 12 high-efficiency WRs
   - Contact top 3 immediately

**Result**: Data-driven shortlist of 8 WR targets ranked by fit and value

---

### Example 2: Program Rebuild Analysis

**Scenario**: New coach taking over struggling program

**Workflow:**
1. **Market Overview** → See total market landscape
   - Understand where your program ranks
   
2. **Team Valuations** → Select your team
   - Current roster value: $22M (Bottom 25%)
   - Competitors averaging $38M
   - Gap to close: $16M
   
3. **Transfer Portal** → Sort by value
   - Top 20 players = $60M total
   - Top 100 players = $180M total
   - Realistic targets: $25-35M range
   
4. **Target Players** → Your team
   - Need: 3 QB, 4 OL, 3 DB (critical gaps)
   - Recommended targets identified
   
5. **Undervalued Gems** → Build depth
   - 25 high-value players under $500K
   - G5 transfers with P5 potential

**Result**: Rebuild strategy with $8M in high-value transfers

---

### Example 3: Competitive Advantage Analysis

**Scenario**: Competing for conference championship

**Workflow:**
1. **Team Valuations** → Compare top 5 in conference
   - You: $41M (2nd in conference)
   - Leader: $44M
   - Weakness: OL value gap ($3M deficit)
   
2. **Transfer Portal** → Filter: OL
   - 3 elite OL available
   - Each valued $1.2M+
   
3. **Target Players** → Scheme fit analysis
   - One OL = 95 scheme fit (perfect match)
   - From ACC team, wants SEC move
   
4. **Undervalued Gems** → Depth building
   - Find 2 more OL under $600K
   - Build depth without breaking budget

**Result**: Close $3M OL gap, move to #1 in conference value

---

## 🔥 Pro Tips

### 1. **Cross-Reference Pages**
- Find player in Portal → Check if in Undervalued Gems → See full stats

### 2. **Track Competitors**
- Monitor rival teams' roster values
- See when they lose high-value players
- Target their portal entries

### 3. **Position Value Strategy**
- QBs command premium (20-30% of team value)
- OL/DL undervalued but critical
- Balance stars vs. depth

### 4. **Timing Matters**
- December portal window: 46.6% of moves
- April window: 22.9% of moves
- Early commitments get best players

### 5. **Scheme Fit > Raw Value**
- 85 fit + $800K > 60 fit + $1.2M
- System match = better on-field results

---

## 📊 Data & Accuracy

### Current Data
- **21,336 players** across 136 FBS programs
- **5,702 stat records** (2022-2023 seasons)
- **2,805 transfer movements** tracked
- **2,656 player valuations** (96% coverage)

### Update Frequency
- Real-time during dashboard session
- Re-run valuations weekly during season
- Full refresh monthly off-season

### Validation
- Elite QBs: $4-5M (matches market expectations)
- Average P5 starter: $500K-1.5M
- Role players: $50K-500K
- 1,731 players tracked across both seasons

---

## 🚀 Next Features (Coming Soon)

- [ ] Multi-year value tracking (player development)
- [ ] Draft projection correlation
- [ ] NIL deal database integration
- [ ] Social media impact scoring
- [ ] Transfer success prediction ML
- [ ] Recruiting class valuations
- [ ] Conference realignment impact

---

## 💻 Technical Notes

**Requirements:**
- Python 3.7+
- Streamlit
- Pandas, Plotly
- SQLite database

**Performance:**
- Cached queries (5-minute refresh)
- Handles 20K+ players smoothly
- < 2 second page loads

**Data Sources:**
- collegefootballdata.com API
- Historical transfer records
- Performance statistics

---

## 📞 Support

**Having Issues?**
- Dashboard not loading → Check if Streamlit running
- No data showing → Run `python test_model_valuations.py`
- Slow performance → Clear browser cache

**Want More Data?**
```bash
# Collect additional seasons
python collect_data.py --year 2024

# Re-run valuations
python test_model_valuations.py
```

---

## 🎯 Remember

This dashboard is your **competitive intelligence tool** for the transfer portal era.

Use it to:
✅ Make data-driven decisions  
✅ Find undervalued talent  
✅ Build winning rosters efficiently  
✅ Stay ahead of competitors  

---

**Start the dashboard**: Double-click `start_dashboard.bat` or run `python -m streamlit run dashboard.py`

**Access**: http://localhost:8501

---

*"Moneyball meets the Transfer Portal"* ⚡

