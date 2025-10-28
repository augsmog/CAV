"""
Collect Basketball Rosters
Collect player rosters for all basketball teams
"""

import sys
from pathlib import Path
import yaml
import argparse

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.cbb_api_client import CollegeBasketballDataAPI
from etl.basketball_pipeline import BasketballDataPipeline

print("="*80)
print("BASKETBALL ROSTER COLLECTION")
print("="*80)
print()

# Parse arguments
parser = argparse.ArgumentParser(description='Collect basketball rosters')
parser.add_argument('--year', type=int, default=2024, help='Season year (default: 2024)')
parser.add_argument('--limit', type=int, help='Limit number of teams (for testing)')
args = parser.parse_args()

# Load config
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

api_key = config.get('collegebasketballdata', {}).get('api_key', '')

if not api_key:
    print("[ERROR] No basketball API key in config")
    sys.exit(1)

# Create API client and pipeline
print(f"Collecting rosters for {args.year} season...")
if args.limit:
    print(f"  (Limited to {args.limit} teams for testing)")
print()

api_client = CollegeBasketballDataAPI(api_key=api_key)
pipeline = BasketballDataPipeline(api_client)

try:
    # Collect rosters
    teams_processed, players_added, players_updated = pipeline.collect_rosters(
        year=args.year,
        limit=args.limit
    )
    
    print("\n" + "="*80)
    print("[SUCCESS] ROSTER COLLECTION COMPLETE")
    print("="*80)
    print(f"\nTeams processed: {teams_processed}")
    print(f"Players added: {players_added}")
    print(f"Players updated: {players_updated}")
    print(f"Total players: {players_added + players_updated}")
    
finally:
    pipeline.close()

