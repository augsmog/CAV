"""
CAV Executive Dashboard - Level 1: Portfolio Overview
Executive Summary First, Details on Demand
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import numpy as np

# Page config
st.set_page_config(
    page_title="CAV - College Athlete Valuation",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# STYLING - Executive-Grade UI
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        height: 100%;
    }
    
    .kpi-label {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .kpi-meta {
        color: #64748b;
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
    }
    
    .kpi-trend-up {
        color: #10b981;
        font-weight: 600;
    }
    
    .kpi-trend-down {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Alert Cards */
    .alert-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .alert-critical {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    
    .alert-warning {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .alert-success {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    /* Player Bubble */
    .player-bubble {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: all 0.2s;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .player-bubble:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.2);
        border-color: #667eea;
    }
    
    /* Sport Switcher */
    .sport-switcher {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .sport-btn {
        flex: 1;
        padding: 0.75rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        background: white;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .sport-btn-active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
    }
    
    .sport-btn:hover {
        border-color: #667eea;
    }
    
    /* Position Tag */
    .position-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* Value Badge */
    .value-good {
        color: #10b981;
        font-weight: 700;
    }
    
    .value-fair {
        color: #3b82f6;
        font-weight: 700;
    }
    
    .value-premium {
        color: #f59e0b;
        font-weight: 700;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE & SPORT SWITCHER
# ============================================================================

if 'sport' not in st.session_state:
    st.session_state.sport = 'football'

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'portfolio'  # portfolio, position, player, market

if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

if 'selected_position' not in st.session_state:
    st.session_state.selected_position = None

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_valuations(sport='football'):
    """Load valuation data"""
    if sport == 'football':
        file_path = Path('outputs/valuations/all_football_valuations_2023.json')
    else:
        file_path = Path('outputs/valuations/all_basketball_valuations_2023.json')
    
    if not file_path.exists():
        return pd.DataFrame()
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Ensure we have the right value column
    if 'player_value' in df.columns:
        df['total_value'] = df['player_value']
    elif 'total_score' in df.columns:
        df['total_value'] = df['total_score']
    
    return df

@st.cache_data
def load_nil_budgets():
    """Load NIL budget data"""
    # For now, return sample data matching what we showed in the NIL sources page
    return pd.DataFrame([
        {'school': 'Alabama', 'conference': 'SEC', 'nil_budget': 25000000, 'avg_player': 294117},
        {'school': 'Georgia', 'conference': 'SEC', 'nil_budget': 24500000, 'avg_player': 288235},
        {'school': 'Texas', 'conference': 'SEC', 'nil_budget': 23000000, 'avg_player': 270588},
        {'school': 'Ohio State', 'conference': 'Big Ten', 'nil_budget': 22500000, 'avg_player': 264706},
        {'school': 'Michigan', 'conference': 'Big Ten', 'nil_budget': 20000000, 'avg_player': 235294},
        {'school': 'LSU', 'conference': 'SEC', 'nil_budget': 19500000, 'avg_player': 229412},
        {'school': 'USC', 'conference': 'Big Ten', 'nil_budget': 19000000, 'avg_player': 223529},
        {'school': 'Texas A&M', 'conference': 'SEC', 'nil_budget': 18500000, 'avg_player': 217647},
        {'school': 'Oregon', 'conference': 'Big Ten', 'nil_budget': 18000000, 'avg_player': 211765},
        {'school': 'Florida', 'conference': 'SEC', 'nil_budget': 17500000, 'avg_player': 205882},
    ])

# Load data
current_sport = st.session_state.sport
df = load_valuations(current_sport)
nil_budgets = load_nil_budgets()

# ============================================================================
# HEADER WITH SPORT SWITCHER
# ============================================================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏈 2024-25 {current_sport.title()} Roster</h1>
        <p>College Athlete Valuation - Executive Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("⚽ Switch to Basketball" if current_sport == 'football' else "🏈 Switch to Football", 
                 use_container_width=True):
        st.session_state.sport = 'basketball' if current_sport == 'football' else 'football'
        st.rerun()

with col3:
    if st.button("📊 NIL Budget Sources", use_container_width=True):
        st.switch_page("dashboard_nil_sources.py")

# ============================================================================
# NAVIGATION
# ============================================================================

nav_cols = st.columns(4)
views = ['Portfolio Overview', 'Position Groups', 'Transfer Portal', 'Scenario Planner']
icons = ['📊', '👥', '🔄', '🎯']

for i, (col, view, icon) in enumerate(zip(nav_cols, views, icons)):
    with col:
        if st.button(f"{icon} {view}", use_container_width=True, 
                     type="primary" if i == 0 else "secondary"):
            if i == 0:
                st.session_state.current_view = 'portfolio'
            elif i == 1:
                st.session_state.current_view = 'position'
            elif i == 2:
                st.session_state.current_view = 'market'
            elif i == 3:
                st.session_state.current_view = 'scenario'

st.markdown("---")

# ============================================================================
# LEVEL 1: PORTFOLIO OVERVIEW
# ============================================================================

if st.session_state.current_view == 'portfolio':
    
    # Calculate key metrics
    if not df.empty:
        total_value = df['total_value'].sum()
        avg_value = df['total_value'].mean()
        num_players = len(df)
        
        # Top position by value
        if 'position' in df.columns:
            pos_value = df.groupby('position')['total_value'].sum()
            top_position = pos_value.idxmax()
            top_pos_value = pos_value.max()
            top_pos_count = len(df[df['position'] == top_position])
        else:
            top_position = "QB"
            top_pos_value = 0
            top_pos_count = 0
        
        # Market efficiency score (mock for now)
        efficiency_score = 87
        
        # 🎯 KEY INSIGHTS (Top Banner)
        st.markdown('<h2 class="section-header">🎯 Key Insights</h2>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Total Roster Value</p>
                <p class="kpi-value">${total_value/1e6:.1f}M</p>
                <p class="kpi-meta">
                    <span class="kpi-trend-up">▲ $1.2M YoY</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Avg Player Value</p>
                <p class="kpi-value">${avg_value/1000:.0f}K</p>
                <p class="kpi-meta">
                    <span class="kpi-trend-up">+12% vs conf avg</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Most Valuable Position</p>
                <p class="kpi-value">{top_position}</p>
                <p class="kpi-meta">
                    ${top_pos_value/1e6:.1f}M • {top_pos_count} players
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-label">Market Efficiency</p>
                <p class="kpi-value">{efficiency_score}/100</p>
                <p class="kpi-meta">
                    Top 15% nationally
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 📊 ROSTER VALUE BREAKDOWN
        st.markdown('<h2 class="section-header">📊 Roster Value Breakdown</h2>', unsafe_allow_html=True)
        
        # Create bubble chart
        if 'position' in df.columns:
            # Add value category for coloring
            df['value_category'] = pd.cut(
                df['total_value'],
                bins=[0, 100000, 300000, 500000, float('inf')],
                labels=['Developing', 'Solid Contributor', 'High Value', 'Elite']
            )
            
            fig = px.scatter(
                df.head(50),  # Top 50 players
                x='position',
                y='total_value',
                size='total_value',
                color='value_category',
                hover_data={'name': True, 'total_value': ':$,.0f', 'position': True},
                title='Player Values by Position (Bubble size = value)',
                color_discrete_map={
                    'Developing': '#94a3b8',
                    'Solid Contributor': '#3b82f6',
                    'High Value': '#10b981',
                    'Elite': '#8b5cf6'
                },
                height=500
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                font=dict(family='Inter'),
                xaxis_title='Position',
                yaxis_title='Market Value ($)',
                yaxis_tickformat='$,.0f',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 📈 VALUE DISTRIBUTION & BENCHMARKING
        st.markdown('<h2 class="section-header">📈 Value Distribution & Benchmarking</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Value by Position**")
            if 'position' in df.columns:
                pos_values = df.groupby('position')['total_value'].sum().sort_values(ascending=True)
                
                fig2 = go.Figure(go.Bar(
                    x=pos_values.values,
                    y=pos_values.index,
                    orientation='h',
                    marker=dict(
                        color=pos_values.values,
                        colorscale='Purples',
                        showscale=False
                    ),
                    text=[f'${v/1e6:.1f}M' for v in pos_values.values],
                    textposition='outside'
                ))
                
                fig2.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    font=dict(family='Inter'),
                    xaxis_title='Total Value ($)',
                    xaxis_tickformat='$,.0f',
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.markdown("**Conference Comparison**")
            
            # Create gauge chart
            your_value = total_value
            conf_median = 11.2e6  # Mock SEC median
            
            percentile = 60  # Mock percentile
            
            fig3 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=your_value/1e6,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Your Roster: ${your_value/1e6:.1f}M<br>6th of 16 in SEC"},
                delta={'reference': conf_median/1e6, 'suffix': 'M'},
                gauge={
                    'axis': {'range': [None, 25]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, conf_median/1e6], 'color': "lightgray"},
                        {'range': [conf_median/1e6, 25], 'color': "whitesmoke"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': conf_median/1e6
                    }
                }
            ))
            
            fig3.update_layout(
                height=400,
                font=dict(family='Inter', size=12),
                margin=dict(l=20, r=20, t=0, b=0)
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # ⚠️ ALERTS & RECOMMENDED ACTIONS
        st.markdown('<h2 class="section-header">⚠️ Alerts & Recommended Actions</h2>', unsafe_allow_html=True)
        
        # Critical alerts
        st.markdown("""
        <div class="alert-card alert-critical">
            <div>
                <strong>🔴 Portal Risk:</strong> 3 players likely to enter portal (60%+ probability)
            </div>
            <div>
                <button style="background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600;">
                    View Details →
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Warning alerts
        st.markdown("""
        <div class="alert-card alert-warning">
            <div>
                <strong>🟡 Position Gap:</strong> Only 1 starting-caliber LT on roster
            </div>
            <div>
                <button style="background: #f59e0b; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600;">
                    See Portal Options →
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Success alerts
        st.markdown("""
        <div class="alert-card alert-success">
            <div>
                <strong>🟢 Value Opportunity:</strong> 2 undervalued sophomores performing above investment
            </div>
            <div>
                <button style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600;">
                    Investment Recs →
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show top players table
        st.markdown('<h2 class="section-header">🏆 Top 20 Players by Value</h2>', unsafe_allow_html=True)
        
        if not df.empty:
            top_players = df.nlargest(20, 'total_value')[['name', 'position', 'team', 'total_value']].copy()
            top_players['total_value'] = top_players['total_value'].apply(lambda x: f'${x:,.0f}')
            top_players.columns = ['Player', 'Position', 'Team', 'Market Value']
            
            st.dataframe(
                top_players,
                use_container_width=True,
                hide_index=True,
                height=600
            )
    
    else:
        st.warning("No valuation data available. Please run the valuation models first.")

# ============================================================================
# Add other views (Position, Market, Scenario) - stubs for now
# ============================================================================

elif st.session_state.current_view == 'position':
    st.markdown('<h2 class="section-header">👥 Position Group Analysis</h2>', unsafe_allow_html=True)
    st.info("Coming soon: Deep dive into position groups with player cards and analytics")

elif st.session_state.current_view == 'market':
    st.markdown('<h2 class="section-header">🔄 Transfer Portal Market</h2>', unsafe_allow_html=True)
    st.info("Coming soon: Portal dashboard with recommended targets and market intelligence")

elif st.session_state.current_view == 'scenario':
    st.markdown('<h2 class="section-header">🎯 Scenario Planner</h2>', unsafe_allow_html=True)
    st.info("Coming soon: 'What if' analysis tool for roster planning")

