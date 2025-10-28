"""
Collect All Historical Data (2015-2024)
For both Football and Basketball to enable predictive model training
"""

import sys
from pathlib import Path
import yaml
import argparse
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.cfb_api_client import CollegeFootballDataAPI
from scrapers.cbb_api_client import CollegeBasketballDataAPI
from database import get_session
from database.models import Team, Player, PerformanceStat
from database.models_basketball import BasketballTeam, BasketballPlayer, BasketballPerformanceStat
from etl.data_pipeline import DataPipeline
from basketball_data_adapter import adapt_basketball_player_to_valuation_format

print("="*80)
print("HISTORICAL DATA COLLECTION (2015-2024)")
print("="*80)
print()

# Parse arguments
parser = argparse.ArgumentParser(description='Collect all historical data')
parser.add_argument('--sport', choices=['football', 'basketball', 'both'], default='both',
                    help='Which sport to collect')
parser.add_argument('--start-year', type=int, default=2015,
                    help='Starting year (default: 2015)')
parser.add_argument('--end-year', type=int, default=2024,
                    help='Ending year (default: 2024)')
parser.add_argument('--test', action='store_true',
                    help='Test mode: only collect 1 team per season')
args = parser.parse_args()

# Load config
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Determine years to collect
years = list(range(args.start_year, args.end_year + 1))
print(f"Collecting seasons: {years[0]} through {years[-1]}")
print(f"Sport(s): {args.sport}")
print(f"Test mode: {args.test}")
print()

session = get_session()

# ============================================================================
# FOOTBALL COLLECTION
# ============================================================================

if args.sport in ['football', 'both']:
    print("="*80)
    print("FOOTBALL DATA COLLECTION")
    print("="*80)
    print()
    
    fb_api_key = config.get('collegefootballdata', {}).get('api_key', '')
    if not fb_api_key:
        print("[ERROR] No football API key")
    else:
        api = CollegeFootballDataAPI(fb_api_key)
        pipeline = DataPipeline(session, api)
        
        for year in years:
            print(f"\n{'='*60}")
            print(f"FOOTBALL: {year} SEASON")
            print(f"{'='*60}\n")
            
            try:
                # Collect teams
                print(f"[{year}] Collecting teams...")
                teams_count = pipeline.collect_and_save_teams(year)
                print(f"[{year}] ✓ {teams_count} teams")
                
                # Collect rosters (limited if test mode)
                team_limit = 2 if args.test else None
                print(f"[{year}] Collecting rosters{' (TEST: 2 teams)' if args.test else ''}...")
                players_count = pipeline.collect_and_save_rosters(year, team_limit=team_limit)
                print(f"[{year}] ✓ {players_count} players")
                
                # Collect stats
                print(f"[{year}] Collecting player stats...")
                stats_count = pipeline.collect_and_save_player_stats(year)
                print(f"[{year}] ✓ {stats_count} stats")
                
                # Collect transfers (if year >= 2021, when portal opened)
                if year >= 2021:
                    print(f"[{year}] Collecting transfers...")
                    transfers_count = pipeline.collect_and_save_transfers(year)
                    print(f"[{year}] ✓ {transfers_count} transfers")
                
                print(f"[{year}] ✅ Football season complete!")
                
            except Exception as e:
                print(f"[{year}] ❌ Error: {e}")
                continue

# ============================================================================
# BASKETBALL COLLECTION
# ============================================================================

if args.sport in ['basketball', 'both']:
    print("\n" + "="*80)
    print("BASKETBALL DATA COLLECTION")
    print("="*80)
    print()
    
    bb_api_key = config.get('collegebasketballdata', {}).get('api_key', '')
    if not bb_api_key:
        print("[ERROR] No basketball API key")
    else:
        bb_api = CollegeBasketballDataAPI(bb_api_key)
        
        for year in years:
            print(f"\n{'='*60}")
            print(f"BASKETBALL: {year} SEASON")
            print(f"{'='*60}\n")
            
            try:
                # Collect teams
                print(f"[{year}] Collecting teams...")
                teams_data = bb_api.get_teams(year=year)
                
                teams_added = 0
                for team_data in teams_data:
                    team_id = team_data.get('id')
                    if not team_id:
                        continue
                    
                    existing = session.query(BasketballTeam).filter_by(source_id=team_id).first()
                    if not existing:
                        new_team = BasketballTeam(
                            source_id=team_id,
                            school=team_data.get('school'),
                            mascot=team_data.get('mascot'),
                            conference=team_data.get('conference'),
                        )
                        session.add(new_team)
                        teams_added += 1
                
                session.commit()
                print(f"[{year}] ✓ {teams_added} new teams")
                
                # Collect stats
                print(f"[{year}] Collecting player stats...")
                stats_data = bb_api.get_player_season_stats(year)
                
                stats_added = 0
                players_added = 0
                
                for stat_record in stats_data:
                    player_name = stat_record.get('name')
                    team_name = stat_record.get('team')
                    
                    if not player_name or not team_name:
                        continue
                    
                    # Find team
                    team = session.query(BasketballTeam).filter_by(school=team_name).first()
                    if not team:
                        continue
                    
                    # Find or create player
                    player = session.query(BasketballPlayer).filter_by(
                        team_id=team.id,
                        name=player_name,
                        season=year
                    ).first()
                    
                    if not player:
                        player = BasketballPlayer(
                            team_id=team.id,
                            name=player_name,
                            position=stat_record.get('position', 'G'),
                            season=year
                        )
                        session.add(player)
                        session.flush()
                        players_added += 1
                    
                    # Add stats
                    existing_stat = session.query(BasketballPerformanceStat).filter_by(
                        player_id=player.id,
                        season=year
                    ).first()
                    
                    if not existing_stat:
                        field_goals = stat_record.get('fieldGoals', {}) or {}
                        three_pts = stat_record.get('threePointFieldGoals', {}) or {}
                        free_throws = stat_record.get('freeThrows', {}) or {}
                        rebounds = stat_record.get('rebounds', {}) or {}
                        win_shares = stat_record.get('winShares', {}) or {}
                        
                        new_stat = BasketballPerformanceStat(
                            player_id=player.id,
                            season=year,
                            games_played=stat_record.get('games', 0),
                            games_started=stat_record.get('starts', 0),
                            minutes=float(stat_record.get('minutes') or 0.0),
                            pts=float(stat_record.get('points') or 0.0),
                            reb=float(rebounds.get('total', 0.0)) if isinstance(rebounds, dict) else 0.0,
                            ast=float(stat_record.get('assists', 0.0)) if stat_record.get('assists') else 0.0,
                            stl=float(stat_record.get('steals', 0.0)) if stat_record.get('steals') else 0.0,
                            blk=float(stat_record.get('blocks', 0.0)) if stat_record.get('blocks') else 0.0,
                            tov=float(stat_record.get('turnovers', 0.0)) if stat_record.get('turnovers') else 0.0,
                            pf=float(stat_record.get('fouls', 0.0)) if stat_record.get('fouls') else 0.0,
                            fgm=float(field_goals.get('made', 0.0)) if isinstance(field_goals, dict) else 0.0,
                            fga=float(field_goals.get('attempted', 0.0)) if isinstance(field_goals, dict) else 0.0,
                            fg_pct=float(field_goals.get('pct', 0.0)) if isinstance(field_goals, dict) else 0.0,
                            tpm=float(three_pts.get('made', 0.0)) if isinstance(three_pts, dict) else 0.0,
                            tpa=float(three_pts.get('attempted', 0.0)) if isinstance(three_pts, dict) else 0.0,
                            tp_pct=float(three_pts.get('pct', 0.0)) if isinstance(three_pts, dict) else 0.0,
                            ftm=float(free_throws.get('made', 0.0)) if isinstance(free_throws, dict) else 0.0,
                            fta=float(free_throws.get('attempted', 0.0)) if isinstance(free_throws, dict) else 0.0,
                            ft_pct=float(free_throws.get('pct', 0.0)) if isinstance(free_throws, dict) else 0.0,
                            per=float(stat_record.get('per', 0.0)) if stat_record.get('per') else None,
                            usage_rate=float(stat_record.get('usage', 0.0)) if stat_record.get('usage') else 0.0,
                            ortg=float(stat_record.get('offensiveRating', 0.0)) if stat_record.get('offensiveRating') else None,
                            drtg=float(stat_record.get('defensiveRating', 0.0)) if stat_record.get('defensiveRating') else None,
                            ws=float(win_shares.get('total', 0.0)) if isinstance(win_shares, dict) else None,
                        )
                        session.add(new_stat)
                        stats_added += 1
                    
                    # Commit every 100
                    if (stats_added + players_added) % 100 == 0:
                        session.commit()
                
                session.commit()
                print(f"[{year}] ✓ {players_added} players, {stats_added} stats")
                print(f"[{year}] ✅ Basketball season complete!")
                
            except Exception as e:
                print(f"[{year}] ❌ Error: {e}")
                session.rollback()
                continue

session.close()

print("\n" + "="*80)
print("HISTORICAL DATA COLLECTION COMPLETE!")
print("="*80)
print()
print("Next steps:")
print("  1. Build predictive model using multi-year data")
print("  2. Validate predictions against actual next-season performance")
print("  3. Iterate and refine weights/algorithms")
print("  4. Display confidence intervals based on historical accuracy")
