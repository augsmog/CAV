"""
Individual Player Deep Dive - Level 3
The "Player Profile" - Where Trust Is Built
Shows complete 6-pillar valuation breakdown with transparency
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path

st.set_page_config(
    page_title="Player Profile | CAV",
    page_icon="👤",
    layout="wide"
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Pillar Card */
    .pillar-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    .pillar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .pillar-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .pillar-score {
        font-size: 1.5rem;
        font-weight: 800;
        color: #667eea;
    }
    
    .pillar-contribution {
        font-size: 1.125rem;
        font-weight: 700;
        color: #10b981;
        margin: 0.5rem 0;
    }
    
    .pillar-details {
        color: #64748b;
        font-size: 0.875rem;
        line-height: 1.6;
    }
    
    .pillar-details ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .progress-bar {
        width: 100%;
        height: 24px;
        background: #f1f5f9;
        border-radius: 12px;
        overflow: hidden;
        margin: 0.75rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 0.5rem;
        color: white;
        font-weight: 700;
        font-size: 0.875rem;
        transition: width 0.3s ease;
    }
    
    /* Value Summary Box */
    .value-summary {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border: 2px solid #667eea30;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .value-summary h3 {
        color: #667eea;
        margin: 0 0 1rem 0;
    }
    
    .value-line {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .value-line:last-child {
        border-bottom: none;
        font-weight: 700;
        font-size: 1.125rem;
        color: #667eea;
        padding-top: 1rem;
        margin-top: 0.5rem;
        border-top: 2px solid #667eea;
    }
    
    /* Comp Card */
    .comp-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .comp-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102,126,234,0.1);
    }
    
    .similarity-stars {
        color: #fbbf24;
        font-size: 1.25rem;
    }
    
    /* Recommendation Box */
    .recommendation-box {
        background: linear-gradient(135deg, #10b98115, #ffffff);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .recommendation-box h3 {
        color: #10b981;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .recommendation-badge {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.125rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA (Mock player for demonstration)
# ============================================================================

# In production, this would load from the selected player
mock_player = {
    'name': 'Jake Smith',
    'position': 'QB',
    'year': 'RS Sophomore',
    'eligibility': 3,
    'school': 'Alabama',
    'photo_url': None,
    
    # Current season stats
    'pass_yards': 3214,
    'pass_tds': 28,
    'completion_pct': 67.2,
    'qb_rating': 158.2,
    'national_rank': 12,
    
    # Market value
    'market_value': 850000,
    'value_range_low': 725000,
    'value_range_high': 975000,
    'current_investment': 650000,
    'conf_rank': 4,
    
    # 6 Pillars
    'pillar1_score': 92,
    'pillar1_contribution': 380000,
    'pillar2_score': 85,
    'pillar2_contribution': 210000,
    'pillar3_score': 78,
    'pillar3_contribution': 140000,
    'pillar4_score': 88,
    'pillar4_contribution': 85000,
    'pillar5_score': 71,
    'pillar5_contribution': 65000,
    'pillar6_adjustment': -5,
    'pillar6_contribution': -45000,
    
    # Risk
    'portal_risk': 15,
    'portal_risk_label': 'Low',
}

# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([6, 1])

with col1:
    if st.button("← Back to Roster"):
        st.switch_page("dashboard_executive.py")

with col2:
    if st.button("📊 Export"):
        st.toast("Export functionality coming soon!")

st.markdown(f"""
<h1 style="color: #1e293b; margin: 0;">#{7} {mock_player['name']} - {mock_player['position']} - {mock_player['year']}</h1>
""", unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Overview", 
    "💰 Valuation", 
    "📊 Performance", 
    "🌍 Market", 
    "🔮 Projection"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: #f8fafc; padding: 2rem; border-radius: 12px; text-align: center;">
            <div style="width: 200px; height: 200px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; margin: 0 auto 1rem auto; display: flex; align-items: center; justify-content: center; color: white; font-size: 4rem; font-weight: 800;">
                #7
            </div>
            <p style="color: #64748b; margin: 0;">Photo placeholder</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Player Snapshot")
        
        cols = st.columns(2)
        with cols[0]:
            st.metric("Current Market Value", f"${mock_player['market_value']:,}")
            st.metric("Value Rank", f"12th of 127 FBS QBs")
        
        with cols[1]:
            st.metric("Conference Rank", f"4th of 16 SEC QBs")
            st.metric("Portal Risk", f"🟢 {mock_player['portal_risk_label']} ({mock_player['portal_risk']}%)")
        
        st.markdown(f"""
        **Bio:** {mock_player['year']}, {mock_player['eligibility']} yrs eligibility  
        **Recruited:** ★★★★ (0.9512 composite)  
        **Height/Weight:** 6'3", 215 lbs
        """)
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats (2024 Season)")
    
    cols = st.columns(4)
    stats = [
        ('Pass Yards', f"{mock_player['pass_yards']:,}", '11th FBS'),
        ('Pass TDs', str(mock_player['pass_tds']), '8th FBS'),
        ('Completion %', f"{mock_player['completion_pct']}%", '18th FBS'),
        ('QB Rating', str(mock_player['qb_rating']), '9th FBS'),
    ]
    
    for col, (label, value, rank) in zip(cols, stats):
        with col:
            st.metric(label, value, rank)
    
    # Key Insights
    st.markdown("### 🎯 Key Insights")
    
    st.success("""
    **✅ Strengths:**
    - Elite red zone efficiency (82%, 3rd nationally)
    - Strong deep ball (9.4 yds/attempt on 20+ yd passes)
    - Improving weekly (+12% rating since Week 4)
    - High social media engagement (180K followers)
    """)
    
    st.warning("""
    **⚠️ Areas for Development:**
    - Pressure management (sacked 8.2% of dropbacks)
    - Consistency vs. ranked opponents (115.3 rating)
    """)
    
    st.info("""
    **💡 Bottom Line:**  
    Elite value at $850K. Performing like $1.1M player. Strong retention candidate. Market would pay more.
    """)

# ============================================================================
# TAB 2: VALUATION (Most Important!)
# ============================================================================

with tab2:
    st.markdown("## 💰 Market Value Analysis")
    
    # Value Range Visualization
    st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h3 style="margin: 0 0 1rem 0;">Current Market Value: <span style="color: #667eea;">${mock_player['market_value']:,}</span></h3>
        <p style="color: #64748b; margin-bottom: 1.5rem;">Confidence Range: ${mock_player['value_range_low']:,} - ${mock_player['value_range_high']:,} (80% confidence)</p>
        
        <div style="position: relative; height: 40px; background: linear-gradient(90deg, #ef4444 0%, #fbbf24 25%, #10b981 50%, #fbbf24 75%, #ef4444 100%); border-radius: 20px; margin: 1rem 0;">
            <div style="position: absolute; left: 50%; transform: translateX(-50%); top: -5px; width: 4px; height: 50px; background: #1e293b;"></div>
            <div style="position: absolute; left: 50%; transform: translateX(-50%); top: 45px; font-weight: 700; color: #1e293b;">
                ${mock_player['market_value']:,}
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-top: 3rem; font-size: 0.875rem; color: #64748b;">
            <div>Low<br>${mock_player['value_range_low']:,}</div>
            <div>High<br>${mock_player['value_range_high']:,}</div>
        </div>
        
        <p style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
            <strong>Transfer Portal Comps:</strong> $775K - $925K (5 players)<br>
            <strong>Your Current Investment:</strong> ${mock_player['current_investment']:,} 
            <span style="color: #10b981; font-weight: 700;">🟢 Good Value</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 🌟 THE 6-PILLAR BREAKDOWN - Core of Your Transparency
    st.markdown("## 📊 Six-Pillar Value Breakdown")
    
    st.markdown("""
    Our valuation combines **six independent models** to produce the most accurate player values in college sports.  
    Each pillar is weighted based on historical predictive power and validated against actual market outcomes.
    """)
    
    # PILLAR 1: PRODUCTION VALUE
    st.markdown(f"""
    <div class="pillar-card">
        <div class="pillar-header">
            <h3 class="pillar-title">PILLAR 1: PRODUCTION VALUE</h3>
            <span class="pillar-score">{mock_player['pillar1_score']}/100</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {mock_player['pillar1_score']}%;">
                {mock_player['pillar1_score']}%
            </div>
        </div>
        
        <p class="pillar-contribution">Contribution: +${mock_player['pillar1_contribution']:,} (35% weight)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Historical on-field performance
            <ul>
                <li>Pass efficiency: 158.2 rating (9th nationally)</li>
                <li>TD production: 28 TDs (8th nationally)</li>
                <li>Turnover rate: Low (8 INTs, 2.1% INT rate)</li>
                <li>EPA per play: +0.32 (Top 15%)</li>
            </ul>
            <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View Detailed Stats →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PILLAR 2: PREDICTIVE PERFORMANCE
    st.markdown(f"""
    <div class="pillar-card">
        <div class="pillar-header">
            <h3 class="pillar-title">PILLAR 2: PREDICTIVE PERFORMANCE</h3>
            <span class="pillar-score">{mock_player['pillar2_score']}/100</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {mock_player['pillar2_score']}%;">
                {mock_player['pillar2_score']}%
            </div>
        </div>
        
        <p class="pillar-contribution">Contribution: +${mock_player['pillar2_contribution']:,} (25% weight)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Predicted performance trajectory
            <ul>
                <li>Year-over-year improvement: +18% in efficiency</li>
                <li>3 years eligibility remaining (high upside)</li>
                <li>Historical comparables improved 12-25% next year</li>
                <li>NFL draft projection: 5th-7th round (2027)</li>
            </ul>
            <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View Projection Model →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PILLAR 3: MARKET SCARCITY
    st.markdown(f"""
    <div class="pillar-card">
        <div class="pillar-header">
            <h3 class="pillar-title">PILLAR 3: POSITIONAL SCARCITY</h3>
            <span class="pillar-score">{mock_player['pillar3_score']}/100</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {mock_player['pillar3_score']}%;">
                {mock_player['pillar3_score']}%
            </div>
        </div>
        
        <p class="pillar-contribution">Contribution: +${mock_player['pillar3_contribution']:,} (15% weight)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Position supply/demand
            <ul>
                <li>QB is highest-value position (+premium)</li>
                <li>Only 18 P4-caliber QBs in portal currently</li>
                <li>30+ schools with QB need</li>
                <li>Demand/supply ratio: 1.67x (above average)</li>
            </ul>
            <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View Market Scarcity →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PILLAR 4: SCHOOL CONTEXT
    st.markdown(f"""
    <div class="pillar-card">
        <div class="pillar-header">
            <h3 class="pillar-title">PILLAR 4: MARKET CONTEXT</h3>
            <span class="pillar-score">{mock_player['pillar4_score']}/100</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {mock_player['pillar4_score']}%;">
                {mock_player['pillar4_score']}%
            </div>
        </div>
        
        <p class="pillar-contribution">Contribution: +${mock_player['pillar4_contribution']:,} (10% weight)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Program & conference impact
            <ul>
                <li>SEC premium: 1.3x multiplier</li>
                <li>Your school: High NIL capacity ($25M+ budget)</li>
                <li>Starter role: Guaranteed (no competition)</li>
                <li>Development track record: Strong QB coaching</li>
            </ul>
            <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View School Context →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PILLAR 5: BRAND VALUE
    st.markdown(f"""
    <div class="pillar-card">
        <div class="pillar-header">
            <h3 class="pillar-title">PILLAR 5: BRAND VALUE</h3>
            <span class="pillar-score">{mock_player['pillar5_score']}/100</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {mock_player['pillar5_score']}%;">
                {mock_player['pillar5_score']}%
            </div>
        </div>
        
        <p class="pillar-contribution">Contribution: +${mock_player['pillar5_contribution']:,} (10% weight)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Marketability & NIL earning potential
            <ul>
                <li>Social media: 180K followers (above average)</li>
                <li>Engagement rate: 4.2% (strong)</li>
                <li>Media exposure: 12 national TV games</li>
                <li>Marketability: Clean image, community involvement</li>
            </ul>
            <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View Brand Analysis →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PILLAR 6: RISK ADJUSTMENTS
    st.markdown(f"""
    <div class="pillar-card" style="border-left-color: #10b981;">
        <div class="pillar-header">
            <h3 class="pillar-title" style="color: #10b981;">PILLAR 6: RISK ADJUSTMENTS</h3>
            <span class="pillar-score" style="color: #10b981;">Impact: {mock_player['pillar6_adjustment']}%</span>
        </div>
        
        <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; margin: 0.75rem 0;">
            <strong style="color: #10b981;">🟢 Low Risk Profile</strong>
        </div>
        
        <p class="pillar-contribution" style="color: #ef4444;">Adjustment: ${mock_player['pillar6_contribution']:,} (5% discount)</p>
        
        <div class="pillar-details">
            <strong>What it measures:</strong> Reliability & downside protection
            <ul>
                <li>Injury history: None (🟢 Clean)</li>
                <li>Character: No issues (🟢 Clean)</li>
                <li>Performance variance: Low (🟢 Consistent)</li>
                <li>Portal risk: 15% (🟢 Low flight risk)</li>
            </ul>
            <button style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                View Risk Assessment →
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # VALUE CALCULATION SUMMARY
    st.markdown(f"""
    <div class="value-summary">
        <h3>🧮 VALUE CALCULATION SUMMARY</h3>
        
        <div class="value-line">
            <span>Base Production Value:</span>
            <span>${mock_player['pillar1_contribution']:,} (35% weight)</span>
        </div>
        <div class="value-line">
            <span>+ Predictive Performance:</span>
            <span>${mock_player['pillar2_contribution']:,} (25% weight)</span>
        </div>
        <div class="value-line">
            <span>+ Positional Scarcity:</span>
            <span>${mock_player['pillar3_contribution']:,} (15% weight)</span>
        </div>
        <div class="value-line">
            <span>+ Market Context:</span>
            <span>${mock_player['pillar4_contribution']:,} (10% weight)</span>
        </div>
        <div class="value-line">
            <span>+ Brand Value:</span>
            <span>${mock_player['pillar5_contribution']:,} (10% weight)</span>
        </div>
        <div class="value-line">
            <span>- Risk Adjustments:</span>
            <span>${mock_player['pillar6_contribution']:,} (5% discount)</span>
        </div>
        <div class="value-line">
            <span><strong>Total Market Value:</strong></span>
            <span><strong>${mock_player['market_value']:,}</strong></span>
        </div>
        
        <button style="background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 700; margin-top: 1rem; width: 100%;">
            View Full Methodology Documentation →
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # COMPARABLE PLAYERS
    st.markdown("## 🔍 Comparable Players (Market Validation)")
    
    comps = [
        {'name': 'Marcus Williams', 'school': 'TCU', 'year': 'RS Jr', 'yards': 3089, 'tds': 26, 'rating': 154.1, 'value': 825000, 'portal_deal': 850000, 'similarity': 94},
        {'name': 'David Lee', 'school': 'Oregon', 'year': 'RS Soph', 'yards': 3412, 'tds': 30, 'rating': 161.3, 'value': 975000, 'portal_deal': None, 'similarity': 91},
        {'name': 'Tyler Martinez', 'school': 'Florida St', 'year': 'RS Soph', 'yards': 2847, 'tds': 23, 'rating': 149.8, 'value': 725000, 'portal_deal': None, 'similarity': 88},
        {'name': 'Chris Johnson', 'school': 'Penn St', 'year': 'RS Jr', 'yards': 3156, 'tds': 25, 'rating': 156.7, 'value': 900000, 'portal_deal': 875000, 'similarity': 87},
    ]
    
    for comp in comps:
        stars = "⭐" * 5 if comp['similarity'] >= 90 else "⭐" * 4
        portal_text = f"Portal Deal: ${comp['portal_deal']:,} (verified)" if comp['portal_deal'] else "Current starter"
        
        st.markdown(f"""
        <div class="comp-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="margin: 0 0 0.25rem 0;">{comp['name']} ({comp['school']}) - {comp['year']}</h4>
                    <p style="color: #64748b; margin: 0; font-size: 0.875rem;">
                        Stats: {comp['yards']:,} yds, {comp['tds']} TD, {comp['rating']} rating
                    </p>
                    <p style="margin: 0.5rem 0 0 0;">
                        <strong>Value: ${comp['value']:,}</strong> | {portal_text}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div class="similarity-stars">{stars}</div>
                    <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Similarity: {comp['similarity']}%</p>
                </div>
            </div>
            <button style="background: white; color: #667eea; border: 2px solid #667eea; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.75rem;">
                View Comparison →
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(f"""
    **Average Comp Value:** $856K (Range: $725K-$975K)  
    **Your Valuation:** $850K ✓ Within market range
    """)
    
    # INVESTMENT RECOMMENDATION
    st.markdown(f"""
    <div class="recommendation-box">
        <h3>💡 INVESTMENT RECOMMENDATION</h3>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1rem 0;">
            <div>
                <p style="color: #64748b; margin: 0; font-size: 0.875rem;">Current Investment:</p>
                <p style="font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0;">${mock_player['current_investment']:,}</p>
            </div>
            <div>
                <p style="color: #64748b; margin: 0; font-size: 0.875rem;">Market Value:</p>
                <p style="font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0;">${mock_player['market_value']:,}</p>
            </div>
        </div>
        
        <div class="recommendation-badge">
            ✅ RETAIN & INVEST - Top Retention Priority
        </div>
        
        <div style="margin-top: 1.5rem;">
            <strong>Rationale:</strong>
            <ul style="margin: 0.5rem 0; color: #64748b;">
                <li>Performing 31% above current investment</li>
                <li>Trajectory suggests $1M+ value next year</li>
                <li>Portal risk low but market would pay more</li>
                <li>Consider retention bonus: $100-150K</li>
            </ul>
            
            <strong style="margin-top: 1rem; display: block;">If He Entered Portal:</strong>
            <ul style="margin: 0.5rem 0; color: #64748b;">
                <li>Expected offers: 15-20 P4 schools</li>
                <li>Likely deal range: $800K-$950K</li>
                <li>Replacement cost: $900K-$1.2M (QB scarcity)</li>
            </ul>
        </div>
        
        <button style="background: #10b981; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 700; margin-top: 1rem; width: 100%; font-size: 1.125rem;">
            Generate Retention Strategy Report →
        </button>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 3: PERFORMANCE (Simplified for now)
# ============================================================================

with tab3:
    st.markdown("## 📊 Performance Analysis")
    st.info("Coming soon: Season progression charts, situational performance heat maps, advanced metrics, and strength of competition analysis")

# ============================================================================
# TAB 4: MARKET (Simplified for now)
# ============================================================================

with tab4:
    st.markdown("## 🌍 Market Intelligence")
    st.info("Coming soon: Positional market overview, conference comparison, transfer portal activity, and replacement cost analysis")

# ============================================================================
# TAB 5: PROJECTION (Simplified for now)
# ============================================================================

with tab5:
    st.markdown("## 🔮 Future Projections")
    st.info("Coming soon: Multi-year value trajectory, performance scenarios, NFL draft projection, and strategic recommendations")

