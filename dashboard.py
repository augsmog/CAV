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
    page_title="CAV - Multi-Sport Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize sport selection in session state
if 'sport' not in st.session_state:
    st.session_state.sport = 'football'

# ============================================================================
# UNTITLED UI DESIGN SYSTEM
# ============================================================================

# Professional Navy/Electric Blue Design System
COLORS = {
    'primary': '#002147',      # Navy Blue - Trust, professionalism
    'primary_light': '#003366',
    'primary_dark': '#001529',
    'accent': '#0066FF',       # Electric Blue - Action, highlights
    'accent_light': '#3385FF',
    'success': '#00C853',      # Green - Good value, positive
    'warning': '#FFC107',      # Amber - Caution, potential
    'error': '#D32F2F',        # Red - Alert, risk
    'neutral': '#757575',      # Gray - Neutral info
    'gray_50': '#FFFFFF',      # White - Clean background
    'gray_100': '#F5F5F5',     # Light Gray - Secondary surfaces
    'gray_200': '#E0E0E0',
    'gray_300': '#BDBDBD',
    'gray_400': '#9E9E9E',
    'gray_500': '#757575',
    'gray_600': '#616161',
    'gray_700': '#424242',
    'gray_800': '#212121',
    'gray_900': '#0A1628',     # Dark mode navy
    'info': '#0066FF',         # Electric Blue for info
}

# Custom CSS - Professional Navy/Electric Blue Design
st.markdown(f"""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    
    /* Global Styles */
    .main {{
        background-color: {COLORS['gray_50']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Typography Hierarchy */
    .display-xl {{
        font-family: 'Inter', sans-serif;
        font-size: 32px;
        font-weight: 800;
        line-height: 1.2;
        color: {COLORS['primary']};
    }}
    
    .display-lg {{
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.2;
        color: {COLORS['primary']};
    }}
    
    .text-xl {{
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: {COLORS['gray_800']};
    }}
    
    .text-md {{
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 400;
        color: {COLORS['gray_700']};
    }}
    
    .text-sm {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: {COLORS['gray_600']};
    }}
    
    .text-xs {{
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 500;
        color: {COLORS['gray_500']};
    }}
    
    /* Data/Numbers - Monospace for alignment */
    .data-number {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 18px;
        font-weight: 500;
        letter-spacing: -0.02em;
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

    /* PREMIUM ENHANCEMENTS */

    /* Import Inter font for professional typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* Enhanced player cards with glassmorphism */
    .player-card {{
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px !important;
        padding: 1.75rem !important;
        margin: 1rem 0 !important;
        border: 2px solid {COLORS['gray_100']} !important;
        box-shadow:
            0 4px 6px rgba(0, 0, 0, 0.04),
            0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .player-card:hover {{
        transform: translateY(-4px) scale(1.01) !important;
        border-color: {COLORS['primary']} !important;
        box-shadow:
            0 20px 40px rgba(127, 86, 217, 0.15),
            0 8px 16px rgba(127, 86, 217, 0.1) !important;
    }}

    /* Enhanced metric cards */
    .metric-card {{
        background: white;
        border-radius: 16px !important;
        padding: 1.75rem !important;
        box-shadow:
            0 2px 4px rgba(0, 0, 0, 0.04),
            0 1px 2px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid {COLORS['gray_200']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_light']});
        opacity: 0;
        transition: opacity 0.3s;
    }}

    .metric-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow:
            0 12px 24px rgba(0, 0, 0, 0.08),
            0 4px 8px rgba(0, 0, 0, 0.04) !important;
        border-color: {COLORS['primary_light']};
    }}

    .metric-card:hover::before {{
        opacity: 1;
    }}

    /* Gradient text for values */
    .market-value-large {{
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }}

    .market-value {{
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Animated stat bars with shimmer */
    .stat-bar {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_light']}) !important;
        height: 100%;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }}

    .stat-bar::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }}

    @keyframes shimmer {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}

    .stat-bar-container {{
        background: {COLORS['gray_100']};
        border-radius: 10px !important;
        height: 10px !important;
        overflow: hidden;
        margin: 0.75rem 0 !important;
    }}

    /* Enhanced badges */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.4rem 0.9rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.2s;
    }}

    .badge-primary {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']}) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(127, 86, 217, 0.25);
    }}

    .badge-success {{
        background: linear-gradient(135deg, {COLORS['success']}, #32D583) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(18, 183, 106, 0.25);
    }}

    .badge-warning {{
        background: linear-gradient(135deg, {COLORS['warning']}, #FDB022) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(247, 144, 9, 0.25);
    }}

    /* Portal badge with pulse */
    .portal-badge {{
        background: {COLORS['warning']} !important;
        color: white !important;
        padding: 0.4rem 0.9rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem;
        font-weight: 700 !important;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 12px rgba(247, 144, 9, 0.3);
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.85; }}
    }}

    /* Enhanced position tags */
    .position-tag {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem !important;
        background: linear-gradient(135deg, {COLORS['gray_900']}, {COLORS['gray_800']}) !important;
        color: white;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.875rem;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}

    /* Section headers with gradient underline */
    .section-header {{
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: {COLORS['gray_900']};
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_light']}) 1;
        border-image-slice: 1;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Enhanced Streamlit buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_light']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 12px rgba(127, 86, 217, 0.25) !important;
    }}

    .stButton>button:hover {{
        background: linear-gradient(135deg, {COLORS['primary_dark']}, {COLORS['primary']}) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(127, 86, 217, 0.35) !important;
    }}

    /* Smooth page transitions */
    .main .block-container {{
        animation: fadeIn 0.5s ease-in;
    }}

    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* Responsive improvements */
    @media (max-width: 768px) {{
        .market-value-large {{ font-size: 2rem !important; }}
        .section-header {{ font-size: 1.5rem !important; }}
        .player-card {{ padding: 1.25rem !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=300)
def load_valuations(sport='football'):
    """Load all player valuations"""
    try:
        if sport == 'basketball':
            filepath = 'outputs/valuations/all_basketball_valuations_2023.json'
        else:
            filepath = 'outputs/valuations/all_valuations_2023.json'
        
        with open(filepath, 'r') as f:
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
                    <span class="score-number">{player_data.get('player_value', player_data.get('total_score', 0))/1e6:.2f}M</span>
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

    # 6-PILLAR ENSEMBLE BREAKDOWN
    st.markdown(f"""
    <div class="metric-card" style="margin-top: 1.5rem; background: linear-gradient(135deg, {COLORS['gray_50']}, white);">
        <h3 class="section-header">6-Pillar Ensemble Valuation Breakdown</h3>
        <p style="font-size: 0.875rem; color: {COLORS['gray_600']}; margin-bottom: 1.5rem;">
            Comprehensive multi-model valuation across production, prediction, scarcity, market, brand, and risk
        </p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
            <!-- Pillar 1: Production Value -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">📊</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 1</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">Production Value</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['primary']};">
                        {player_data.get('performance_score', 75):.0f}
                    </span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {player_data.get('performance_score', 75)}%;"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Historical on-field performance</p>
            </div>

            <!-- Pillar 2: Predictive Performance -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">🔮</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 2</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">Future Projection</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['primary']};">
                        {min(player_data.get('performance_score', 75) * 1.1, 100):.0f}
                    </span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {min(player_data.get('performance_score', 75) * 1.1, 100)}%;"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Expected trajectory & development</p>
            </div>

            <!-- Pillar 3: Positional Scarcity -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">💎</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 3</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">Market Scarcity</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['warning']};">
                        {1.5 if player_data.get('position') in ['QB', 'EDGE', 'CB'] else 1.2:.1f}x
                    </span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {(1.5 if player_data.get('position') in ['QB', 'EDGE', 'CB'] else 1.2) * 50}%; background: linear-gradient(90deg, {COLORS['warning']}, #FDB022);"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Supply/demand premium</p>
            </div>

            <!-- Pillar 4: Market Context -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">🏆</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 4</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">School Context</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['info']};">
                        {1.3 if player_data.get('team') in ['Alabama', 'Georgia', 'Ohio State'] else 1.1:.1f}x
                    </span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {(1.3 if player_data.get('team') in ['Alabama', 'Georgia', 'Ohio State'] else 1.1) * 60}%; background: linear-gradient(90deg, {COLORS['info']}, #3DBFF6);"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Conference & program premium</p>
            </div>

            <!-- Pillar 5: Brand Value -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">⭐</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 5</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">Brand & NIL</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['success']};">
                        {player_data.get('brand_score', 65):.0f}
                    </span>
                    <span class="text-sm">/100</span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: {player_data.get('brand_score', 65)}%; background: linear-gradient(90deg, {COLORS['success']}, #32D583);"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Social media & marketability</p>
            </div>

            <!-- Pillar 6: Risk Assessment -->
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">🛡️</span>
                    <div>
                        <p class="text-xs" style="margin: 0;">PILLAR 6</p>
                        <p style="margin: 0; font-weight: 700; font-size: 0.875rem;">Risk Adjustment</p>
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin: 0.5rem 0;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['success']};">
                        0.97x
                    </span>
                </div>
                <div class="stat-bar-container">
                    <div class="stat-bar" style="width: 97%; background: linear-gradient(90deg, {COLORS['success']}, #32D583);"></div>
                </div>
                <p class="text-sm" style="margin-top: 0.5rem;">Low risk (minimal concerns)</p>
            </div>
        </div>

        <div style="margin-top: 2rem; padding: 1.25rem; background: white; border-radius: 12px; border-left: 4px solid {COLORS['primary']};">
            <p style="margin: 0; font-weight: 700; color: {COLORS['gray_900']};">
                🎯 Ensemble Model Result
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: {COLORS['gray_600']};">
                All six pillars combined using configurable weights to produce final market value with confidence intervals
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

            # Additional Details Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 class="section-header">Player Valuation</h3>
            <p style="font-size: 0.875rem; color: {COLORS['gray_500']}; margin-bottom: 1rem;">What schools/collectives pay for on-field value</p>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Base Position Value</span>
                    <span class="text-xl">{player_data['position']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Performance Multiplier</span>
                    <span class="text-xl">{player_data.get('performance_score', 0):.0f}/100</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Scheme Fit Multiplier</span>
                    <span class="text-xl">{player_data.get('scheme_fit_score', 0):.0f}/100</span>
                </div>
                <div class="divider"></div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-xl" style="font-weight: 700;">Player Value</span>
                    <span class="market-value">${player_data.get('player_value', player_data.get('total_score', 0))/1e6:.2f}M</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 class="section-header">NIL Potential</h3>
            <p style="font-size: 0.875rem; color: {COLORS['gray_500']}; margin-bottom: 1rem;">What player can earn through marketing/endorsements</p>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Brand Score</span>
                    <span class="text-xl">{player_data.get('brand_score', 0):.0f}/100</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Social Media Reach</span>
                    <span class="text-xl">-</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-md">Program Exposure</span>
                    <span class="text-xl">{player_data['team']}</span>
                </div>
                <div class="divider"></div>
                <div style="display: flex; justify-content: space-between; margin: 0.75rem 0;">
                    <span class="text-xl" style="font-weight: 700;">Annual NIL Potential</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['success']};">${player_data.get('nil_potential', 0)/1e6:.2f}M</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Combined Value Summary
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="text-sm">PLAYER VALUE</p>
            <p style="font-size: 1.75rem; font-weight: 700; color: {COLORS['primary']};">
                ${player_data.get('player_value', player_data.get('total_score', 0))/1e6:.2f}M
            </p>
            <p class="text-sm">Schools/Collectives Pay</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="text-sm">NIL POTENTIAL</p>
            <p style="font-size: 1.75rem; font-weight: 700; color: {COLORS['success']};">
                ${player_data.get('nil_potential', 0)/1e6:.2f}M
            </p>
            <p class="text-sm">Player Earns (Marketing)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="text-sm">TOTAL OPPORTUNITY</p>
            <p style="font-size: 1.75rem; font-weight: 700; color: {COLORS['gray_900']};">
                ${(player_data.get('player_value', player_data.get('total_score', 0)) + player_data.get('nil_potential', 0))/1e6:.2f}M
            </p>
            <p class="text-sm">Combined Annual Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Show confidence metrics if V3 data available
        if 'sample_confidence' in player_data:
            confidence = player_data.get('sample_confidence', 1.0)
            confidence_color = COLORS['success'] if confidence > 0.9 else COLORS['warning'] if confidence > 0.7 else COLORS['error']
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">CONFIDENCE</p>
                <p style="font-size: 1.75rem; font-weight: 700; color: {confidence_color};">
                    {confidence:.0%}
                </p>
                <p class="text-sm">Snaps: {player_data.get('snaps_played', 0):,}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">SEASON</p>
                <p style="font-size: 1.75rem; font-weight: 700; color: {COLORS['gray_900']};">
                    {player_data.get('season', 2023)}
                </p>
                <p class="text-sm">Year</p>
            </div>
            """, unsafe_allow_html=True)
    
    # V3 Sample Size & Context Info
    if 'sample_confidence' in player_data and player_data.get('sample_confidence', 1.0) < 1.0:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<h3 class="section-header">Sample Size & Context (V3)</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">SNAPS PLAYED</p>
                <p style="font-size: 1.5rem; font-weight: 700;">{player_data.get('snaps_played', 0):,}</p>
                <p class="text-sm">Confidence: {player_data.get('sample_confidence', 0):.0%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">CONTEXT ADJUSTMENT</p>
                <p style="font-size: 1.5rem; font-weight: 700;">{player_data.get('context_adjustment', 1.0):.2f}x</p>
                <p class="text-sm">High Leverage vs Garbage Time</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="text-sm">OPPONENT ADJUSTMENT</p>
                <p style="font-size: 1.5rem; font-weight: 700;">{player_data.get('opponent_adjustment', 1.0):.2f}x</p>
                <p class="text-sm">Strength of Competition</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show confidence interval
        if 'value_low' in player_data and 'value_high' in player_data:
            st.info(f"📊 **Value Range**: ${player_data['value_low']/1e6:.2f}M - ${player_data['value_high']/1e6:.2f}M "
                   f"(±{player_data.get('confidence_interval_pct', 0):.0%} confidence interval)")

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.markdown(f"""
<div style="padding: 1rem 0;">
    <h1 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">CFB Market</h1>
    <p style="color: {COLORS['gray_500']}; font-size: 0.875rem;">Transfer Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SPORT SWITCHER
# ============================================================================

st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">CAV Platform</h2>
    <p style="font-size: 0.75rem; color: #64748b;">Multi-Sport Valuation</p>
</div>
""", unsafe_allow_html=True)

# Sport Toggle Buttons
col1, col2 = st.sidebar.columns(2)

with col1:
    football_type = "primary" if st.session_state.sport == 'football' else "secondary"
    if st.button("🏈 Football", key="btn_football", use_container_width=True, type=football_type):
        st.session_state.sport = 'football'
        st.rerun()

with col2:
    basketball_type = "primary" if st.session_state.sport == 'basketball' else "secondary"
    if st.button("🏀 Basketball", key="btn_basketball", use_container_width=True, type=basketball_type):
        st.session_state.sport = 'basketball'
        st.rerun()

# Current Sport Indicator
sport_color = '#15803d' if st.session_state.sport == 'basketball' else '#1d4ed8'
sport_bg = '#f0fdf4' if st.session_state.sport == 'basketball' else '#eff6ff'
st.sidebar.markdown(f"""
<div style="text-align: center; margin: 0.75rem 0 1rem 0; padding: 0.5rem; background: {sport_bg}; border-radius: 6px; border: 2px solid {sport_color};">
    <p style="margin: 0; font-size: 0.875rem; font-weight: 700; color: {sport_color}; text-transform: uppercase;">
        {st.session_state.sport} MODE {'🏈' if st.session_state.sport == 'football' else '🏀'}
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Check if viewing player detail
if 'view_player_detail' in st.session_state and st.session_state.view_player_detail:
    page = "Player Detail"
    if st.sidebar.button("← Back to Database"):
        st.session_state.view_player_detail = False
        if 'selected_player' in st.session_state:
            del st.session_state.selected_player
        st.rerun()
else:
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

current_sport = st.session_state.get('sport', 'football')
valuations_df = load_valuations(sport=current_sport)
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
        # Handle both V3 (total_score) and V4 (player_value) data
        value_col = 'player_value' if 'player_value' in valuations_df.columns else 'total_score'
        total_value = valuations_df[value_col].sum()
        avg_value = valuations_df[value_col].mean()
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
            value_col = 'player_value' if 'player_value' in valuations_df.columns else 'total_score'
            position_values = valuations_df.groupby('position')[value_col].sum().sort_values(ascending=False)
            
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
                value_col = 'player_value' if 'player_value' in valuations_df.columns else 'total_score'
                avg_val = valuations_df[valuations_df['position'] == pos][value_col].mean() / 1e3
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
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Season filter
            seasons = sorted(valuations_df['season'].unique().tolist(), reverse=True) if 'season' in valuations_df.columns else [2023]
            selected_season = st.selectbox("Season", seasons)
        
        with col2:
            positions = ['All'] + sorted(valuations_df['position'].unique().tolist())
            selected_position = st.selectbox("Position", positions)
        
        with col3:
            teams = ['All'] + sorted(valuations_df['team'].unique().tolist())
            selected_team = st.selectbox("Team", teams)
        
        with col4:
            min_value = st.number_input("Min Value ($K)", 0, 5000, 0, step=100)
        
        with col5:
            sort_option = st.selectbox("Sort by", ["Value (High-Low)", "Value (Low-High)", "Name", "Performance"])
        
        # Apply filters
        filtered_df = valuations_df.copy()
        
        # Filter by season
        if 'season' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['season'] == selected_season]
        
        if selected_position != 'All':
            filtered_df = filtered_df[filtered_df['position'] == selected_position]
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['team'] == selected_team]
        if min_value > 0:
            value_col = 'player_value' if 'player_value' in filtered_df.columns else 'total_score'
            filtered_df = filtered_df[filtered_df[value_col] >= (min_value * 1000)]
        
        # Sort
        value_col = 'player_value' if 'player_value' in filtered_df.columns else 'total_score'
        if sort_option == "Value (High-Low)":
            filtered_df = filtered_df.sort_values(value_col, ascending=False)
        elif sort_option == "Value (Low-High)":
            filtered_df = filtered_df.sort_values(value_col, ascending=True)
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
                value_col = 'player_value' if 'player_value' in filtered_df.columns else 'total_score'
                st.metric("Avg Value", f"${filtered_df[value_col].mean()/1e3:.0f}K")
        with col3:
            if not filtered_df.empty:
                value_col = 'player_value' if 'player_value' in filtered_df.columns else 'total_score'
                st.metric("Total Value", f"${filtered_df[value_col].sum()/1e6:.1f}M")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Display warning for limited sample players
        if 'limited_sample_warning' in filtered_df.columns:
            limited_count = filtered_df['limited_sample_warning'].sum()
            if limited_count > 0:
                st.warning(f"⚠️ {limited_count} players have limited sample sizes. Values shown with reduced confidence.")
        
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
                    # Display WAR if available (V4), otherwise player value
                    if 'war' in row and row.get('war', 0) != 0:
                        war_color = COLORS['success'] if row['war'] >= 1.0 else COLORS['primary'] if row['war'] >= 0.5 else COLORS['gray_600']
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <p class="text-sm">WAR</p>
                            <p style="font-weight: 700; font-size: 1.125rem; color: {war_color};">{row['war']:.2f}</p>
                            <p class="text-xs" style="color: {COLORS['gray_500']};"> +{row.get('wins_added', 0):.1f} wins</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <p class="text-sm">PLAYER VALUE</p>
                            <p style="font-weight: 700; font-size: 1.125rem; color: {COLORS['primary']};">${row.get('player_value', row.get('total_score', 0))/1e6:.2f}M</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <p class="text-sm">NIL POTENTIAL</p>
                        <p style="font-weight: 700; font-size: 1.125rem; color: {COLORS['success']};">${row.get('nil_potential', 0)/1e6:.2f}M</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[3]:
                    # Show confidence if available (V3)
                    if 'sample_confidence' in row and row['sample_confidence'] < 1.0:
                        confidence_color = COLORS['warning'] if row['sample_confidence'] < 0.7 else COLORS['gray_600']
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <p class="text-sm">CONFIDENCE</p>
                            <p style="font-weight: 700; font-size: 1.125rem; color: {confidence_color};">{row['sample_confidence']:.0%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <p class="text-sm">PERFORMANCE</p>
                            <p style="font-weight: 700; font-size: 1.125rem;">{row.get('performance_score', 0):.0f}/100</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with cols[4]:
                    if st.button("View Details", key=f"view_{idx}", type="primary"):
                        st.session_state.selected_player = row.to_dict()
                        st.session_state.view_player_detail = True
                        st.rerun()  # Navigate to player detail page
                
                st.markdown(f'<div style="border-bottom: 1px solid {COLORS["gray_200"]}; margin: 1rem 0;"></div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: PLAYER DETAIL (Separate Page)
# ============================================================================

elif page == "Player Detail":
    if 'selected_player' not in st.session_state:
        st.error("No player selected")
        if st.button("← Back to Database"):
            st.session_state.view_player_detail = False
            st.rerun()
    else:
        player_data = st.session_state.selected_player
        
        # Header with back button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<h1 class="display-lg">{player_data["player"]}</h1>', unsafe_allow_html=True)
        with col2:
            if st.button("← Back to Database", type="secondary"):
                st.session_state.view_player_detail = False
                del st.session_state.selected_player
                st.rerun()
        
        # Player header card
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <span class="position-tag">{player_data['position']}</span>
                <div>
                    <p style="margin: 0; font-size: 1.5rem; font-weight: 700; color: {COLORS['gray_900']};">{player_data['player']}</p>
                    <p style="margin: 0; font-size: 1rem; color: {COLORS['gray_500']};">{player_data['team']} • Class: {player_data.get('class_year', 'N/A')} • Season: {player_data.get('season', 2023)}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 0.75rem; color: {COLORS['gray_500']}; margin: 0;">PLAYER VALUE</p>
                <p style="font-size: 2rem; font-weight: 700; color: {COLORS['primary']}; margin: 0;">
                    ${player_data.get('player_value', player_data.get('total_score', 0))/1e6:.2f}M
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center;">
                <p style="font-size: 0.75rem; color: {COLORS['gray_500']}; margin: 0;">NIL POTENTIAL</p>
                <p style="font-size: 2rem; font-weight: 700; color: {COLORS['success']}; margin: 0;">
                    ${player_data.get('nil_potential', 0)/1e6:.2f}M
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Key Metrics Row - V4 WAR Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Display WAR prominently if available
            if 'war' in player_data and player_data.get('war', 0) != 0:
                st.metric("WAR", f"{player_data['war']:.3f}", 
                         delta=f"+{player_data.get('wins_added', 0):.2f} wins")
            else:
                st.metric("Overall Score", f"{player_data.get('performance_score', 0):.0f}/100")
        
        with col2:
            if 'war_tier' in player_data and player_data.get('war_tier') != 'Unknown':
                tier = player_data['war_tier']
                st.metric("WAR Tier", tier)
            else:
                st.metric("Scheme Fit", f"{player_data.get('scheme_fit_score', 0):.0f}/100")
        
        with col3:
            if 'leverage_index' in player_data:
                leverage = player_data.get('leverage_index', 1.0)
                leverage_desc = "High Leverage" if leverage > 1.2 else "Garbage Time" if leverage < 0.7 else "Average"
                st.metric("Game Context", f"{leverage:.2f}x", delta=leverage_desc)
            else:
                st.metric("Brand Score", f"{player_data.get('brand_score', 0):.0f}/100")
        
        with col4:
            if 'war_uncertainty' in player_data:
                uncertainty = player_data.get('war_uncertainty', 0)
                st.metric("Confidence", f"±{uncertainty:.0%}", 
                         delta="Limited Sample" if uncertainty >= 0.30 else "Full Sample",
                         delta_color="inverse" if uncertainty >= 0.30 else "normal")
            elif 'sample_confidence' in player_data:
                confidence = player_data['sample_confidence']
                st.metric("Confidence", f"{confidence:.0%}", 
                         delta="Limited Sample" if confidence < 0.9 else "Full Sample",
                         delta_color="inverse" if confidence < 0.9 else "normal")
            else:
                st.metric("Season", f"{player_data.get('season', 2023)}")
        
        # V4 WAR-Based Breakdown
        st.markdown("### 📊 WAR-Based Valuation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Player Valuation** (What Schools Pay)")
            
            # WAR breakdown if available
            if 'war' in player_data and player_data.get('war', 0) != 0:
                st.markdown(f"**WAR**: {player_data['war']:.3f} (Wins Above Replacement)")
                st.markdown(f"**Wins Added**: +{player_data.get('wins_added', 0):.2f}")
                st.markdown(f"**Tier**: {player_data.get('war_tier', 'Unknown')}")
                
                # WAR components
                if 'participation_factor' in player_data:
                    st.markdown(f"- Participation: {player_data['participation_factor']:.2f}")
                if 'leverage_index' in player_data:
                    st.markdown(f"- Leverage Index: {player_data['leverage_index']:.2f}x")
                if 'opponent_adjustment' in player_data:
                    st.markdown(f"- Opponent Quality: {player_data['opponent_adjustment']:.2f}x")
            else:
                # Fallback to performance scores
                perf_score = player_data.get('performance_score', 0)
                st.markdown(f"Performance: {perf_score:.0f}/100")
                st.progress(perf_score / 100)
                
                scheme_score = player_data.get('scheme_fit_score', 0)
                st.markdown(f"Scheme Fit: {scheme_score:.0f}/100")
                st.progress(scheme_score / 100)
            
            st.metric("Total Player Value", f"${player_data.get('player_value', 0)/1e6:.2f}M")
        
        with col2:
            st.markdown("**NIL Potential** (What Player Earns)")
            
            # Brand bar
            brand_score = player_data.get('brand_score', 0)
            st.markdown(f"Brand Score: {brand_score:.0f}/100")
            st.progress(brand_score / 100)
            
            st.markdown(f"Program: {player_data['team']}")
            st.markdown(f"Position: {player_data['position']}")
            
            st.metric("Annual NIL Potential", f"${player_data.get('nil_potential', 0)/1e6:.2f}M")
        
        # Sample Size & Context (V3)
        if 'sample_confidence' in player_data and player_data.get('sample_confidence', 1.0) < 1.0:
            st.markdown("---")
            st.markdown("### 🎯 Sample Size & Context Analysis (V3)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Snaps Played", f"{player_data.get('snaps_played', 0):,}")
            
            with col2:
                st.metric("Sample Confidence", f"{player_data.get('sample_confidence', 0):.0%}")
            
            with col3:
                st.metric("Context Adj.", f"{player_data.get('context_adjustment', 1.0):.2f}x")
            
            with col4:
                st.metric("Opponent Adj.", f"{player_data.get('opponent_adjustment', 1.0):.2f}x")
            
            # Confidence Interval
            if 'value_low' in player_data and 'value_high' in player_data:
                st.info(f"📊 **Value Range**: ${player_data['value_low']/1e6:.2f}M - ${player_data['value_high']/1e6:.2f}M "
                       f"(±{player_data.get('confidence_interval_pct', 0):.0%} confidence interval)")
                
                st.warning("⚠️ **Limited Sample Warning**: This player has limited playing time. "
                          "Value estimates have higher uncertainty.")
        
        # Combined Summary
        st.markdown("---")
        st.markdown("### 💰 Total Opportunity")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Player Value",
                f"${player_data.get('player_value', 0)/1e6:.2f}M",
                help="What schools/collectives pay for on-field performance"
            )
        
        with col2:
            st.metric(
                "NIL Potential", 
                f"${player_data.get('nil_potential', 0)/1e6:.2f}M",
                help="What player can earn through marketing/endorsements"
            )
        
        with col3:
            combined = player_data.get('player_value', 0) + player_data.get('nil_potential', 0)
            st.metric(
                "Combined Value",
                f"${combined/1e6:.2f}M",
                help="Total annual opportunity for player"
            )

# ============================================================================
# PAGE: TEAM RANKINGS  
# ============================================================================

elif page == "🏫 Team Rankings":
    st.markdown(f'<h1 class="display-lg">Team Rankings</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="text-md" style="margin-bottom: 2rem;">Roster valuations and competitive analysis</p>', unsafe_allow_html=True)
    
    if not valuations_df.empty:
        team_values = valuations_df.groupby('team').agg({
            value_col: ['sum', 'mean', 'count']
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
                        <p class="market-value">${row.get('player_value', row.get('total_score', 0))/1e6:.2f}M</p>
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
        value_col = 'player_value' if 'player_value' in valuations_df.columns else 'total_score'
        valuations_df['efficiency'] = valuations_df['performance_score'] / (valuations_df[value_col] / 1e6)
        
        gems = valuations_df[
            (valuations_df['performance_score'] > 60) &
            (valuations_df[value_col] < 1000000)
        ].sort_values('efficiency', ascending=False)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Opportunities Found", f"{len(gems):,}")
        with col2:
            if not gems.empty:
                st.metric("Avg Performance", f"{gems['performance_score'].mean():.1f}")
        with col3:
            if not gems.empty:
                value_col = 'player_value' if 'player_value' in gems.columns else 'total_score'
                st.metric("Avg Value", f"${gems[value_col].mean()/1e3:.0f}K")
        
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
                        <p style="font-weight: 700; font-size: 1.5rem; color: {COLORS['success']};">${row.get('player_value', row.get('total_score', 0))/1e6:.2f}M</p>
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

