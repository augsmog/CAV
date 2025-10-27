"""
CAV Methodology Dashboard Page
Explains our data-driven valuation approach with supporting data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Valuation Methodology | CAV",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #6366f1;
    }
    .formula-box {
        background-color: #f1f5f9;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    .section-header {
        color: #1e293b;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        color: #475569;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="font-size: 3rem; font-weight: 800; color: #1e293b;">🎯 Valuation Methodology</h1>
    <p style="font-size: 1.2rem; color: #64748b; max-width: 800px; margin: 0 auto;">
        Data-driven player valuations, not gut feelings. Learn how we quantify player worth using 
        WAR analytics, market data, and real NIL spending patterns.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# Section 1: The Problem We Solve
# ============================================================================
st.markdown('<h2 class="section-header">❌ The Problem: Gut Feelings vs. Data</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #dc2626;">Traditional Evaluation</h3>
        <ul>
            <li>Based on "eye test" and highlight reels</li>
            <li>Overvalues box score stats (passing yards, etc.)</li>
            <li>Ignores game context (garbage time vs. clutch)</li>
            <li>No opponent quality adjustments</li>
            <li>Doesn't account for sample size reliability</li>
        </ul>
        <p style="margin-top: 1rem; font-weight: 600;">Result: Overpaying backups, missing value gems</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #16a34a;">
        <h3 style="color: #16a34a;">CAV Approach</h3>
        <ul>
            <li>Quantitative WAR (Wins Above Replacement)</li>
            <li>Leverage-adjusted performance metrics</li>
            <li>Opponent strength calibration</li>
            <li>Sample size confidence intervals</li>
            <li>Market-calibrated dollar values</li>
        </ul>
        <p style="margin-top: 1rem; font-weight: 600;">Result: Efficient spending, winning rosters</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# Section 2: NIL Market Data
# ============================================================================
st.markdown('<h2 class="section-header">💰 Real Market Data: NIL Spending by Team</h2>', unsafe_allow_html=True)

# Load NIL data
try:
    with open('data/nil_spending_data.json', 'r') as f:
        nil_data = json.load(f)
    
    df_nil = pd.DataFrame(nil_data['data'])
    df_nil = df_nil[~df_nil.get('is_average', False)]  # Filter out averages
    
    # Statistics
    stats = nil_data.get('statistics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average NIL Budget", f"${stats.get('average_budget', 0)/1e6:.1f}M")
    col2.metric("Median NIL Budget", f"${stats.get('median_budget', 0)/1e6:.1f}M")
    col3.metric("Top Spender", f"${stats.get('max_budget', 0)/1e6:.1f}M")
    col4.metric("Total Market", f"${stats.get('total_nil_spending', 0)/1e6:.0f}M")
    
    st.markdown("### Top 20 NIL Spenders (2023 Season)")
    
    # Create bar chart
    df_top = df_nil.nsmallest(20, 'nil_budget').sort_values('nil_budget')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_top['team'],
        x=df_top['nil_budget'] / 1e6,
        orientation='h',
        marker=dict(
            color=df_top['nil_budget'],
            colorscale='Blues',
            showscale=False
        ),
        text=[f"${b/1e6:.1f}M" for b in df_top['nil_budget']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>NIL Budget: $%{x:.1f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="NIL Budget (Millions)",
        yaxis_title="",
        height=600,
        showlegend=False,
        xaxis=dict(range=[0, 22]),
        margin=dict(l=150)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Conference breakdown
    st.markdown("### NIL Spending by Conference")
    
    conf_avg = df_nil.groupby('conference')['nil_budget'].mean().sort_values(ascending=False)
    
    fig_conf = px.bar(
        x=conf_avg.values / 1e6,
        y=conf_avg.index,
        orientation='h',
        title="Average NIL Budget by Conference",
        labels={'x': 'Average Budget (Millions)', 'y': 'Conference'},
        text=[f"${v/1e6:.1f}M" for v in conf_avg.values]
    )
    fig_conf.update_traces(textposition='outside')
    fig_conf.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig_conf, use_container_width=True)
    
    # Source note
    st.info("""
    **Data Source**: 2023 NIL Collective Research  
    - Power 5 collectives raised $677.25M total in 2023
    - Average per school: $9.82M
    - SEC average: $13.29M | Big Ten average: $10.69M
    """)
    
except FileNotFoundError:
    st.warning("NIL spending data not yet loaded. Run `python scrapers/nil_ncaa_scraper.py` to collect data.")

# ============================================================================
# Section 3: Our Valuation Formula
# ============================================================================
st.markdown('<h2 class="section-header">🧮 The Valuation Formula</h2>', unsafe_allow_html=True)

st.markdown("""
### Step 1: Calculate WAR (Wins Above Replacement)

WAR quantifies how many wins a player contributes beyond what a replacement-level player would provide.
""")

st.markdown("""
<div class="formula-box">
<strong>WAR = Base Performance × Leverage Index × Opponent Quality × Participation Factor</strong>

Where:
• <strong>Base Performance</strong>: Position-specific metrics (QB: YPA, completion %, TD/INT; DL: sacks, TFL; etc.)
• <strong>Leverage Index</strong>: Game context weight (clutch = 1.5x, garbage time = 0.3x)
• <strong>Opponent Quality</strong>: Strength of competition (P5 = 1.0x+, FCS = 0.7x)
• <strong>Participation Factor</strong>: Snap share × starter bonus
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Step 2: Convert WAR to Player Value
    
    Player value is calibrated to real NIL market data:
    """)
    
    st.markdown("""
    <div class="formula-box">
    <strong>Player Value = WAR × Position Market Rate</strong>
    
    Position Rates ($/WAR):
    • QB: $1,500,000 per WAR
    • RB: $1,000,000 per WAR
    • WR: $750,000 per WAR
    • DL: $1,200,000 per WAR
    • LB: $900,000 per WAR
    • DB: $800,000 per WAR
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Step 3: Calculate NIL Potential
    
    Separate from team value, this measures athlete's earning power:
    """)
    
    st.markdown("""
    <div class="formula-box">
    <strong>NIL Potential = (Brand Score × Program Factor) + Position Premium</strong>
    
    Brand Score Components:
    • Social media following
    • Engagement rate
    • Media mentions
    • On-field production
    </div>
    """, unsafe_allow_html=True)

# Example calculation
st.markdown("### Example: Elite QB Valuation")

example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    st.markdown("""
    **Player Stats**
    - 3,500 passing yards
    - 8.5 yards/attempt
    - 35 TDs, 8 INTs
    - 750 snaps (88% of team)
    - 10 starts, 12 games
    """)

with example_col2:
    st.markdown("""
    **WAR Calculation**
    - Base Performance: 85/100
    - Leverage Index: 1.15x
    - Opponent Quality: 1.05x
    - Participation: 0.92
    - **WAR: 2.8**
    """)

with example_col3:
    st.markdown("""
    **Final Valuation**
    - WAR: 2.8
    - Rate: $1.5M per WAR
    - **Player Value: $4.2M**
    - **NIL Potential: $850K**
    """)

# ============================================================================
# Section 4: Why This Works
# ============================================================================
st.markdown('<h2 class="section-header">✅ Why This Methodology Works</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h4>📊 Empirically Grounded</h4>
        <p>Built on real NIL spending data from 100+ programs. Market rates calibrated to actual deals.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #8b5cf6;">
        <h4>⚖️ Context-Aware</h4>
        <p>Adjusts for opponent strength, game leverage, and sample size. No more overvaluing garbage-time stats.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #10b981;">
        <h4>🎯 Predictive Power</h4>
        <p>WAR correlates strongly with team wins. Optimize $/WAR to maximize on-field success per dollar.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# Section 5: Key Insights
# ============================================================================
st.markdown('<h2 class="section-header">🔑 Key Insights from Our Data</h2>', unsafe_allow_html=True)

insight1, insight2 = st.columns(2)

with insight1:
    st.markdown("""
    ### 1. Position Value Hierarchy
    
    Not all positions are valued equally in the NIL market:
    
    1. **QB** ($1.5M/WAR) - Highest due to outsized impact
    2. **DL** ($1.2M/WAR) - Premium pass rushers command top dollar
    3. **RB** ($1.0M/WAR) - Market rate for elite runners
    4. **LB** ($900K/WAR) - Defensive playmakers
    5. **DB** ($800K/WAR) - Coverage specialists
    6. **WR** ($750K/WAR) - Deep market creates efficiency
    
    **Implication**: Focus NIL budget on QB, DL, and undervalued WRs
    """)

with insight2:
    st.markdown("""
    ### 2. Conference Spending Arms Race
    
    Clear spending tiers have emerged:
    
    - **Elite ($15M+)**: Texas, Alabama, Ohio State
    - **High ($10-15M)**: Most SEC/Big Ten schools
    - **Medium ($7-10M)**: ACC, Big 12 leaders
    - **Low ($2-5M)**: Group of 5 programs
    
    **Implication**: Must spend to compete within conference. G5 programs need efficiency focus.
    """)

# ============================================================================
# Section 6: How to Use CAV
# ============================================================================
st.markdown('<h2 class="section-header">🚀 How to Use CAV Valuations</h2>', unsafe_allow_html=True)

use_case1, use_case2, use_case3 = st.columns(3)

with use_case1:
    st.markdown("""
    ### Transfer Portal Targeting
    
    1. Set your NIL budget
    2. Filter portal players by position need
    3. Sort by WAR (high impact)
    4. Check value efficiency ($/WAR)
    5. Target undervalued gems
    
    **Goal**: Maximize WAR added per dollar spent
    """)

with use_case2:
    st.markdown("""
    ### Roster Optimization
    
    1. Calculate current roster WAR
    2. Identify overpaid players (high $/WAR)
    3. Find underpaid players (low $/WAR)
    4. Rebalance budget allocation
    5. Project win impact
    
    **Goal**: Improve team WAR without increasing budget
    """)

with use_case3:
    st.markdown("""
    ### Recruiting Strategy
    
    1. Compare HS recruit value projections
    2. Assess portal transfer alternatives
    3. Run "what-if" scenarios
    4. Calculate ROI by position
    5. Make data-backed offers
    
    **Goal**: Build sustainable winning rosters
    """)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #64748b;">
    <p><strong>CAV Platform</strong> - Data-driven valuations for the NIL era</p>
    <p>Questions? Contact us or view our <a href="https://github.com/augsmog/CAV" target="_blank">GitHub repository</a></p>
</div>
""", unsafe_allow_html=True)

