# CAV Product Vision: SaaS Platform for College Athletics

## Executive Summary

CAV (College Athlete Valuation) is building the **Transfermarkt for college sports** - a comprehensive SaaS platform that provides universities with data-driven tools for roster construction, cap management, and strategic team building in the NIL era.

---

## Market Context: The Opendorse Landscape

### What Opendorse Provides
Opendorse currently focuses on:
- **Brand Network**: Connecting athletes with Fortune 50 companies
- **Marketplace**: Athlete profile showcasing for brand discovery
- **Team Builder**: NIL budget allocation and compliance
- **Payments & Contracts**: Transaction management
- **Content & Insights**: Social media analytics
- **Education**: Personal branding resources

### The CAV Differentiator
**Opendorse helps athletes monetize their brand. CAV helps teams build winning rosters.**

We're not competing with Opendorse - we're complementary. They handle the athlete-to-brand connection. We handle the team-to-athlete decision-making.

---

## CAV Platform Architecture

### Core Product Pillars

```
┌─────────────────────────────────────────────────────────────┐
│                     CAV PLATFORM                            │
├─────────────────────────────────────────────────────────────┤
│  1. VALUATION ENGINE (Our Moat)                            │
│     • WAR-based player valuations                          │
│     • Market-calibrated pricing                            │
│     • Multi-year projections                               │
│     • Position-specific analytics                          │
├─────────────────────────────────────────────────────────────┤
│  2. ROSTER MANAGEMENT                                       │
│     • Current roster composition & value                   │
│     • Depth chart visualization                            │
│     • Scholarship allocation                               │
│     • Class balance (FR/SO/JR/SR)                          │
│     • Scheme fit analysis                                  │
├─────────────────────────────────────────────────────────────┤
│  3. CAP MANAGEMENT (NIL Budget)                            │
│     • Total NIL budget tracking                            │
│     • Position-based budget allocation                     │
│     • $/WAR efficiency metrics                             │
│     • Budget vs. market benchmarks                         │
│     • Compliance guardrails                                │
├─────────────────────────────────────────────────────────────┤
│  4. TRANSFER PORTAL INTELLIGENCE                           │
│     • Live portal tracker                                  │
│     • Target player identification                         │
│     • Market value estimates                               │
│     • Scheme fit scoring                                   │
│     • Recruitment priority rankings                        │
├─────────────────────────────────────────────────────────────┤
│  5. SCENARIO PLANNING                                       │
│     • "What-if" roster simulations                         │
│     • Multi-year projections                               │
│     • Budget scenario modeling                             │
│     • Win impact forecasting                               │
│     • Transfer vs. recruit tradeoffs                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Feature Deep-Dive

### 1. Valuation Engine (COMPLETE ✓)

**Status**: Production-ready for all positions

**Capabilities**:
- ✅ WAR calculation for QB, RB, WR, TE, DL, LB, DB
- ✅ Leverage-adjusted performance (clutch vs garbage time)
- ✅ Opponent quality adjustments
- ✅ Sample size confidence intervals
- ✅ Separate Player Value vs. NIL Potential
- ✅ Multi-season historical data (2022-2023)

**Value Proposition**:
> "Know exactly what every player is worth - not just to brands, but to your team's win total."

---

### 2. Roster Management (TO BUILD)

#### 2.1 Roster Dashboard
```
┌─────────────────────────────────────────────────────┐
│  OHIO STATE BUCKEYES - 2024 ROSTER                 │
├─────────────────────────────────────────────────────┤
│  Total Roster Value: $45.2M                        │
│  Total Players: 85                                  │
│  Avg Value/Player: $532K                           │
│  Conference Rank: #2 (Big Ten)                     │
│  National Rank: #8                                  │
├─────────────────────────────────────────────────────┤
│  BY POSITION GROUP:                                │
│  QB  (4 players) - $8.2M  | ■■■■■■■■■░░           │
│  RB  (8 players) - $3.1M  | ■■■░░░░░░░░           │
│  WR  (12 players) - $5.8M | ■■■■■░░░░░░           │
│  OL  (15 players) - $4.2M | ■■■░░░░░░░░           │
│  DL  (12 players) - $6.5M | ■■■■■■░░░░░           │
│  LB  (10 players) - $4.8M | ■■■■░░░░░░░           │
│  DB  (15 players) - $7.1M | ■■■■■■■░░░░           │
│  SPEC (9 players) - $1.5M | ■░░░░░░░░░░           │
└─────────────────────────────────────────────────────┘
```

#### 2.2 Depth Chart Manager
- Visual drag-and-drop depth chart
- Auto-calculate team WAR by starting lineup
- Identify depth weaknesses
- Project departures (seniors, early NFL entries)
- Scholarship counter with compliance alerts

#### 2.3 Class Balance Optimizer
```
Ideal Target: 25% FR, 25% SO, 25% JR, 25% SR

Current State:
FR: 28% (▲ Recruiting heavy)
SO: 22% (▼ Below target)
JR: 18% (▼ Transfer concern)
SR: 32% (▲ High turnover risk)

ALERT: 27 seniors departing after season
       Recommend targeting 15 transfers + 12 HS recruits
```

#### 2.4 Scheme Fit Alignment
- Flag players with poor scheme fit (<60/100)
- Identify scheme-perfect transfers (>90/100)
- Project performance change with scheme adjustments

---

### 3. Cap Management (TO BUILD)

#### 3.1 NIL Budget Tracker
```
┌─────────────────────────────────────────────────────┐
│  TOTAL NIL BUDGET: $12,000,000                     │
├─────────────────────────────────────────────────────┤
│  Allocated:     $10,500,000 (87.5%)                │
│  Reserved:      $1,000,000  (8.3%)                 │
│  Available:     $500,000    (4.2%)                 │
├─────────────────────────────────────────────────────┤
│  BUDGET ALLOCATION BY POSITION:                    │
│  QB:  $2.5M  (21%) - $/WAR: $862K  [EFFICIENT]    │
│  WR:  $1.8M  (15%) - $/WAR: $1.2M  [OVERPAID]    │
│  DL:  $2.2M  (18%) - $/WAR: $950K  [MARKET]      │
│  RB:  $1.1M  (9%)  - $/WAR: $2.8M  [UNDERPAID]   │
├─────────────────────────────────────────────────────┤
│  RECOMMENDATIONS:                                  │
│  ⚠ WR corps overpaid by ~$300K relative to value │
│  ⚠ RB room significantly underinvested            │
│  ✓ QB spending efficient for production           │
└─────────────────────────────────────────────────────┘
```

#### 3.2 Position Budget Optimizer
- AI-recommended budget allocation by position
- $/WAR benchmarking vs. conference/national averages
- Budget rebalancing scenarios
- Multi-year budget planning (recruit classes)

#### 3.3 Player Contract Tracker
- Individual player NIL commitments
- Contract expiration alerts
- Market value vs. current pay comparison
- Renegotiation triggers (underperforming/overperforming)

#### 3.4 Compliance Dashboard
- NCAA/conference rule adherence
- Budget cap warnings (if applicable)
- Documentation requirements
- Audit trail for all allocations

---

### 4. Transfer Portal Intelligence (TO BUILD)

#### 4.1 Live Portal Tracker
```
┌─────────────────────────────────────────────────────┐
│  TRANSFER PORTAL - LIVE (247 players)             │
├─────────────────────────────────────────────────────┤
│  FILTERS: Position: QB | Need Level: High         │
│           Budget: $500K-$1M | Fit: >85            │
├─────────────────────────────────────────────────────┤
│  RECOMMENDED TARGETS (8 matches):                  │
│                                                    │
│  1. ★★★ Kyle McCord (Syracuse QB)                │
│     WAR: 2.1 | Value: $3.2M | Fit: 94/100       │
│     Status: Committed to Syracuse (12/15)         │
│     Priority: HIGH - Elite production, scheme fit │
│                                                    │
│  2. ★★★ Jordan McCloud (Texas Tech QB)           │
│     WAR: 1.8 | Value: $2.8M | Fit: 89/100       │
│     Status: In portal (12/12)                     │
│     Priority: HIGH - Available, good value        │
│                                                    │
│  3. ★★☆ Emory Jones (Arizona State QB)           │
│     WAR: 1.2 | Value: $1.9M | Fit: 87/100       │
│     Status: In portal (12/10)                     │
│     Priority: MEDIUM - Solid backup option        │
└─────────────────────────────────────────────────────┘
```

#### 4.2 Target Identification Algorithm
1. **Need Assessment**: Auto-detect roster gaps (position, class year, scheme fit)
2. **Market Scan**: Cross-reference all portal players
3. **Value Matching**: Filter by budget constraints
4. **Fit Scoring**: Scheme compatibility + team culture
5. **Priority Ranking**: Weighted by need urgency × player quality

#### 4.3 Recruitment Board
- Drag-and-drop board (Interested → Contacted → Visiting → Committed)
- Automated follow-up reminders
- Competitive intelligence (other teams recruiting same player)
- Offer management (made offers vs. budget availability)

#### 4.4 "Undervalued Gems" Finder
- Players with high WAR but low NIL market demand
- Late-blooming sophomores/juniors
- Scheme-change beneficiaries
- Small-school standouts moving up

---

### 5. Scenario Planning (TO BUILD)

#### 5.1 Roster Simulator
```
SCENARIO: "Add 3 Portal DL + 2 Portal LB"

BEFORE:
Team WAR: 28.5 (Projected: 9-3 record)
Total Budget: $10.5M allocated
DL Depth: Weak (Backup starter quality)
LB Depth: Average

AFTER (with targets):
Team WAR: 31.2 (Projected: 10-2 record)
Total Budget: $12.2M allocated (+$1.7M)
DL Depth: Strong (Elite starters)
LB Depth: Strong (Above average starters)

ROI: +1.4 wins for +$1.7M investment
      = $1.2M per additional win
```

#### 5.2 "What-If" Scenarios
- **"Replace QB1 with portal transfer"**: Impact on wins, budget, scheme
- **"Lose top 5 recruits to flip"**: Fallback options, value loss
- **"3 unexpected NFL early entries"**: Emergency portal targets
- **"Budget cut by $2M"**: Optimization to maintain performance
- **"New OC with different scheme"**: Roster fit impacts, transfer needs

#### 5.3 Multi-Year Projections
- 4-year roster evolution
- Graduating class replacement plans
- Recruiting class value tracking
- Budget growth/contraction scenarios
- Conference realignment impacts

#### 5.4 Win Impact Calculator
```
Current Roster Baseline: 8.5 projected wins

IF we add:
+ Jalen Milroe (QB, WAR 2.1) → +2.1 wins = 10.6 wins
+ Quinshon Judkins (RB, WAR 1.2) → +1.2 wins = 11.8 wins
+ Will Johnson (CB, WAR 0.8) → +0.8 wins = 12.6 wins

BUT must lose (budget):
- Current QB2 (WAR 0.3) → -0.3 wins
- Current RB3 (WAR 0.1) → -0.1 wins

NET CHANGE: +3.8 wins (to 12.3 projected wins)
COST: +$5.2M in additional NIL
BUDGET REQUIRED: $15.7M total

PLAYOFF PROBABILITY: 35% → 88% (+53%)
```

---

## Technical Architecture

### Platform Stack
```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Next.js/React)                          │
│  • Team dashboards                                 │
│  • Scenario builder                                │
│  • Interactive roster charts                       │
└────────────────┬───────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────┐
│  API LAYER (FastAPI/Python)                        │
│  • REST API endpoints                              │
│  • Real-time portal updates                        │
│  • Valuation calculations                          │
└────────────────┬───────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────┐
│  CORE ENGINE (Python)                              │
│  • WAR calculator                                  │
│  • Scenario simulator                              │
│  • Budget optimizer                                │
│  • ML prediction models                            │
└────────────────┬───────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────┐
│  DATA LAYER                                        │
│  • PostgreSQL (production data)                    │
│  • Redis (caching, real-time)                      │
│  • S3 (analytics exports)                          │
└─────────────────────────────────────────────────────┘
```

### Data Sources
- **collegefootballdata.com**: Stats, rosters, schedules
- **Transfer Portal API**: Real-time portal tracking
- **Social Media APIs**: NIL potential metrics
- **Manual Input**: Team budgets, offers, commitments
- **Future**: Computer vision All-22 analysis (proprietary edge)

---

## Go-To-Market Strategy

### Phase 1: Pilot Program (Q1 2025)
- **Target**: 3-5 mid-major programs ($50K/year)
- **Focus**: Roster management + valuation
- **Goal**: Prove ROI (1-2 win improvement)

### Phase 2: Power 5 Expansion (Q2-Q3 2025)
- **Target**: 10-15 Power 5 programs ($200K/year)
- **Focus**: Full platform (cap + scenarios)
- **Goal**: Establish market leadership

### Phase 3: Conference Deals (Q4 2025+)
- **Target**: Conference-wide agreements (Big Ten, SEC)
- **Focus**: Standardized tools across conference
- **Goal**: Industry standard platform

### Pricing Model
```
TIER 1: Valuation Access Only
  - $25K/year
  - Dashboard access
  - Player valuations
  - Basic roster view

TIER 2: Roster Management
  - $100K/year
  - Everything in Tier 1
  - Depth chart tools
  - Class balance analysis
  - Transfer portal tracker

TIER 3: Full Platform
  - $200K/year
  - Everything in Tier 2
  - Cap management
  - Scenario planning
  - Dedicated success manager
  - Custom integrations

TIER 4: Conference Enterprise
  - Custom pricing
  - All programs in conference
  - Shared benchmarking
  - Conference-wide analytics
```

---

## Competitive Advantages

### 1. **The Valuation Moat**
Nobody else has a rigorous, WAR-based player valuation system. This is our intellectual property and competitive edge.

### 2. **Team-Centric (Not Athlete-Centric)**
Opendorse, INFLCR, and others focus on helping athletes. We help teams build rosters. Different customer, different use case.

### 3. **Data-Driven Decision Making**
We turn roster construction from art into science. CFOs and ADs love quantifiable ROI.

### 4. **Transfermarkt Model**
The "transfermarkt for college sports" positioning is instantly understandable and validates the market need.

### 5. **Future: Proprietary Data**
Long-term vision of All-22 computer vision gives us data nobody else can access.

---

## Success Metrics

### For Teams Using CAV
- **Win improvement**: +1.5 wins on average
- **NIL efficiency**: 20% better $/WAR vs. peer schools
- **Portal hit rate**: 75% of targeted transfers meet/exceed projections
- **Roster balance**: Optimal age distribution maintained
- **Budget adherence**: <5% variance from planned allocation

### For CAV Business
- **ARR Growth**: $5M by end of Year 2
- **Customer Count**: 40 programs by end of Year 2
- **Retention Rate**: >90% annual retention
- **NPS Score**: >70 (promoter score)
- **Market Share**: #1 platform for P5 programs

---

## Roadmap

### Q1 2025: Foundation
- ✅ Complete valuation engine (DONE!)
- ⬜ Build roster management dashboard
- ⬜ Pilot with 3 test schools
- ⬜ Incorporate feedback

### Q2 2025: Cap Management
- ⬜ Build budget tracker
- ⬜ Implement $/WAR analytics
- ⬜ Add compliance guardrails
- ⬜ Launch to 10 schools

### Q3 2025: Scenario Planning
- ⬜ Build roster simulator
- ⬜ Add "what-if" scenarios
- ⬜ Multi-year projections
- ⬜ Win impact calculator

### Q4 2025: Scale
- ⬜ Transfer portal intelligence
- ⬜ Conference deals
- ⬜ API partnerships
- ⬜ 40+ schools using platform

### 2026+: Advanced Features
- ⬜ Computer vision All-22 analysis
- ⬜ ML-powered recruitment recommendations
- ⬜ Predictive injury/performance models
- ⬜ Expand to basketball, baseball

---

## Conclusion

**CAV is positioned to become the operating system for college sports roster management in the NIL era.**

By combining our proprietary valuation technology with practical roster management, cap management, and scenario planning tools, we give athletic directors and coaches the data-driven insights they need to build championship teams efficiently.

We're not just selling valuations - we're selling wins.

---

*Document Version: 1.0*  
*Last Updated: October 27, 2025*  
*Author: CAV Product Team*

