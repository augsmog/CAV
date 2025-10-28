"""
Collect Basketball Player Statistics
Comprehensive data collection for multiple seasons
"""

import sys
from pathlib import Path
import yaml
import argparse
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.cbb_api_client import CollegeBasketballDataAPI
from database import get_session
from database.models_basketball import BasketballTeam, BasketballPlayer, BasketballPerformanceStat

print("="*80)
print("BASKETBALL DATA COLLECTION")
print("="*80)
print()

# Parse arguments
parser = argparse.ArgumentParser(description='Collect basketball player statistics')
parser.add_argument('--season', type=int, nargs='+', default=[2023], 
                    help='Season years to collect (e.g., --season 2023 2022 2021)')
parser.add_argument('--all', action='store_true',
                    help='Collect last 3 seasons (2023, 2022, 2021)')
args = parser.parse_args()

# Determine seasons to collect
if args.all:
    seasons = [2023, 2022, 2021]
else:
    seasons = args.season

print(f"Collecting data for seasons: {', '.join(map(str, seasons))}")
print()

# Load config
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

api_key = config.get('collegebasketballdata', {}).get('api_key', '')

if not api_key:
    print("[ERROR] No basketball API key in config")
    sys.exit(1)

# Create API client
api = CollegeBasketballDataAPI(api_key=api_key)
session = get_session()

# Statistics tracking
total_stats_added = 0
total_stats_updated = 0
total_players_created = 0

# Process each season
for season in seasons:
    print("="*80)
    print(f"COLLECTING {season} SEASON")
    print("="*80)
    print()
    
    # Get all player stats for the season
    print(f"Fetching player stats from API...")
    stats_data = api.get_player_season_stats(season)
    
    if not stats_data:
        print(f"[WARNING] No stats data for {season} season")
        continue
    
    print(f"Retrieved {len(stats_data)} player stat records")
    print()
    
    stats_added = 0
    stats_updated = 0
    stats_failed = 0
    players_created = 0
    
    # Process each player's stats
    for i, stat_record in enumerate(stats_data, 1):
        try:
            # Extract player info
            player_name = stat_record.get('name')
            team_name = stat_record.get('team')
            position = stat_record.get('position', 'Unknown')
            
            if not player_name or not team_name:
                stats_failed += 1
                continue
            
            # Find the team
            team = session.query(BasketballTeam).filter_by(school=team_name).first()
            if not team:
                # Create team if it doesn't exist
                team = BasketballTeam(
                    school=team_name,
                    conference=stat_record.get('conference')
                )
                session.add(team)
                session.flush()
            
            # Find or create player
            player = session.query(BasketballPlayer).filter_by(
                team_id=team.id,
                name=player_name,
                season=season
            ).first()
            
            if not player:
                # Create new player
                player = BasketballPlayer(
                    team_id=team.id,
                    name=player_name,
                    position=position,
                    season=season
                )
                session.add(player)
                session.flush()
                players_created += 1
            
            # Check if stats exist
            existing_stat = session.query(BasketballPerformanceStat).filter_by(
                player_id=player.id,
                season=season
            ).first()
            
            # Prepare stat data - using correct field names from model
            # Extract nested dict values safely
            field_goals = stat_record.get('fieldGoals', {}) or {}
            three_pts = stat_record.get('threePointFieldGoals', {}) or {}
            free_throws = stat_record.get('freeThrows', {}) or {}
            rebounds = stat_record.get('rebounds', {}) or {}
            win_shares = stat_record.get('winShares', {}) or {}
            
            stat_data = {
                'player_id': player.id,
                'season': season,
                'games_played': stat_record.get('games', 0),
                'games_started': stat_record.get('starts', 0),
                'minutes': float(stat_record.get('minutes') or 0.0),
                'pts': float(stat_record.get('points') or 0.0),
                'reb': float(rebounds.get('total', 0.0)) if isinstance(rebounds, dict) else 0.0,
                'oreb': float(rebounds.get('offensive', 0.0)) if isinstance(rebounds, dict) else 0.0,
                'dreb': float(rebounds.get('defensive', 0.0)) if isinstance(rebounds, dict) else 0.0,
                'ast': float(stat_record.get('assists', 0.0)) if stat_record.get('assists') else 0.0,
                'stl': float(stat_record.get('steals', 0.0)) if stat_record.get('steals') else 0.0,
                'blk': float(stat_record.get('blocks', 0.0)) if stat_record.get('blocks') else 0.0,
                'tov': float(stat_record.get('turnovers', 0.0)) if stat_record.get('turnovers') else 0.0,
                'pf': float(stat_record.get('fouls', 0.0)) if stat_record.get('fouls') else 0.0,
                # Shooting stats
                'fgm': float(field_goals.get('made', 0.0)) if isinstance(field_goals, dict) else 0.0,
                'fga': float(field_goals.get('attempted', 0.0)) if isinstance(field_goals, dict) else 0.0,
                'fg_pct': float(field_goals.get('pct', 0.0)) if isinstance(field_goals, dict) else 0.0,
                'tpm': float(three_pts.get('made', 0.0)) if isinstance(three_pts, dict) else 0.0,
                'tpa': float(three_pts.get('attempted', 0.0)) if isinstance(three_pts, dict) else 0.0,
                'tp_pct': float(three_pts.get('pct', 0.0)) if isinstance(three_pts, dict) else 0.0,
                'ftm': float(free_throws.get('made', 0.0)) if isinstance(free_throws, dict) else 0.0,
                'fta': float(free_throws.get('attempted', 0.0)) if isinstance(free_throws, dict) else 0.0,
                'ft_pct': float(free_throws.get('pct', 0.0)) if isinstance(free_throws, dict) else 0.0,
                # Advanced stats
                'per': float(stat_record.get('per', 0.0)) if stat_record.get('per') else None,
                'usage_rate': float(stat_record.get('usage', 0.0)) if stat_record.get('usage') else 0.0,
                'ortg': float(stat_record.get('offensiveRating', 0.0)) if stat_record.get('offensiveRating') else None,
                'drtg': float(stat_record.get('defensiveRating', 0.0)) if stat_record.get('defensiveRating') else None,
                'ws': float(win_shares.get('total', 0.0)) if isinstance(win_shares, dict) else None,
                'bpm': float(stat_record.get('bpm', 0.0)) if stat_record.get('bpm') else None
            }
            
            if existing_stat:
                # Update existing
                for key, value in stat_data.items():
                    if value is not None:
                        setattr(existing_stat, key, value)
                stats_updated += 1
            else:
                # Create new
                stat = BasketballPerformanceStat(**stat_data)
                session.add(stat)
                stats_added += 1
            
            # Commit every 100 records
            if (stats_added + stats_updated) % 100 == 0:
                session.commit()
                print(f"  Progress: {i}/{len(stats_data)} - {stats_added} added, {stats_updated} updated, {players_created} new players...")
        
        except Exception as e:
            print(f"  [WARNING] Failed to process {player_name if 'player_name' in locals() else 'player'}: {e}")
            stats_failed += 1
            session.rollback()
            continue
    
    # Final commit for this season
    session.commit()
    
    print()
    print(f"[SUCCESS] {season} Season Complete:")
    print(f"  Players created: {players_created}")
    print(f"  Stats added: {stats_added}")
    print(f"  Stats updated: {stats_updated}")
    print(f"  Stats failed: {stats_failed}")
    print()
    
    total_stats_added += stats_added
    total_stats_updated += stats_updated
    total_players_created += players_created

# Close session
session.close()

print("="*80)
print("BASKETBALL DATA COLLECTION COMPLETE")
print("="*80)
print()
print(f"TOTAL ACROSS ALL SEASONS:")
print(f"  Seasons collected: {len(seasons)}")
print(f"  Players created: {total_players_created}")
print(f"  Stats added: {total_stats_added}")
print(f"  Stats updated: {total_stats_updated}")
print(f"  Total stats: {total_stats_added + total_stats_updated}")
print()
print("Next steps:")
print("  1. Build basketball performance calculator")
print("  2. Build basketball WAR system")
print("  3. Run valuations")
print("  4. View in dashboard")

