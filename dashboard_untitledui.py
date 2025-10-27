"""
College Football Transfer Market - UntitledUI Design System
Clean, modern interface with detailed player analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, Team, PerformanceStat, Transfer

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CFB Market Intelligence",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# UNTITLED UI DESIGN SYSTEM
# ============================================================================

# Color Palette (UntitledUI inspired)
COLORS = {
    'primary': '#7F56D9',      # Purple
    'primary_light': '#9E77ED',
    'primary_dark': '#6941C6',
    'success': '#12B76A',
    'warning': '#F79009',
    'error': '#F04438',
    'gray_50': '#F9FAFB',
    'gray_100': '#F3F4F6',
    'gray_200': '#E5E7EB',
    'gray_300': '#D1D5DB',
    'gray_400': '#9CA3AF',
    'gray_500': '#6B7280',
    'gray_600': '#4B5563',
    'gray_700': '#374151',
    'gray_800': '#1F2937',
    'gray_900': '#111827',
}

# Custom CSS - UntitledUI Design
st.markdown(f"""
<style>
    /* Global Styles */
    .main {{
        background-color: {COLORS['gray_50']};
    }}
    
    /* Typography */
    .display-xl {{
        font-size: 3.75rem;
        font-weight: 700;
        line-height: 1.2;
        color: {COLORS['gray_900']};
    }}
    
    .display-lg {{
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.2;
        color: {COLORS['gray_900']};
    }}
    
    .text-xl {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['gray_700']};
    }}
    
    .text-md {{
        font-size: 1rem;
        color: {COLORS['gray_600']};
    }}
    
    .text-sm {{
        font-size: 0.875rem;
        color: {COLORS['gray_500']};
    }}
    
    /* Cards */
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid {COLORS['gray_200']};
        transition: all 0.2s;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    .player-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        border: 1px solid {COLORS['gray_200']};
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .player-card:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 12px rgba(127, 86, 217, 0.15);
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .badge-primary {{
        background: {COLORS['primary_light']};
        color: white;
    }}
    
    .badge-success {{
        background: {COLORS['success']};
        color: white;
    }}
    
    .badge-warning {{
        background: {COLORS['warning']};
        color: white;
    }}
    
    .badge-gray {{
        background: {COLORS['gray_100']};
        color: {COLORS['gray_700']};
    }}
    
    /* Market Value Display */
    .market-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    .market-value-large {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    /* Portal Badge */
    .portal-badge {{
        background: {COLORS['warning']};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    /* Stat Bars */
    .stat-bar-container {{
        background: {COLORS['gray_100']};
        border-radius: 8px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }}
    
    .stat-bar {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_light']});
        height: 100%;
        transition: width 0.3s ease;
    }}
    
    /* Position Tags */
    .position-tag {{
        display: inline-block;
        padding: 0.375rem 0.875rem;
        background: {COLORS['gray_900']};
        color: white;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
    }}
    
    /* Score Display */
    .score-display {{
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
    }}
    
    .score-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    .score-label {{
        font-size: 0.875rem;
        color: {COLORS['gray_500']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Divider */
    .divider {{
        border-top: 1px solid {COLORS['gray_200']};
        margin: 2rem 0;
    }}
    
    /* Section Headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS['gray_900']};
        margin-bottom: 1rem;
    }}
    
    /* Team Logo Placeholder */
    .team-logo {{
        width: 48px;
        height: 48px;
        background: {COLORS['gray_200']};
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: {COLORS['gray_600']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=300)
def load_valuations():
    """Load all player valuations"""
    try:
        with open('outputs/valuations/all_valuations_2023.json', 'r') as f:
            data = json.load(f)
            return pd.DataFrame(data['valuations'])
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_portal_players():
    """Load transfer portal data"""
    session = get_session()
    transfers = session.query(Transfer).filter(
        Transfer.season == 2023,
        Transfer.to_team.is_(None)
    ).all()
    
    portal_ids = [t.player_id for t in transfers]
    return portal_ids

@st.cache_resource
def get_db_session():
    return get_session()

# ============================================================================
# PLAYER DETAIL MODAL (Using Session State)
# ============================================================================

def show_player_detail(player_data):
    """Display detailed player analysis modal"""
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <h1 style="margin: 0; color: {COLORS['gray_900']};">{player_data['player']}</h1>
                    <span class="position-tag">{player_data['position']}</span>
                </div>
                <p class="text-md" style="margin-top: 0.5rem;">{player_data['team']} • Class: {player_data.get('class_year', 'N/A')}</p>
            </div>
            <div class="market-value-large">${player_data.get('market_value', 0)/1e6:.2f}M</div>
        </div>
        
        <div class="divider"></div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 1.5rem 0;">
            <div>
                <p class="text-sm">OVERALL SCORE</p>
                <div class="score-display">
                    <span class="score-number">{player_data['total_score']/1e6:.2f}M</span>
                </div>
            </div>
            <div>
                <p class="text-sm">PERFORMANCE</p>
                <div class="score-display">
                    <span class="score-number">{player_data.get('performance_score', 0):.1f}</span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {player_data.get('performance_score', 0)}%;"></div>
                </div>
            </div>
            <div>
                <p class="text-sm">SCHEME FIT</p>
                <div class="score-display">
                    <span class="score-number">{player_data.get('scheme_fit_score', 0):.1f}</span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {player_data.get('scheme_fit_score', 0)}%;"></div>
                </div>
            </div>
            <div>
                <p class="text-sm">BRAND VALUE</p>
                <div class="score-display">
                    <span class="score-number">{player_data.get('brand_score', 0):.1f}</span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {player_data.get('brand_score', 0)}%;"></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional Details Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 class="section-header">Valuation Breakdown</h3>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Performance Score</span>
                    <span class="text-xl">${player_data.get('performance_score', 0) * 40000:.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Scheme Fit Bonus</span>
                    <span class="text-xl">${player_data.get('scheme_fit_score', 0) * 10000:.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Brand Value</span>
                    <span class="text-xl">${player_data.get('brand_score', 0) * 5000:.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Positional Multiplier</span>
                    <span class="text-xl">1.{player_data['position'][:1]}</span>
                </div>
                <div class="divider"></div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-xl" style="font-weight: 700;">Total Market Value</span>
                    <span class="market-value">${player_data.get('market_value', 0)/1e6:.2f}M</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 class="section-header">Player Profile</h3>
            <div style="margin-top: 1rem;">
                <div style="margin: 0.75rem 0;">
                    <p class="text-sm">POSITION</p>
                    <p class="text-xl">{player_data['position']}</p>
                </div>
                <div style="margin: 0.75rem 0;">
                    <p class="text-sm">TEAM</p>
                    <p class="text-xl">{player_data['team']}</p>
                </div>
                <div style="margin: 0.75rem 0;">
                    <p class="text-sm">CLASS YEAR</p>
                    <p class="text-xl">{player_data.get('class_year', 'N/A')}</p>
                </div>
                <div style="margin: 0.75rem 0;">
                    <p class="text-sm">ELIGIBILITY STATUS</p>
                    <span class="badge badge-success">Active</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.markdown(f"""
<div style="padding: 1rem 0;">
    <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">CFB Market</h1>
    <p style="color: {COLORS['gray_500']}; font-size: 0.875rem;">Transfer Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Market Overview", "👥 Player Database", "🏫 Team Rankings", "🔄 Transfer Portal", "💎 Value Opportunities"],
    label_visibility="collapsed"
)

st.sidebar.markdown(f"""
<div class="divider"></div>
<div style="padding: 1rem 0;">
    <p class="text-sm">Data updated: {datetime.now().strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

valuations_df = load_valuations()
portal_ids = load_portal_players()

# ============================================================================
# PAGE: MARKET OVERVIEW
# ============================================================================

if page == "🏠 Market Overview":
    st.markdown(f'<h1 class="display-lg">Market Overview</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Real-time intelligence on the college football transfer market</p>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if not valuations_df.empty:
        total_value = valuations_df['total_score'].sum()
        avg_value = valuations_df['total_score'].mean()
        total_players = len(valuations_df)
        portal_count = len(portal_ids)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">TOTAL MARKET VALUE</p>
                <p class="market-value">${total_value/1e9:.2f}B</p>
                <p class="text-sm">FBS Programs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">AVG PLAYER VALUE</p>
                <p class="market-value">${avg_value/1e3:.0f}K</p>
                <p class="text-sm">2023 Season</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">PLAYERS VALUED</p>
                <p class="market-value">{total_players:,}</p>
                <p class="text-sm">Across all positions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">IN TRANSFER PORTAL</p>
                <p class="market-value">{portal_count:,}</p>
                <p class="text-sm">Available players</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Position Distribution
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<h2 class="section-header">Market Value by Position</h2>', unsafe_allow_html=True)
            position_values = valuations_df.groupby('position')['total_score'].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=position_values.values / 1e6,
                y=position_values.index,
                orientation='h',
                labels={'x': 'Total Market Value ($M)', 'y': 'Position'}
            )
            fig.update_traces(marker_color=COLORS['primary'])
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        
        with col2:
            st.markdown('<h2 class="section-header">Position Stats</h2>', unsafe_allow_html=True)
            position_counts = valuations_df['position'].value_counts()
            for pos in position_counts.head(8).index:
                count = position_counts[pos]
                avg_val = valuations_df[valuations_df['position'] == pos]['total_score'].mean() / 1e3
                st.markdown(f"""
                <div style="margin: 1rem 0; padding: 1rem; background: white; border-radius: 8px; border: 1px solid {COLORS['gray_200']};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="position-tag">{pos}</span>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-weight: 700; color: {COLORS['gray_900']};">{count} players</p>
                            <p style="margin: 0; font-size: 0.75rem; color: {COLORS['gray_500']};">Avg: ${avg_val:.0f}K</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# PAGE: PLAYER DATABASE
# ============================================================================

elif page == "👥 Player Database":
    st.markdown(f'<h1 class="display-lg">Player Database</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Comprehensive player valuations and analytics</p>', unsafe_allow_html=True)
    
    if not valuations_df.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positions = ['All'] + sorted(valuations_df['position'].unique().tolist())
            selected_position = st.selectbox("Position", positions)
        
        with col2:
            teams = ['All'] + sorted(valuations_df['team'].unique().tolist())
            selected_team = st.selectbox("Team", teams)
        
        with col3:
            min_value = st.number_input("Min Value ($K)", 0, 5000, 0, step=100)
        
        with col4:
            sort_option = st.selectbox("Sort by", ["Value (High-Low)", "Value (Low-High)", "Name", "Performance"])
        
        # Apply filters
        filtered_df = valuations_df.copy()
        if selected_position != 'All':
            filtered_df = filtered_df[filtered_df['position'] == selected_position]
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['team'] == selected_team]
        if min_value > 0:
            filtered_df = filtered_df[filtered_df['total_score'] >= (min_value * 1000)]
        
        # Sort
        if sort_option == "Value (High-Low)":
            filtered_df = filtered_df.sort_values('total_score', ascending=False)
        elif sort_option == "Value (Low-High)":
            filtered_df = filtered_df.sort_values('total_score', ascending=True)
        elif sort_option == "Name":
            filtered_df = filtered_df.sort_values('player')
        else:
            filtered_df = filtered_df.sort_values('performance_score', ascending=False)
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Players Found", f"{len(filtered_df):,}")
        with col2:
            if not filtered_df.empty:
                st.metric("Avg Value", f"${filtered_df['total_score'].mean()/1e3:.0f}K")
        with col3:
            if not filtered_df.empty:
                st.metric("Total Value", f"${filtered_df['total_score'].sum()/1e6:.1f}M")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Player Cards with Click-through
        for idx, row in filtered_df.head(50).iterrows():
            in_portal = row.get('player_id') in portal_ids if 'player_id' in row else False
            
            with st.container():
                cols = st.columns([3, 1, 1, 1, 1])
                
                with cols[0]:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span class="position-tag">{row['position']}</span>
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 1.125rem; color: {COLORS['gray_900']};">{row['player']}</p>
                            <p style="margin: 0; font-size: 0.875rem; color: {COLORS['gray_500']};">{row['team']}</p>
                        </div>
                        {f'<span class="portal-badge">IN PORTAL</span>' if in_portal else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <p class="text-sm">VALUE</p>
                        <p style="font-weight: 700; font-size: 1.125rem; color: {COLORS['primary']};">${row['total_score']/1e6:.2f}M</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <p class="text-sm">PERFORMANCE</p>
                        <p style="font-weight: 700; font-size: 1.125rem;">{row.get('performance_score', 0):.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <p class="text-sm">SCHEME FIT</p>
                        <p style="font-weight: 700; font-size: 1.125rem;">{row.get('scheme_fit_score', 0):.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[4]:
                    if st.button("View Details", key=f"view_{idx}", type="primary"):
                        st.session_state.selected_player = row.to_dict()
                        st.session_state.show_player_modal = True
                
                st.markdown(f'<div style="border-bottom: 1px solid {COLORS["gray_200"]}; margin: 1rem 0;"></div>', unsafe_allow_html=True)
        
        # Show player detail modal if selected
        if st.session_state.get('show_player_modal', False):
            with st.expander("📊 Player Details", expanded=True):
                show_player_detail(st.session_state.selected_player)
                if st.button("Close"):
                    st.session_state.show_player_modal = False
                    st.rerun()

# ============================================================================
# PAGE: TEAM RANKINGS  
# ============================================================================

elif page == "🏫 Team Rankings":
    st.markdown(f'<h1 class="display-lg">Team Rankings</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Roster valuations and competitive analysis</p>', unsafe_allow_html=True)
    
    if not valuations_df.empty:
        team_values = valuations_df.groupby('team').agg({
            'total_score': ['sum', 'mean', 'count']
        }).reset_index()
        team_values.columns = ['team', 'total_value', 'avg_value', 'player_count']
        team_values = team_values.sort_values('total_value', ascending=False).reset_index(drop=True)
        
        # Top team cards
        for rank, row in team_values.head(25).iterrows():
            st.markdown(f"""
            <div class="player-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1.5rem;">
                        <div style="font-size: 2rem; font-weight: 700; color: {COLORS['gray_400']}; min-width: 3rem;">
                            #{rank + 1}
                        </div>
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 1.25rem; color: {COLORS['gray_900']};">{row['team']}</p>
                            <p style="margin: 0; font-size: 0.875rem; color: {COLORS['gray_500']};">{int(row['player_count'])} valued players</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 2rem; align-items: center;">
                        <div style="text-align: right;">
                            <p class="text-sm">TOTAL VALUE</p>
                            <p class="market-value">${row['total_value']/1e6:.1f}M</p>
                        </div>
                        <div style="text-align: right;">
                            <p class="text-sm">AVG PLAYER</p>
                            <p style="font-weight: 700; font-size: 1.25rem; color: {COLORS['gray_700']};">${row['avg_value']/1e3:.0f}K</p>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PAGE: TRANSFER PORTAL
# ============================================================================

elif page == "🔄 Transfer Portal":
    st.markdown(f'<h1 class="display-lg">Transfer Portal</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Available players and market opportunities</p>', unsafe_allow_html=True)
    
    if not valuations_df.empty and portal_ids:
        portal_players = valuations_df[valuations_df.index.isin(portal_ids)]
        
        st.metric("Available Players", f"{len(portal_players):,}")
        
        for idx, row in portal_players.head(30).iterrows():
            st.markdown(f"""
            <div class="player-card" style="border-left: 4px solid {COLORS['warning']};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span class="portal-badge">AVAILABLE</span>
                        <span class="position-tag">{row['position']}</span>
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 1.125rem;">{row['player']}</p>
                            <p style="margin: 0; font-size: 0.875rem; color: {COLORS['gray_500']};">From: {row['team']}</p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <p class="market-value">${row['total_score']/1e6:.2f}M</p>
                        <p style="font-size: 0.875rem; color: {COLORS['gray_500']};">
                            Performance: {row.get('performance_score', 0):.0f} | 
                            Fit: {row.get('scheme_fit_score', 0):.0f}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PAGE: VALUE OPPORTUNITIES
# ============================================================================

elif page == "💎 Value Opportunities":
    st.markdown(f'<h1 class="display-lg">Value Opportunities</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Undervalued players with high potential</p>', unsafe_allow_html=True)
    
    if not valuations_df.empty:
        # Calculate value efficiency
        valuations_df['efficiency'] = valuations_df['performance_score'] / (valuations_df['total_score'] / 1e6)
        
        gems = valuations_df[
            (valuations_df['performance_score'] > 60) &
            (valuations_df['total_score'] < 1000000)
        ].sort_values('efficiency', ascending=False)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Opportunities Found", f"{len(gems):,}")
        with col2:
            if not gems.empty:
                st.metric("Avg Performance", f"{gems['performance_score'].mean():.1f}")
        with col3:
            if not gems.empty:
                st.metric("Avg Value", f"${gems['total_score'].mean()/1e3:.0f}K")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        for idx, row in gems.head(40).iterrows():
            in_portal = idx in portal_ids
            
            st.markdown(f"""
            <div class="player-card" style="border-left: 4px solid {COLORS['success']};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span class="badge badge-success">VALUE</span>
                        <span class="position-tag">{row['position']}</span>
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 1.125rem;">{row['player']}</p>
                            <p style="margin: 0; font-size: 0.875rem; color: {COLORS['gray_500']};">{row['team']}</p>
                        </div>
                        {f'<span class="portal-badge">IN PORTAL</span>' if in_portal else ''}
                    </div>
                    <div style="text-align: right;">
                        <p style="font-weight: 700; font-size: 1.5rem; color: {COLORS['success']};">${row['total_score']/1e6:.2f}M</p>
                        <p style="font-size: 0.875rem; color: {COLORS['gray_500']};">
                            Performance: {row['performance_score']:.1f} | 
                            Efficiency: {row['efficiency']:.1f}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="margin-top: 4rem; padding: 2rem 0; border-top: 1px solid {COLORS['gray_200']}; text-align: center;">
    <p style="color: {COLORS['gray_500']}; font-size: 0.875rem;">
        CFB Market Intelligence Platform • Data updated {datetime.now().strftime('%B %d, %Y')}
    </p>
</div>
""", unsafe_allow_html=True)

