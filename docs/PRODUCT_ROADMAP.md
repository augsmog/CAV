# CAV Product Roadmap: Building the SaaS Platform

## Vision Statement
**Build the Transfermarkt for college sports** - a comprehensive SaaS platform that provides universities with data-driven tools for roster construction, cap management, and strategic team building in the NIL era.

---

## Competitive Positioning

### Opendorse (Current Market Leader)
**Their Focus**: Help athletes monetize their personal brand
- Athlete marketplace for brand deals
- NIL compliance & education
- Content distribution tools
- Brand-to-athlete connections

**Our Focus**: Help teams build winning rosters
- Player valuation & WAR analytics
- Roster construction optimization
- NIL budget management  
- Transfer portal intelligence
- Scenario planning tools

**Key Insight**: We're complementary, not competitive. They connect athletes to brands. We help teams make data-driven roster decisions.

---

## Phase 1: Roster Management Tools (Q1 2025)

### 1.1 Roster Dashboard
**Status**: To Build  
**Timeline**: 4-6 weeks  
**Dependencies**: Valuation engine (✅ Complete)

**Features**:
- Current roster visualization
- Total roster value calculation
- Position group breakdowns
- Conference/national ranking
- Value distribution charts

**Technical Requirements**:
- Streamlit or React dashboard
- Database queries for aggregated stats
- Chart.js/Plotly visualizations
- Real-time data refresh

---

### 1.2 Depth Chart Manager
**Status**: To Build  
**Timeline**: 3-4 weeks

**Features**:
- Visual depth chart (drag-and-drop interface)
- Auto-calculate team WAR by starting lineup
- Backup quality assessment
- Injury/departure impact simulation
- Export to PDF for coaching staff

**Technical Requirements**:
- React DnD or Streamlit drag components
- WAR aggregation by lineup
- Position-specific depth scoring
- PDF generation (ReportLab)

---

### 1.3 Scholarship Tracker
**Status**: To Build  
**Timeline**: 2 weeks

**Features**:
- 85-man roster counter
- Scholarship allocation by position/class
- Compliance alerts (FBS/FCS rules)
- Projected scholarship availability
- Class balance visualization (FR/SO/JR/SR)

**Technical Requirements**:
- Simple counter logic
- NCAA rule validation
- Alert system
- Balance optimization algorithm

---

## Phase 2: Cap Management System (Q2 2025)

### 2.1 NIL Budget Tracker
**Status**: To Build  
**Timeline**: 4 weeks

**Features**:
- Total budget input & tracking
- Allocated vs. available funds
- Position-based budget allocation
- Player-level NIL commitments
- Budget utilization percentage

**Technical Requirements**:
- Budget database tables
- Player-to-budget linking
- Aggregation queries
- Alert thresholds

---

### 2.2 $/WAR Efficiency Analytics
**Status**: To Build  
**Timeline**: 3 weeks

**Features**:
- Calculate $/WAR for each player
- Position group efficiency metrics
- Benchmarking vs. conference/national averages
- Overpaid/underpaid player identification
- Reallocation recommendations

**Technical Requirements**:
- $/WAR calculation (NIL $ / player WAR)
- Peer comparison database
- Statistical outlier detection
- Recommendation engine

---

### 2.3 Contract Management
**Status**: To Build  
**Timeline**: 3 weeks

**Features**:
- Individual player NIL agreements
- Contract expiration tracking
- Automatic renewal reminders
- Market value vs. current pay comparison
- Renegotiation triggers

**Technical Requirements**:
- Contract database schema
- Expiration date tracking
- Email/notification system
- Market value delta calculation

---

## Phase 3: Transfer Portal Intelligence (Q3 2025)

### 3.1 Live Portal Tracker
**Status**: To Build  
**Timeline**: 6 weeks

**Features**:
- Real-time transfer portal player list
- Auto-update from data sources
- Filter by position, value, scheme fit
- Target identification algorithm
- Competitive intelligence (other schools recruiting)

**Technical Requirements**:
- Portal data API integration
- Automated scraping (if no API)
- Real-time database updates
- Advanced filtering logic
- Notification system for new entries

---

### 3.2 Target Recommendation Engine
**Status**: To Build  
**Timeline**: 4 weeks

**Features**:
- Auto-detect roster gaps
- Match portal players to team needs
- Budget constraint filtering
- Scheme fit scoring
- Priority ranking algorithm

**Technical Requirements**:
- Need assessment algorithm
- Multi-criteria matching
- Weighted scoring system
- ML-based recommendations (future)

---

### 3.3 Recruitment Board
**Status**: To Build  
**Timeline**: 3 weeks

**Features**:
- Kanban-style board (Interested → Contacted → Visiting → Committed)
- Drag-and-drop player cards
- Notes & communication log
- Follow-up reminders
- Offer tracking

**Technical Requirements**:
- Kanban UI (React Beautiful DnD)
- Status tracking database
- CRM-style logging
- Reminder system

---

## Phase 4: Scenario Planning (Q4 2025)

### 4.1 Roster Simulator
**Status**: To Build  
**Timeline**: 6 weeks

**Features**:
- "What-if" scenario builder
- Add/remove players from roster
- Auto-calculate new team WAR
- Budget impact calculation
- Win projection updates

**Technical Requirements**:
- Scenario state management
- WAR aggregation engine
- Budget simulation
- Win projection model

---

### 4.2 Multi-Year Projections
**Status**: To Build  
**Timeline**: 4 weeks

**Features**:
- 4-year roster evolution
- Graduating class replacement planning
- Recruiting class value tracking
- Budget growth/contraction scenarios

**Technical Requirements**:
- Multi-year database schema
- Graduation/eligibility tracking
- Recruiting class integration
- Time-series projections

---

### 4.3 Win Impact Calculator
**Status**: To Build  
**Timeline**: 3 weeks

**Features**:
- Team WAR → Win projection
- Incremental win value calculation
- Playoff probability estimates
- ROI per NIL dollar spent

**Technical Requirements**:
- WAR-to-wins conversion model
- Historical win correlation data
- Probability calculations
- Cost-benefit analysis

---

## Technical Infrastructure Needs

### Backend
- **Framework**: FastAPI or Django REST
- **Database**: PostgreSQL (production), Redis (caching)
- **Hosting**: AWS/GCP/Azure
- **Authentication**: OAuth 2.0, team-based access control

### Frontend
- **Option A**: React/Next.js (most flexible, best UX)
- **Option B**: Streamlit (faster to build, less polish)
- **Visualization**: D3.js, Chart.js, Plotly

### Data Pipeline
- **Ingestion**: Continue using current ETL
- **Real-time**: WebSocket for portal updates
- **Caching**: Redis for frequently accessed data
- **Export**: CSV, PDF, Excel for reports

---

## Implementation Priority

### HIGH PRIORITY (Build First)
1. **Roster Dashboard** - Core value prop
2. **Depth Chart Manager** - Immediate coaching utility
3. **NIL Budget Tracker** - AD/CFO requirement
4. **$/WAR Analytics** - Unique differentiator

### MEDIUM PRIORITY (Build Second)
5. **Transfer Portal Tracker** - High value, but data dependencies
6. **Scenario Planning** - Powerful, but complex
7. **Contract Management** - Nice-to-have, not critical

### FUTURE (Post-MVP)
8. **Multi-Year Projections**
9. **ML Recommendations**
10. **Computer Vision All-22 Analysis**

---

## Resource Requirements

### Development Team
- **1 Full-Stack Developer**: Frontend + Backend
- **1 Data Engineer**: ETL, APIs, data quality
- **1 ML Engineer (part-time)**: Recommendation algorithms
- **1 Designer (contract)**: UI/UX for dashboards

### Timeline to MVP
- **3-4 months** for Phase 1 + Phase 2 (roster + cap management)
- **Pilot-ready** by Q1 2025

### Budget Estimate
- **Development**: $150K-$200K (3-4 months)
- **Infrastructure**: $5K/month (AWS, APIs, tools)
- **Sales/Marketing**: $50K (pilot program)

**Total First Year**: ~$300K-$350K

---

## Success Metrics

### Product Metrics
- **Roster value accuracy**: ±10% of actual win outcomes
- **Budget optimization**: 15-20% improvement in $/WAR
- **Portal hit rate**: 70%+ of targeted players meet projections
- **User engagement**: Coaches log in 3+ times per week during season

### Business Metrics
- **Pilot conversion**: 80%+ pilots convert to paid
- **Revenue Year 1**: $500K (5 schools @ $100K)
- **Revenue Year 2**: $3M (20 schools @ $150K avg)
- **Churn**: <10% annual

---

## Next Steps (Immediate)

1. ✅ **Complete valuation engine** (DONE!)
2. ⬜ **Push current code to GitHub** (In progress)
3. ⬜ **Build Roster Dashboard MVP** (4 weeks)
4. ⬜ **Add NIL Budget Tracker** (3 weeks)
5. ⬜ **Pilot with 1-2 friendly programs** (Find via network)
6. ⬜ **Iterate based on feedback** (Ongoing)

---

*Last Updated: October 27, 2025*

