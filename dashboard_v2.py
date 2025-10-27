"""
College Football Transfer Market - Transfermarkt-style Dashboard
Market values, roster analysis, and transfer portal intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Player, Team, PerformanceStat, Transfer

# Page config
st.set_page_config(
    page_title="CFB Transfer Market",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Transfermarkt style
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        margin-bottom: 1rem;
    }
    .market-value {
        font-size: 2rem;
        font-weight: bold;
        color: #059669;
    }
    .team-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem 0;
    }
    .player-card {
        background: #f8fafc;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .portal-player {
        background: #fef3c7;
        padding: 1rem;
        border-left: 4px solid #f59e0b;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .value-up {
        color: #059669;
        font-weight: bold;
    }
    .value-down {
        color: #dc2626;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
@st.cache_resource
def get_db_session():
    return get_session()

session = get_db_session()

# Load data with caching
@st.cache_data(ttl=300)
def load_team_values():
    """Calculate total roster value for each team"""
    # Load valuations
    try:
        with open('outputs/valuations/all_valuations_2023.json', 'r') as f:
            data = json.load(f)
            valuations_df = pd.DataFrame(data['valuations'])
    except:
        return pd.DataFrame()
    
    # Group by team and calculate total value
    team_values = valuations_df.groupby('team').agg({
        'total_score': ['sum', 'mean', 'count']
    }).reset_index()
    
    team_values.columns = ['team', 'total_value', 'avg_player_value', 'player_count']
    team_values = team_values.sort_values('total_value', ascending=False)
    
    return team_values

@st.cache_data(ttl=300)
def load_portal_players():
    """Get players currently in transfer portal (2023)"""
    transfers = session.query(Transfer, Player).join(
        Player, Transfer.player_id == Player.id
    ).filter(
        Transfer.season == 2023,
        Transfer.to_team.is_(None)  # No destination = still available
    ).all()
    
    data = []
    for transfer, player in transfers:
        data.append({
            'player_id': player.id,
            'name': player.name,
            'position': player.position,
            'from_team': transfer.from_team,
            'class_year': player.class_year
        })
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def load_valuations():
    try:
        with open('outputs/valuations/all_valuations_2023.json', 'r') as f:
            data = json.load(f)
            return pd.DataFrame(data['valuations'])
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_position_needs(team_name):
    """Analyze team's position depth and needs"""
    players = session.query(Player).filter_by(current_team_id=None).all()  # Simplified
    # Get team players and analyze depth charts
    # This is a simplified version - expand based on actual roster
    return {
        'QB': 3,
        'RB': 2,
        'WR': 4,
        'TE': 2,
        'OL': 5,
        'DL': 4,
        'LB': 3,
        'DB': 4
    }

# Sidebar
st.sidebar.title("💰 Transfer Market Hub")
page = st.sidebar.radio(
    "Navigate",
    ["Market Overview", "Team Valuations", "Transfer Portal", "Target Players", "Undervalued Gems"]
)

# ============================================================================
# PAGE: MARKET OVERVIEW
# ============================================================================
if page == "Market Overview":
    st.markdown('<p class="main-header">📊 College Football Transfer Market</p>', unsafe_allow_html=True)
    st.markdown("*Market Intelligence for Athletic Directors and Coaches*")
    
    # Load data
    team_values = load_team_values()
    valuations_df = load_valuations()
    portal_df = load_portal_players()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_market_value = team_values['total_value'].sum() if not team_values.empty else 0
        st.metric(
            "Total Market Value",
            f"${total_market_value/1e9:.2f}B",
            "All FBS Programs"
        )
    
    with col2:
        avg_team_value = team_values['total_value'].mean() if not team_values.empty else 0
        st.metric(
            "Avg Team Value",
            f"${avg_team_value/1e6:.1f}M",
            "Per Program"
        )
    
    with col3:
        portal_count = len(portal_df)
        st.metric(
            "Available in Portal",
            f"{portal_count:,}",
            "Uncommitted Players"
        )
    
    with col4:
        if not valuations_df.empty:
            avg_player = valuations_df['total_score'].mean()
            st.metric(
                "Avg Player Value",
                f"${avg_player/1e3:.0f}K",
                "2023 Season"
            )
    
    st.markdown("---")
    
    # Market Leaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💎 Most Valuable Teams")
        if not team_values.empty:
            top_10_teams = team_values.head(10).copy()
            top_10_teams['total_value_m'] = (top_10_teams['total_value'] / 1e6).round(1)
            
            fig = px.bar(
                top_10_teams,
                x='total_value_m',
                y='team',
                orientation='h',
                title="Top 10 Teams by Roster Value",
                labels={'total_value_m': 'Total Roster Value ($M)', 'team': ''},
                color='total_value_m',
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Most Valuable Players")
        if not valuations_df.empty:
            top_players = valuations_df.nlargest(10, 'total_score')[
                ['player', 'position', 'team', 'total_score']
            ].copy()
            top_players['value_m'] = (top_players['total_score'] / 1e6).round(2)
            
            for idx, row in top_players.iterrows():
                st.markdown(f"""
                <div class="player-card">
                    <strong>{row['player']}</strong> ({row['position']}) - {row['team']}<br>
                    <span class="market-value">${row['value_m']}M</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Portal Activity
    st.markdown("---")
    st.subheader("🔄 Transfer Portal Activity")
    
    if not portal_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Position breakdown of available players
            position_counts = portal_df['position'].value_counts().head(8)
            fig = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                title="Available Players by Position"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Quick Stats**")
            st.metric("Total Available", len(portal_df))
            if 'position' in portal_df.columns:
                st.metric("Top Position", portal_df['position'].mode()[0] if not portal_df['position'].mode().empty else "N/A")
            if 'from_team' in portal_df.columns:
                st.metric("Teams Affected", portal_df['from_team'].nunique())

# ============================================================================
# PAGE: TEAM VALUATIONS
# ============================================================================
elif page == "Team Valuations":
    st.markdown('<p class="main-header">🏫 Team Roster Valuations</p>', unsafe_allow_html=True)
    
    team_values = load_team_values()
    valuations_df = load_valuations()
    
    if team_values.empty:
        st.error("No valuation data available. Run valuations first.")
    else:
        # Filters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_team = st.text_input("🔍 Search Team", placeholder="Enter team name...")
        
        with col2:
            sort_by = st.selectbox("Sort by", ["Total Value", "Average Player Value", "Player Count"])
        
        # Apply filters
        filtered_teams = team_values.copy()
        if search_team:
            filtered_teams = filtered_teams[
                filtered_teams['team'].str.contains(search_team, case=False, na=False)
            ]
        
        # Sort
        if sort_by == "Total Value":
            filtered_teams = filtered_teams.sort_values('total_value', ascending=False)
        elif sort_by == "Average Player Value":
            filtered_teams = filtered_teams.sort_values('avg_player_value', ascending=False)
        else:
            filtered_teams = filtered_teams.sort_values('player_count', ascending=False)
        
        # Display team cards
        st.markdown("### 📊 Team Rankings")
        
        for idx, row in filtered_teams.head(20).iterrows():
            rank = idx + 1
            total_val = row['total_value'] / 1e6
            avg_val = row['avg_player_value'] / 1e3
            
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                st.markdown(f"### #{rank}")
            
            with col2:
                st.markdown(f"**{row['team']}**")
                st.caption(f"{int(row['player_count'])} valued players")
            
            with col3:
                st.metric("Total Value", f"${total_val:.1f}M")
            
            with col4:
                st.metric("Avg Player", f"${avg_val:.0f}K")
        
        # Detailed team analysis
        st.markdown("---")
        st.subheader("🔍 Detailed Team Analysis")
        
        selected_team = st.selectbox(
            "Select team for detailed breakdown",
            team_values['team'].tolist()
        )
        
        if selected_team:
            team_players = valuations_df[valuations_df['team'] == selected_team]
            
            if not team_players.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total = team_players['total_score'].sum() / 1e6
                    st.metric("Total Roster Value", f"${total:.2f}M")
                
                with col2:
                    avg = team_players['total_score'].mean() / 1e3
                    st.metric("Avg Player Value", f"${avg:.0f}K")
                
                with col3:
                    st.metric("Valued Players", len(team_players))
                
                # Position breakdown
                st.markdown("**Value by Position**")
                position_values = team_players.groupby('position')['total_score'].sum().sort_values(ascending=False)
                
                fig = px.bar(
                    x=position_values.values / 1e6,
                    y=position_values.index,
                    orientation='h',
                    labels={'x': 'Total Value ($M)', 'y': 'Position'},
                    title=f"{selected_team} - Position Value Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top players on team
                st.markdown("**Most Valuable Players**")
                top_team_players = team_players.nlargest(10, 'total_score')[
                    ['player', 'position', 'total_score', 'performance_score']
                ]
                top_team_players['Value ($M)'] = (top_team_players['total_score'] / 1e6).round(2)
                top_team_players['Performance'] = top_team_players['performance_score'].round(1)
                
                display_df = top_team_players[['player', 'position', 'Value ($M)', 'Performance']]
                display_df.columns = ['Player', 'Position', 'Market Value ($M)', 'Performance Score']
                st.dataframe(display_df, hide_index=True, use_container_width=True)

# ============================================================================
# PAGE: TRANSFER PORTAL
# ============================================================================
elif page == "Transfer Portal":
    st.markdown('<p class="main-header">🔄 Transfer Portal Market</p>', unsafe_allow_html=True)
    st.markdown("*Available Players & Market Intelligence*")
    
    portal_df = load_portal_players()
    valuations_df = load_valuations()
    
    if portal_df.empty:
        st.warning("No portal data available or all players have committed.")
    else:
        # Merge with valuations
        portal_with_values = portal_df.merge(
            valuations_df[['player', 'total_score', 'performance_score', 'position']],
            left_on='name',
            right_on='player',
            how='left'
        )
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            positions = ['All'] + sorted(portal_with_values['position_x'].dropna().unique().tolist())
            filter_position = st.selectbox("Position", positions)
        
        with col2:
            min_value = st.number_input("Min Value ($)", value=0, step=100000)
        
        with col3:
            sort_by = st.selectbox("Sort", ["Value (High-Low)", "Value (Low-High)", "Name"])
        
        # Apply filters
        filtered_portal = portal_with_values.copy()
        if filter_position != 'All':
            filtered_portal = filtered_portal[filtered_portal['position_x'] == filter_position]
        if min_value > 0:
            filtered_portal = filtered_portal[filtered_portal['total_score'] >= min_value]
        
        # Sort
        if sort_by == "Value (High-Low)":
            filtered_portal = filtered_portal.sort_values('total_score', ascending=False)
        elif sort_by == "Value (Low-High)":
            filtered_portal = filtered_portal.sort_values('total_score', ascending=True)
        else:
            filtered_portal = filtered_portal.sort_values('name')
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Available Players", len(filtered_portal))
        with col2:
            if not filtered_portal['total_score'].isna().all():
                avg_val = filtered_portal['total_score'].mean() / 1e3
                st.metric("Avg Value", f"${avg_val:.0f}K")
        with col3:
            if not filtered_portal['total_score'].isna().all():
                total_val = filtered_portal['total_score'].sum() / 1e6
                st.metric("Total Market", f"${total_val:.1f}M")
        
        st.markdown("---")
        st.subheader("📋 Available Players")
        
        # Display portal players
        for idx, row in filtered_portal.head(20).iterrows():
            value = row['total_score'] / 1e6 if pd.notna(row['total_score']) else 0
            perf = row['performance_score'] if pd.notna(row['performance_score']) else 0
            
            st.markdown(f"""
            <div class="portal-player">
                <strong>{row['name']}</strong> - {row['position_x']} - From: {row['from_team']}<br>
                <span style="font-size: 1.2rem; color: #f59e0b;">💰 ${value:.2f}M</span> | 
                Performance: {perf:.1f} | 
                Class: {row['class_year'] if pd.notna(row['class_year']) else 'N/A'}
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PAGE: TARGET PLAYERS
# ============================================================================
elif page == "Target Players":
    st.markdown('<p class="main-header">🎯 Recommended Targets</p>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Transfer Recommendations*")
    
    # Team selector
    team_values = load_team_values()
    if not team_values.empty:
        your_team = st.selectbox("Select Your Team", team_values['team'].tolist())
        
        valuations_df = load_valuations()
        portal_df = load_portal_players()
        
        if not valuations_df.empty and not portal_df.empty:
            # Get team's current roster
            team_roster = valuations_df[valuations_df['team'] == your_team]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### Your Team Stats")
                if not team_roster.empty:
                    st.metric("Current Roster Value", f"${team_roster['total_score'].sum()/1e6:.1f}M")
                    st.metric("Players Valued", len(team_roster))
                    st.metric("Avg Player Value", f"${team_roster['total_score'].mean()/1e3:.0f}K")
            
            with col2:
                st.markdown("### Position Needs Analysis")
                if not team_roster.empty:
                    position_counts = team_roster['position'].value_counts()
                    
                    needs = []
                    ideal_counts = {'QB': 3, 'RB': 4, 'WR': 6, 'TE': 3, 'OL': 8, 'DL': 6, 'LB': 5, 'DB': 6}
                    
                    for pos, ideal in ideal_counts.items():
                        current = position_counts.get(pos, 0)
                        if current < ideal:
                            needs.append({'Position': pos, 'Need': ideal - current, 'Current': current, 'Ideal': ideal})
                    
                    if needs:
                        needs_df = pd.DataFrame(needs)
                        st.dataframe(needs_df, hide_index=True, use_container_width=True)
            
            # Recommended targets
            st.markdown("---")
            st.subheader("🎯 Top Transfer Targets")
            
            # Merge portal with valuations
            targets = portal_df.merge(
                valuations_df[['player', 'total_score', 'performance_score', 'scheme_fit_score', 'position']],
                left_on='name',
                right_on='player',
                how='inner'
            )
            
            # Focus on positions of need
            if not team_roster.empty:
                position_counts = team_roster['position'].value_counts()
                weak_positions = [pos for pos in ['QB', 'RB', 'WR', 'TE'] if position_counts.get(pos, 0) < 3]
                
                if weak_positions:
                    st.markdown(f"**Recommended for positions: {', '.join(weak_positions)}**")
                    priority_targets = targets[targets['position_x'].isin(weak_positions)]
                else:
                    priority_targets = targets
                
                # Sort by value and scheme fit
                priority_targets['combined_score'] = (
                    priority_targets['total_score'] * 0.6 + 
                    priority_targets['scheme_fit_score'] * 1000000 * 0.4
                )
                priority_targets = priority_targets.sort_values('combined_score', ascending=False)
                
                # Display top targets
                for idx, row in priority_targets.head(15).iterrows():
                    value = row['total_score'] / 1e6
                    fit_score = row['scheme_fit_score'] if pd.notna(row['scheme_fit_score']) else 0
                    
                    fit_color = "#059669" if fit_score > 75 else "#f59e0b" if fit_score > 60 else "#dc2626"
                    
                    st.markdown(f"""
                    <div class="player-card">
                        <strong style="font-size: 1.1rem;">{row['name']}</strong> - {row['position_x']}<br>
                        From: {row['from_team']} | Class: {row['class_year'] if pd.notna(row['class_year']) else 'N/A'}<br>
                        <span style="font-size: 1.3rem; color: #059669;">💰 ${value:.2f}M</span> | 
                        <span style="color: {fit_color};">Scheme Fit: {fit_score:.0f}/100</span><br>
                        <small>Performance: {row['performance_score']:.1f}</small>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: UNDERVALUED GEMS
# ============================================================================
elif page == "Undervalued Gems":
    st.markdown('<p class="main-header">💎 Undervalued Gems</p>', unsafe_allow_html=True)
    st.markdown("*High Performance, Low Market Value - Find the Bargains*")
    
    valuations_df = load_valuations()
    portal_df = load_portal_players()
    
    if not valuations_df.empty:
        # Calculate value efficiency (performance / value)
        valuations_df['value_efficiency'] = valuations_df['performance_score'] / (valuations_df['total_score'] / 1e6)
        
        # Filter for reasonable performers
        gems = valuations_df[
            (valuations_df['performance_score'] > 60) &  # Decent performance
            (valuations_df['total_score'] < 1000000)  # Under $1M
        ].copy()
        
        gems = gems.sort_values('value_efficiency', ascending=False)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            positions = ['All'] + sorted(gems['position'].unique().tolist())
            filter_pos = st.selectbox("Position", positions)
        
        with col2:
            max_value = st.slider("Max Value ($M)", 0.1, 2.0, 1.0, 0.1)
        
        # Apply filters
        if filter_pos != 'All':
            gems = gems[gems['position'] == filter_pos]
        gems = gems[gems['total_score'] <= (max_value * 1e6)]
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gems Found", len(gems))
        with col2:
            if not gems.empty:
                st.metric("Avg Value", f"${gems['total_score'].mean()/1e3:.0f}K")
        with col3:
            if not gems.empty:
                st.metric("Avg Performance", f"{gems['performance_score'].mean():.1f}")
        
        st.markdown("---")
        st.subheader("💎 Top Value Plays")
        
        # Display gems
        for idx, row in gems.head(20).iterrows():
            value = row['total_score'] / 1e6
            perf = row['performance_score']
            efficiency = row['value_efficiency']
            
            # Check if in portal
            in_portal = row['player'] in portal_df['name'].values if not portal_df.empty else False
            portal_badge = "🔄 IN PORTAL" if in_portal else ""
            
            st.markdown(f"""
            <div class="player-card">
                <strong style="font-size: 1.1rem;">{row['player']}</strong> - {row['position']} - {row['team']} {portal_badge}<br>
                <span style="font-size: 1.2rem; color: #059669;">💰 ${value:.2f}M</span> | 
                <span style="color: #3b82f6;">Performance: {perf:.1f}</span> | 
                <span style="color: #8b5cf6;">Value Score: {efficiency:.1f}</span><br>
                <small>Scheme Fit: {row.get('scheme_fit_score', 0):.0f} | Brand: {row.get('brand_score', 0):.0f}</small>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #64748b;'>
    <p><strong>College Football Transfer Market Intelligence</strong></p>
    <p>Market valuations updated in real-time | Data from 2022-2023 seasons</p>
    <p style='font-size: 0.9rem;'>💡 Like Transfermarkt for College Sports</p>
</div>
""", unsafe_allow_html=True)

