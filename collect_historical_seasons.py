"""
Collect Historical Seasons for Predictive Model Training
Football: 2020-2024 (5 seasons)
Basketball: 2020-2024 (5 seasons)
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_config
from database import init_database, get_engine
from etl.data_pipeline import collect_season_data

print("="*80)
print("HISTORICAL DATA COLLECTION FOR PREDICTIVE MODELING")
print("="*80)
print()

parser = argparse.ArgumentParser()
parser.add_argument('--sport', choices=['football', 'basketball', 'both'], default='football')
parser.add_argument('--start', type=int, default=2020)
parser.add_argument('--end', type=int, default=2024)
args = parser.parse_args()

config = get_config()
init_database()

seasons = list(range(args.start, args.end + 1))
print(f"Collecting {args.sport} seasons: {seasons}")
print()

if args.sport in ['football', 'both']:
    print("FOOTBALL DATA COLLECTION")
    print("-" * 60)
    
    for year in seasons:
        print(f"\n[FOOTBALL {year}]")
        try:
            result = collect_season_data(year)
            print(f"✓ {year}: {result['teams']} teams, {result['players']} players, {result['stats']} stats")
        except Exception as e:
            print(f"✗ {year}: Error - {e}")
    
    print("\n" + "="*60)
    print("FOOTBALL COLLECTION COMPLETE")
    print("="*60)

if args.sport in ['basketball', 'both']:
    print("\n\nBASKETBALL DATA COLLECTION")
    print("-" * 60)
    
    # Use the existing basketball collection script
    import subprocess
    for year in seasons:
        print(f"\n[BASKETBALL {year}]")
        try:
            result = subprocess.run(
                ['python', 'collect_basketball_stats.py', '--season', str(year)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Parse output for success message
                if 'Season Complete' in result.stdout:
                    print(f"✓ {year}: Collection successful")
                else:
                    print(f"✓ {year}: Completed (check logs for details)")
            else:
                print(f"✗ {year}: Error")
        except Exception as e:
            print(f"✗ {year}: Error - {e}")
    
    print("\n" + "="*60)
    print("BASKETBALL COLLECTION COMPLETE")
    print("="*60)

print("\n\n" + "="*80)
print("HISTORICAL DATA COLLECTION COMPLETE!")
print("="*80)
print("\nData ready for:")
print("  • Predictive model training")
print("  • Validation against actual outcomes")
print("  • Confidence interval calculation")
print("  • Algorithm refinement")

