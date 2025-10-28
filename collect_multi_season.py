"""
Collect Multiple Seasons of Data
Efficiently collects historical data for model training and validation
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_config
from database import init_database
from etl.data_pipeline import collect_season_data
import argparse

print("="*80)
print("MULTI-SEASON DATA COLLECTION")
print("="*80)
print()

parser = argparse.ArgumentParser()
parser.add_argument('--sport', choices=['football', 'basketball'], default='football', help='Sport to collect')
parser.add_argument('--start', type=int, default=2020, help='Start year')
parser.add_argument('--end', type=int, default=2024, help='End year (inclusive)')
parser.add_argument('--quick', action='store_true', help='Quick mode: stats only')
args = parser.parse_args()

config = get_config()
init_database()

seasons = list(range(args.start, args.end + 1))
print(f"Collecting {args.sport} data for seasons: {seasons}")
print(f"Mode: {'Quick (stats only)' if args.quick else 'Full (teams, rosters, stats)'}")
print()

if args.sport == 'football':
    for year in seasons:
        print(f"\n{'='*60}")
        print(f"FOOTBALL: {year} SEASON")
        print(f"{'='*60}\n")
        
        try:
            if args.quick:
                # Just collect stats for existing players
                from etl.data_pipeline import DataPipeline
                from database import get_session
                from scrapers.cfb_api_client import CollegeFootballDataAPI
                
                session = get_session()
                api = CollegeFootballDataAPI(config.collegefootballdata['api_key'])
                pipeline = DataPipeline()
                
                stats_count = pipeline.collect_and_save_player_stats(year)
                print(f"✓ {year}: Collected {stats_count} player stats")
            else:
                result = collect_season_data(year)
                print(f"✓ {year}: {result['teams']} teams, {result['players']} players, {result['stats']} stats")
        
        except Exception as e:
            print(f"✗ {year}: Error - {e}")
            continue

elif args.sport == 'basketball':
    print("Basketball multi-season collection...")
    print("Using existing collect_basketball_stats.py for each season")
    
    import subprocess
    for year in seasons:
        print(f"\n[BASKETBALL {year}]")
        try:
            result = subprocess.run(
                ['python', 'collect_basketball_stats.py', '--season', str(year)],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                print(f"✓ {year}: Collection complete")
            else:
                print(f"✗ {year}: Error (see logs)")
        except subprocess.TimeoutExpired:
            print(f"✗ {year}: Timeout")
        except Exception as e:
            print(f"✗ {year}: {e}")

print("\n" + "="*80)
print("MULTI-SEASON COLLECTION COMPLETE")
print("="*80)
print("\nReady for:")
print("  • Predictive model training")
print("  • Historical validation")
print("  • Confidence interval calculation")

